#!/usr/bin/env python3
"""Merge a contacts export into config/network/roster.csv — phone and email only.

The seed roster has LinkedIn URLs and nothing else to reach anyone by, so the
call schedule cannot show a number until this has run. Point it at a Google
Contacts CSV, a Dex export, or anything with name/email/phone columns.

Matching is exact on a normalised name, plus Hebrew names via the roster's
name_he column. Near-misses are reported for the user to resolve by hand and
never merged on a guess: writing the wrong phone number against a name means
calling the wrong person.

    python3 scripts/merge_contacts.py contacts.csv           # report only
    python3 scripts/merge_contacts.py contacts.csv --apply   # write it
"""

import argparse
import csv
import difflib
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "config" / "network" / "roster.csv"

# Column names are matched with punctuation and spacing stripped, so "E-mail
# 1 - Value" (Google Contacts), "e_mail" and "Email" all reduce to the same
# key. Getting this wrong is silent — the merge reports success and fills
# nothing — so the prefixes below are deliberately generous.
NAME_FIELDS = ["name", "fullname", "displayname", "שם"]
EMAIL_FIELDS = ["email", "emailaddress", "primaryemail", "אימייל", "מייל"]
PHONE_FIELDS = ["phone", "mobile", "phonenumber", "primaryphone", "cell",
                "טלפון", "נייד"]


def normalise(name: str) -> str:
    """Fold case, accents and punctuation so "Ben-Uri" matches "ben uri"."""
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^\w\s]", " ", name, flags=re.UNICODE)
    return " ".join(name.lower().split())


def normalise_phone(raw: str) -> str:
    """Keep digits and a leading +. Israeli local form becomes +972 so the two
    notations for one number do not read as two different people."""
    digits = re.sub(r"[^\d+]", "", raw or "")
    if digits.startswith("0") and len(digits) >= 9:
        return "+972" + digits[1:]
    return digits


def fold(key: str) -> str:
    """"E-mail 1 - Value" → "email1value"."""
    return re.sub(r"[^a-z0-9֐-׿]", "", (key or "").lower())


def pick(row: dict, candidates: list[str]) -> str:
    folded = {fold(k): (v or "").strip() for k, v in row.items() if k}
    for field in candidates:                       # exact first
        if folded.get(field):
            return folded[field]
    # Google Contacts numbers its columns: "Phone 2 - Value", "E-mail 3 - Value".
    # Take the lowest-numbered non-empty one, which is the primary.
    for key in sorted(folded):
        if folded[key] and any(key.startswith(f) for f in candidates):
            return folded[key]
    return ""


def load_contacts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    contacts = []
    for row in rows:
        name = pick(row, NAME_FIELDS)
        if not name:
            first = pick(row, ["firstname", "givenname"])
            last = pick(row, ["lastname", "familyname", "surname"])
            name = f"{first} {last}".strip()
        if not name:
            continue
        contacts.append({
            "name": name,
            "email": pick(row, EMAIL_FIELDS),
            "phone": normalise_phone(pick(row, PHONE_FIELDS)),
        })
    return contacts


def merge(contacts_path: Path, apply: bool) -> None:
    with ROSTER.open(encoding="utf-8") as fh:
        roster = list(csv.DictReader(fh))
        columns = list(roster[0].keys())

    contacts = load_contacts(contacts_path)
    index: dict[str, dict] = {}
    for c in contacts:
        index.setdefault(normalise(c["name"]), c)

    filled, already, unmatched, suggestions = [], [], [], []
    for person in roster:
        keys = [normalise(person["name"])]
        if person.get("name_he"):
            keys.append(normalise(person["name_he"]))
        match = next((index[k] for k in keys if k in index), None)

        if not match:
            # Loose on purpose: a near match is only ever reported for the user
            # to confirm, never merged, so a few false suggestions cost nothing
            # and a missed one leaves an alum unreachable all year.
            close = difflib.get_close_matches(keys[0], index, n=1, cutoff=0.80)
            if close:
                suggestions.append((person["name"], index[close[0]]["name"]))
            else:
                unmatched.append(person["name"])
            continue

        added = []
        for field in ("email", "phone"):
            if match[field] and not person[field]:
                person[field] = match[field]
                added.append(field)
        (filled if added else already).append(
            f"{person['name']} ({'+'.join(added)})" if added else person["name"])

    print(f"{len(contacts)} contacts read, {len(roster)} alumni in the roster\n")
    print(f"  filled       {len(filled)}")
    print(f"  already set  {len(already)}")
    print(f"  no match     {len(unmatched)}")

    if suggestions:
        print(f"\n  near matches — not merged, confirm by hand "
              f"(add the Hebrew spelling to name_he, or fix the contact):")
        for roster_name, contact_name in suggestions:
            print(f"    roster: {roster_name:<28} contact: {contact_name}")

    if unmatched:
        print(f"\n  still unreachable ({len(unmatched)}) — these stay on "
              f"LinkedIn until a number turns up:")
        for name in unmatched[:15]:
            print(f"    {name}")
        if len(unmatched) > 15:
            print(f"    … and {len(unmatched) - 15} more")

    if not apply:
        print("\nDry run. Re-run with --apply to write config/network/roster.csv.")
        return

    with ROSTER.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(roster)
    print(f"\nwrote {ROSTER.relative_to(ROOT)} — "
          f"re-run scripts/build_schedule.py to pick up the new numbers.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contacts", type=Path, help="contacts export (.csv)")
    ap.add_argument("--apply", action="store_true",
                    help="write the roster; without it this is a dry run")
    args = ap.parse_args()
    merge(args.contacts, args.apply)
