#!/usr/bin/env python3
"""Merge a contacts export into config/network/roster.csv.

Understands a Dex export (its own column names, plus the APEX custom fields
Dex carries) and a plain Google Contacts CSV.

Matching is exact on a normalised name, then on the LinkedIn slug. Nothing is
merged on a fuzzy name: in the real export "Eyal Kraft" is one edit away from
"Eyal Katz", who runs a different company — and a wrong phone number means
calling the wrong person. Near matches are printed for a human to judge.

The verified master sheet wins over Dex for role and company, EXCEPT where the
roster has no verified role at all — those 16 rows are the Alumni Roll-Up
backlog, and anything Dex knows about them is progress.

    python3 scripts/merge_contacts.py dex_contacts.csv           # report only
    python3 scripts/merge_contacts.py dex_contacts.csv --apply   # write it
"""

import argparse
import csv
import difflib
import re
import sys
import unicodedata
from pathlib import Path

csv.field_size_limit(10 ** 7)

ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "config" / "network" / "roster.csv"
LOG = ROOT / "logs" / "roster-log.md"

UNVERIFIED = re.compile(r"^\s*(unknown|identity check|\(roster: none\))", re.I)

# Column names are matched with punctuation stripped, so "E-mail 1 - Value",
# "dex_email" and "Email" all reduce to comparable keys.
NAME_F = ["fullname", "name", "displayname", "שם"]
EMAIL_F = ["dexemail", "dexemails", "email", "emailaddress", "primaryemail", "מייל"]
PHONE_F = ["dexphone", "dexphones", "phone", "mobile", "phonenumber", "cell", "נייד"]
LINKEDIN_F = ["linkedin", "linkedinurl", "linkedinprofile"]

# Dex's APEX-specific columns. Kept as context in notes, never used to
# overwrite the roster's own cohort/track — mismatches are reported instead.
DEX_EXTRA = {
    "מחזור קורס": "military course",   # NOT the APEX cohort — Talpiot/ARAM
                                        # course number, e.g. ט׳, 36
    "Military Track ": "unit",
    "Domains": "domains",
    "Role": "role tag",
    "Commitment level ": "commitment",
    "Status": "status",
    "Met with": "met with",
    "Who warm intro": "warm intro via",
    "education": "education",
    "dex_tags": "tags",
}


def fold(key: str) -> str:
    return re.sub(r"[^a-z0-9֐-׿]", "", (key or "").lower())


def norm(name: str) -> str:
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^\w\s]", " ", name, flags=re.UNICODE)
    return " ".join(name.lower().split())


def slug(url: str) -> str | None:
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", (url or "").lower())
    return m.group(1).rstrip("/") if m else None


def _one_phone(raw: str) -> str:
    digits = re.sub(r"[^\d+]", "", (raw or "").strip().lstrip("'\""))
    if digits.startswith("0") and len(digits) >= 9:
        return "+972" + digits[1:]
    return digits


def plausible(phone: str) -> bool:
    """An Israeli number is +972 then 9 digits. Dex sometimes stores a
    truncated primary alongside a correct alternate, and a number one digit
    short dials a stranger — so length is checked, not assumed."""
    d = re.sub(r"\D", "", phone)
    return len(d) == 12 if d.startswith("972") else len(d) >= 10


def clean_phone(raw: str) -> str:
    """Dex writes numbers with a leading apostrophe to stop Excel mangling
    them, and dex_phones holds several separated by commas or pipes. Take the
    first plausible one rather than the first one."""
    candidates = [_one_phone(p) for p in re.split(r"[|,;]", raw or "") if p.strip()]
    candidates = [c for c in candidates if c]
    for c in candidates:
        if plausible(c):
            return c
    return candidates[0] if candidates else ""


def pick(row: dict, candidates: list[str]) -> str:
    folded = {fold(k): (v or "").strip() for k, v in row.items() if k}
    for field in candidates:
        if folded.get(field):
            return folded[field]
    for key in sorted(folded):                          # "Phone 2 - Value" etc
        if folded[key] and any(key.startswith(f) for f in candidates):
            return folded[key]
    return ""


def load_contacts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for row in rows:
        name = pick(row, NAME_F)
        if not name:
            first = pick(row, ["firstname", "givenname"])
            last = pick(row, ["lastname", "familyname", "surname"])
            name = f"{first} {last}".strip()
        if not name:
            continue
        row["_name"] = name
        row["_email"] = pick(row, EMAIL_F)
        row["_phone"] = clean_phone(
            " , ".join(v for v in (row.get("dex_phone"),
                                   row.get("dex_phones")) if v)
            or pick(row, PHONE_F))
        row["_slug"] = slug(pick(row, LINKEDIN_F))
        out.append(row)
    return out


def dex_notes(c: dict) -> str:
    """Whatever Dex knows that the roster has no column for."""
    bits = []
    for field, label in DEX_EXTRA.items():
        val = (c.get(field) or "").strip()
        if val and val.lower() not in ("none", "-"):
            bits.append(f"{label}: {val}")
    return " · ".join(bits)


