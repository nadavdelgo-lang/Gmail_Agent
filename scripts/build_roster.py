#!/usr/bin/env python3
"""Build config/network/roster.csv from the APEX alumni master spreadsheet.

Run once to seed the roster. After that the file is owned by the skills
(/call-log, /network-sync), so re-running would discard everything they have
learned — the script refuses unless --force is passed.

The source sheet was built to screen alumni against GPU-systems / power /
real-time-control criteria for a founding team. That is a different question
from the one the network role asks, so its verdicts are preserved verbatim in
`source_note` and never used for tiering. Tiers are re-derived here from the
role definition's own priority list (§5).
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "source" / "Apex_Master_150726.xlsx"
TARGET = ROOT / "config" / "network" / "roster.csv"

COLUMNS = [
    "id", "name", "name_he", "cohort", "founder_track", "track", "company",
    "role", "location", "domain", "tier", "tie_strength", "current_goal",
    "needs", "can_help", "last_contact", "last_source", "next_action",
    "next_action_due", "linkedin", "email", "phone", "source_note", "notes",
]

# --- tiering (role definition §5) -------------------------------------------
# Tier sets CALL FREQUENCY only. It is not a judgement of who matters, and the
# matching engine ignores it entirely — a tier-C engineer at Wiz is still a
# first-class referral path into Wiz.
#
# A (3 calls/yr): founders, stealth builders, anyone at a transition point —
#   the people §5 says to prioritise, and whose situation changes fastest.
# B (2 calls/yr): people carrying seniority or research standing. This is the
#   pool that supplies office hours, referrals and introductions for tier A,
#   so it is worth knowing what they can give and keeping it current.
# C (1 call/yr): no verified role — the Alumni Roll-Up backlog (§9), where the
#   first touch is finding out what they actually do — plus individual
#   contributors whose situation moves slowly. An annual touch is honest; two
#   would be activity for its own sake, which §22 explicitly warns against.

FOUNDER = re.compile(
    r"stealth|founder|co-founder|founding|\bceo\b|\bcto\b|building", re.I)
UNKNOWN = re.compile(r"^\s*(unknown|identity check|\(roster: none\))", re.I)
SENIOR = re.compile(
    r"\blead\b|leader|leading|\bhead\b|director|principal|chief|architect|"
    r"\bvp\b|senior|manager|\bmgr\b|executive|professor|researcher|research|"
    r"scientist|\bphd\b|physicist|officer", re.I)

# --- domain, derived from the role text -------------------------------------
# Ordered: first match wins. Used by the matching engine to answer "who else
# works on this", so it is deliberately coarse — a wrong-but-plausible domain
# is worse than a blank one.
DOMAINS = [
    ("security", r"security|cyber|wiz\b|cyera|snyk|orca|palo alto|claroty|"
                 r"zafran|breeze|puresec|akeyless|miggo|threat|firmware|"
                 r"ics/ot|reverse-engineering|binary-exploitation|d-fend"),
    ("research", r"\bphd\b|\bmsc\b|weizmann|technion|\btau\b|bar-ilan|"
                 r"professor|researcher|research student|hebrew university|huji"),
    ("quantum-physics", r"quantum|physicist|fusion|pulsed power"),
    ("ai-ml", r"\bai\b|\bml\b|machine learning|deep learning|algorithm|"
              r"data scien|nlp|llm|ai-coe|autonomous|computer vision"),
    ("infra-systems", r"infra|cloud|network|dpdk|smartnic|\bdpu\b|datapath|"
                      r"platform|architect|datadog|azure|kubernetes|granulate|"
                      r"back-end|full-stack|software engineer|swe\b"),
    ("hardware-embedded", r"embedded|imaging|iot|solaredge|wokwi|tinytapeout|"
                          r"dna storage|hardware|elbit|rafael|vayyar"),
    ("health-bio", r"health|medic|\bmed\b|care|cardia|protai|predicta|bio"),
    ("product-gtm", r"product|\bcpo\b|\bvp\b|alliance|manager|director|"
                    r"consultant|advisor"),
]


def derive_domain(role: str) -> str:
    text = role or ""
    for name, pattern in DOMAINS:
        if re.search(pattern, text, re.I):
            return name
    return ""


def derive_tier(role: str, founder_track: bool) -> str:
    if founder_track:
        return "A"
    role = role or ""
    if UNKNOWN.match(role) or not role.strip():
        return "C"
    if FOUNDER.search(role):
        return "A"
    if SENIOR.search(role):
        return "B"
    return "C"


def split_role_company(raw: str) -> tuple[str, str]:
    """Split "CTO @ Stealth" into role and company. Text with no @ stays whole
    as the role — guessing a company out of prose is exactly the kind of
    invented fact the roster must not carry."""
    text = (raw or "").strip()
    if not text:
        return "", ""
    if "@" in text:
        role, _, company = text.partition("@")
        return role.strip().rstrip(","), company.strip().split(";")[0].strip()
    return text, ""


def build(force: bool = False) -> int:
    if TARGET.exists() and not force:
        sys.exit(
            f"{TARGET} already exists. It is owned by the skills once seeded — "
            "re-running would discard every call, need and next action recorded "
            "since. Pass --force only if you really mean to reset it."
        )

    wb = openpyxl.load_workbook(SOURCE, data_only=True)
    rows = list(wb["Evaluation"].iter_rows(values_only=True))
    header, body = rows[0], rows[1:]
    assert header[1] == "Name", f"unexpected sheet layout: {header}"

    out = []
    for raw in body:
        num, name, cohort, track, verified, linkedin, rationale = raw[:7]
        if not name:
            continue
        role, company = split_role_company(verified)
        cohort = (cohort or "").strip()
        # "#2 + Founder Track" is two facts in one cell. Split them so the
        # funnel KPI can count cohorts without three of them having size 1.
        founder_track = "yes" if "founder track" in cohort.lower() else ""
        cohort = cohort.split("+")[0].strip()
        track = (track or "").strip()
        linkedin = (linkedin or "").strip()
        if linkedin.startswith("("):        # "(roster: none)" is not a URL
            linkedin = ""
        out.append({
            "id": str(int(num)) if isinstance(num, float) else str(num or ""),
            "name": name.strip(),
            "name_he": "",
            "cohort": cohort,
            "founder_track": founder_track,
            "track": "" if track == "-" else track,
            "company": company,
            "role": role,
            "location": "",
            "domain": derive_domain(verified or ""),
            "tier": derive_tier(verified or "", bool(founder_track)),
            "tie_strength": "",
            "current_goal": "",
            "needs": "",
            "can_help": "",
            "last_contact": "",
            "last_source": "",
            "next_action": "",
            "next_action_due": "",
            "linkedin": linkedin,
            "email": "",
            "phone": "",
            "source_note": (rationale or "").strip(),
            "notes": "",
        })

    out.sort(key=lambda r: (r["cohort"], r["name"]))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(out)

    tiers = {t: sum(1 for r in out if r["tier"] == t) for t in "ABC"}
    cohorts: dict[str, int] = {}
    for r in out:
        cohorts[r["cohort"]] = cohorts.get(r["cohort"], 0) + 1
    print(f"wrote {len(out)} alumni to {TARGET.relative_to(ROOT)}")
    print(f"  tiers    {tiers}  → {tiers['A']*3 + tiers['B']*2 + tiers['C']} "
          f"conversations/year")
    print(f"  cohorts  {cohorts}")
    unverified = sum(1 for r in out if UNKNOWN.match(r["role"] or "")
                     or not (r["role"] or r["company"]))
    print(f"  no verified role  {unverified} (the Alumni Roll-Up backlog)")
    return len(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing roster.csv")
    build(**vars(ap.parse_args()))
