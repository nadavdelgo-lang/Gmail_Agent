#!/usr/bin/env python3
"""Merge the official APEX contact sheet into config/network/roster.csv.

`Apex_Phones.xlsx` is the organisation's own list, consolidated from the
Master sheets, the cohort-3 registrations, the Notion Founder-Track DB and Dex.
The user has designated it authoritative for contact details, so it wins over
Dex for email / phone / LinkedIn — with one exception, below.

It does NOT win for role and company: the sheet fills those for only 22 of 122
people, while the roster has them for 95 of 97. A blank never overwrites a
value, and a verified role is never replaced.

Three traps this file exists to handle:

  * The LinkedIn column is a hyperlink whose *text* is the word "LinkedIn".
    Read `cell.hyperlink.target`, or you write the literal string "LinkedIn"
    into 96 rows.
  * Hebrew cells carry invisible RTL marks (U+200E/F, U+202A-E) and NBSPs.
    They survive a naive read and break every later comparison.
  * A phone can be truncated in the source. Assaf Monsa's is `054431999-`,
    one digit short — and a number one digit short dials a stranger. A
    shorter number never replaces a well-formed one.

    python3 scripts/merge_apex_sheet.py <xlsx>           # report only
    python3 scripts/merge_apex_sheet.py <xlsx> --apply   # write it
"""

import argparse
import csv
import datetime as dt
import re
import unicodedata
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "config" / "network" / "roster.csv"
LOG = ROOT / "logs" / "roster-log.md"

INVISIBLE = dict.fromkeys(map(ord, "‎‏‪‫‬‭‮"
                                   "⁦⁧⁨⁩﻿"), None)
UNVERIFIED = re.compile(r"^\s*(unknown|identity check|\(roster: none\))", re.I)


def clean(v) -> str:
    if v is None:
        return ""
    s = str(v).translate(INVISIBLE).replace("\xa0", " ")
    s = s.replace("‑", "-").replace("‐", "-").replace("–", "-")
    return " ".join(s.split())


def norm(name: str) -> str:
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^\w\s]", " ", name, flags=re.UNICODE)
    return " ".join(name.lower().split())


def slug(url: str) -> str | None:
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", (url or "").lower())
    return m.group(1).rstrip("/") if m else None


def phone(raw: str) -> tuple[str, bool]:
    """Return (E.164 phone, well_formed). An Israeli number is +972 + 9 digits."""
    d = re.sub(r"\D", "", clean(raw))
    if not d:
        return "", False
    if d.startswith("972"):
        pass
    elif d.startswith("0"):
        d = "972" + d[1:]
    else:
        d = "972" + d
    return "+" + d, len(d) == 12


def read_sheet(path: Path) -> list[dict]:
    ws = openpyxl.load_workbook(path).worksheets[0]     # hyperlinks intact
    cols = ["idx", "name_he", "name", "company_role", "track",
            "email", "linkedin", "phone", "category"]
    people = []
    for row in ws.iter_rows(min_row=4):
        d = {c: clean(cell.value) for c, cell in zip(cols, row)}
        if not (d["name"] or d["name_he"]):
            continue
        if not d["category"] and not d["email"] and not d["phone"]:
            continue                                    # colour-legend rows
        link = row[6]
        d["linkedin"] = (clean(link.hyperlink.target)
                         if link.hyperlink and link.hyperlink.target
                         else ("" if d["linkedin"].lower() == "linkedin" else d["linkedin"]))
        d["phone"], d["phone_ok"] = phone(d["phone"])
        people.append(d)
    return people