def merge(path: Path, apply: bool) -> None:
    with ROSTER.open(encoding="utf-8") as fh:
        roster = list(csv.DictReader(fh))
        columns = list(roster[0].keys())

    contacts = load_contacts(path)
    by_name, by_slug = {}, {}
    for c in contacts:
        by_name.setdefault(norm(c["_name"]), c)
        if c["_slug"]:
            by_slug.setdefault(c["_slug"], c)

    filled, unmatched, near, changes = [], [], [], []
    roles_recovered, mismatches = [], []

    for person in roster:
        c = by_name.get(norm(person["name"]))
        how = "name"
        if not c:
            s = slug(person["linkedin"])
            if s and s in by_slug:
                c, how = by_slug[s], "linkedin"
        if not c and person.get("name_he"):
            c, how = by_name.get(norm(person["name_he"])), "name_he"

        if not c:
            close = difflib.get_close_matches(norm(person["name"]), by_name,
                                              n=1, cutoff=0.80)
            if close:
                near.append((person["name"], by_name[close[0]]["_name"],
                             by_name[close[0]].get("job_title", ""),
                             by_name[close[0]].get("company", "")))
            unmatched.append(person["name"])
            continue

        added = []
        for field, value in (("phone", c["_phone"]), ("email", c["_email"]),
                             ("location", (c.get("location") or "").strip())):
            if value and not person[field]:
                person[field] = value
                added.append(field)
                changes.append((person["name"], field, value, f"dex ({how})"))
        if c["_slug"] and not person["linkedin"]:
            person["linkedin"] = f"https://www.linkedin.com/in/{c['_slug']}"
            added.append("linkedin")

        # Only where the master sheet established nothing.
        if UNVERIFIED.match(person["role"] or "") or not (person["role"] or
                                                          person["company"]):
            jt = (c.get("job_title") or "").strip()
            co = (c.get("company") or "").strip()
            if jt or co:
                person["role"] = jt or person["role"]
                if co and co.lower() != "none":
                    person["company"] = co
                added.append("role/company")
                roles_recovered.append((person["name"], jt, co))
                changes.append((person["name"], "role", jt, f"dex ({how})"))

        extra = dex_notes(c)
        if extra:
            stamp = f"[dex import] {extra}"
            person["notes"] = (person["notes"] + " · " + stamp
                               if person["notes"] else stamp)

        # Cross-checks: reported, never applied. Dex's "Track" column holds
        # the APEX cohort; "מחזור קורס" holds the military course number and
        # is not comparable to it.
        dex_cohort = (c.get("Track") or "").strip()
        if dex_cohort and dex_cohort != person["cohort"]:
            mismatches.append((person["name"], "APEX cohort",
                               person["cohort"], dex_cohort))
        dex_unit = (c.get("Military Track ") or "").strip()
        if dex_unit and person["track"] and dex_unit.lower() not in person["track"].lower():
            mismatches.append((person["name"], "unit",
                               person["track"], dex_unit))

        if added:
            filled.append(f"{person['name']} ({'+'.join(added)})")

    print(f"{len(contacts)} contacts read · {len(roster)} alumni in the roster\n")
    print(f"  matched      {len(roster) - len(unmatched)}")
    print(f"  filled       {len(filled)}")
    print(f"  no match     {len(unmatched)}")
    print(f"  roles recovered for previously-unknown alumni: {len(roles_recovered)}")

    if roles_recovered:
        print("\n  Roll-up progress — role recovered from Dex:")
        for name, jt, co in roles_recovered:
            print(f"    {name:<22} {jt[:38]:<38} @ {co[:22]}")

    if mismatches:
        print("\n  Cross-check disagreements (roster kept, Dex reported):")
        for name, field, mine, theirs in mismatches:
            print(f"    {name:<22} {field}: roster={mine!r} dex={theirs!r}")

    if near:
        print(f"\n  Near matches — NOT merged, confirm by hand:")
        for rn, dn, jt, co in near:
            print(f"    roster {rn:<20} ≈ dex {dn:<22} {jt[:26]} @ {co[:18]}")

    if unmatched:
        print(f"\n  Still unreachable ({len(unmatched)}):")
        for name in unmatched[:20]:
            print(f"    {name}")
        if len(unmatched) > 20:
            print(f"    … and {len(unmatched) - 20} more")

    if not apply:
        print("\nDry run. Re-run with --apply to write the roster.")
        return

    with ROSTER.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(roster)

    if changes:
        import datetime as dt
        today = dt.date.today().isoformat()
        with LOG.open("a", encoding="utf-8") as fh:
            for name, field, value, src in changes:
                fh.write(f"{today} | {name} | {field} |  → {value} | {src}\n")

    print(f"\nwrote {ROSTER.relative_to(ROOT)} "
          f"({len(changes)} field changes logged to logs/roster-log.md)")
    print("Re-run scripts/build_schedule.py and scripts/build_workbook.py "
          "--force to pick up the new numbers.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contacts", type=Path)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    merge(a.contacts, a.apply)