def merge(path: Path, apply: bool) -> None:
    with ROSTER.open(encoding="utf-8") as fh:
        roster = list(csv.DictReader(fh))
        columns = list(roster[0].keys())

    sheet = read_sheet(path)
    by_name = {norm(s["name"]): s for s in sheet if s["name"]}
    by_he = {norm(s["name_he"]): s for s in sheet if s["name_he"]}
    by_slug = {slug(s["linkedin"]): s for s in sheet if slug(s["linkedin"])}
    by_mail = {s["email"].lower(): s for s in sheet if s["email"]}

    changes, conflicts, kept, unmatched = [], [], [], []
    seen = set()

    for p in roster:
        s = by_name.get(norm(p["name"]))
        if not s and p.get("name_he"):
            s = by_he.get(norm(p["name_he"]))
        if not s:
            s = by_he.get(norm(p["name"]))              # roster name in Hebrew
        if not s and slug(p["linkedin"]):
            s = by_slug.get(slug(p["linkedin"]))
        if not s and p["email"]:
            s = by_mail.get(p["email"].lower())
        if not s:
            unmatched.append(p["name"])
            continue
        seen.add(id(s))

        # Hebrew name: the roster has none, and call summaries arrive in Hebrew.
        if s["name_he"] and not p.get("name_he"):
            p["name_he"] = s["name_he"]
            changes.append((p["name"], "name_he", s["name_he"]))

        # LinkedIn: the sheet's URLs carry share tracking (?utm_source=share_via
        # ...) and sometimes il.linkedin.com. Every single overlapping row
        # resolves to the same /in/ slug, so the sheet adds nothing but noise
        # where we already have a link. Fill the blanks; report a real
        # disagreement rather than silently picking a side.
        if s["linkedin"]:
            if not p["linkedin"]:
                p["linkedin"] = s["linkedin"]
                changes.append((p["name"], "linkedin", s["linkedin"]))
            elif slug(p["linkedin"]) != slug(s["linkedin"]):
                conflicts.append((p["name"], "linkedin",
                                  p["linkedin"], s["linkedin"]))

        # Email: authoritative, with one exception — a plus-addressed alias
        # (hila4321+aiaram@) is a signup artifact for the same mailbox, not a
        # better way to reach a person. Never displace the plain address with it.
        if s["email"] and s["email"].lower() != p["email"].lower():
            base = s["email"].split("+")[0] + "@" + s["email"].split("@")[-1]
            if "+" in s["email"].split("@")[0] and base.lower() == p["email"].lower():
                kept.append((p["name"], p["email"], s["email"] + " (plus-alias)"))
            else:
                if p["email"]:
                    conflicts.append((p["name"], "email", p["email"], s["email"]))
                    stamp = f"[apex sheet] also reachable at {p['email']}"
                    p["notes"] = (p["notes"] + " · " + stamp) if p["notes"] else stamp
                p["email"] = s["email"]
                changes.append((p["name"], "email", s["email"]))

        # Phone: authoritative, except never trade a valid number for a short one.
        if s["phone"]:
            old_ok = len(re.sub(r"\D", "", p["phone"])) == 12
            if s["phone_ok"] and s["phone"] != p["phone"]:
                if p["phone"]:
                    conflicts.append((p["name"], "phone", p["phone"], s["phone"]))
                p["phone"] = s["phone"]
                changes.append((p["name"], "phone", s["phone"]))
            elif not s["phone_ok"] and old_ok:
                kept.append((p["name"], p["phone"], s["phone"]))
            elif not s["phone_ok"] and not p["phone"]:
                kept.append((p["name"], "(none)", s["phone"]))

        # Military track, where the roster has none.
        if s["track"] and not p["track"]:
            p["track"] = s["track"]
            changes.append((p["name"], "track", s["track"]))

        # Role/company only where the roster established nothing.
        if s["company_role"] and (UNVERIFIED.match(p["role"] or "")
                                  or not (p["role"] or p["company"])):
            parts = [x.strip() for x in s["company_role"].split("|")]
            if len(parts) == 2:
                p["company"], p["role"] = parts[0], parts[1]
            else:
                p["role"] = s["company_role"]
            changes.append((p["name"], "role/company", s["company_role"]))

    extra = [s for s in sheet if id(s) not in seen]

    print(f"roster {len(roster)} · sheet {len(sheet)} people")
    print(f"  matched            {len(roster) - len(unmatched)}")
    print(f"  field changes      {len(changes)}")
    print(f"  overwrote a value  {len(conflicts)}")
    print(f"  not in the sheet   {len(unmatched)}  {unmatched}")

    if kept:
        print("\n  Kept the roster's phone — sheet's is malformed:")
        for n, old, new in kept:
            print(f"    {n:<20} kept {old:<16} sheet had {new}")

    if conflicts:
        print(f"\n  Replaced ({len(conflicts)}) — sheet is authoritative for contact fields:")
        for n, f, old, new in conflicts[:40]:
            print(f"    {n:<20} {f:<9} {old[:38]:<38} -> {new[:38]}")
        if len(conflicts) > 40:
            print(f"    ... and {len(conflicts) - 40} more")

    print(f"\n  In the sheet, not in the roster: {len(extra)}")
    for e in extra:
        print(f"    + {(e['name'] or e['name_he'])[:28]:<28} {e['category']}")

    if not apply:
        print("\nDry run. Re-run with --apply to write the roster.")
        return

    with ROSTER.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(roster)

    today = dt.date.today().isoformat()
    with LOG.open("a", encoding="utf-8") as fh:
        for name, field, value in changes:
            fh.write(f"{today} | {name} | {field} |  -> {value} | apex sheet 6.7.2026\n")

    print(f"\nwrote {ROSTER.relative_to(ROOT)} ({len(changes)} changes logged)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    merge(a.sheet, a.apply)
