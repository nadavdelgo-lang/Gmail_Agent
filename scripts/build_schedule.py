#!/usr/bin/env python3
"""Generate plan/2026-2027/call-schedule.csv — who to call, on which day.

Turns the roster's tiers into a dated rotation: every alum gets their tier's
number of conversations a year, spread so nobody is called twice in quick
succession and every week samples across cohorts.

Regenerating is safe and expected — the schedule is derived, not owned. Rows
already marked done in the existing file keep their status, so re-running after
adding off-weeks or re-tiering someone does not erase history.
"""

import argparse
import csv
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "network" / "network.yaml"
ROSTER = ROOT / "config" / "network" / "roster.csv"
TARGET = ROOT / "plan" / "2026-2027" / "call-schedule.csv"

YEAR_START = dt.date(2026, 9, 1)
YEAR_END = dt.date(2027, 8, 31)

COLUMNS = ["date", "weekday", "week_no", "quarter", "name", "cohort", "tier",
           "channel", "purpose", "phone", "email", "status"]

# Israel works Sunday–Thursday. Thursday is left clear for the weekly report
# and for calls that slipped, so the rotation only fills Sun–Wed.
WEEKDAY_INDEX = {"Sunday": 6, "Monday": 0, "Tuesday": 1, "Wednesday": 2,
                 "Thursday": 3}

UNKNOWN = re.compile(r"^\s*(unknown|identity check|\(roster: none\))", re.I)
# Still mid-build — the conversation is about what is blocking them.
IN_FLIGHT = re.compile(r"stealth|building", re.I)
# Already built something — the conversation is about what they can open up.
FOUNDER_TITLE = re.compile(r"founder|co-founder|\bceo\b|\bcto\b", re.I)


def quarter_of(d: dt.date) -> str:
    """Q1 = Sep–Nov, matching the plan's quarters rather than the calendar's."""
    return f"Q{(d.year * 12 + d.month - (YEAR_START.year * 12 + YEAR_START.month)) // 3 + 1}"


def week_starts(off_weeks: set[str]) -> list[dt.date]:
    """Every Sunday in the plan year, minus the weeks the user has marked off
    (חגים, vacation). Off-weeks are declared in network.yaml, never guessed
    here — the Hebrew calendar is not something to infer."""
    d = YEAR_START
    while d.weekday() != 6:                       # 6 == Sunday
        d += dt.timedelta(days=1)
    weeks = []
    # The last week only counts if its whole Sun–Wed block fits inside the
    # year — otherwise the final call spills into September and shows up in a
    # quarter that does not exist.
    while d + dt.timedelta(days=3) <= YEAR_END:
        if d.isoformat() not in off_weeks:
            weeks.append(d)
        d += dt.timedelta(days=7)
    return weeks


def purpose_for(person: dict) -> str:
    """A starting objective for the call, in the shape §16 asks for — "what I
    want to learn", not "coffee with Tom". These are defaults; /call-log and
    /weekly-brief sharpen them once the roster knows more about the person.
    Anything specific comes from the roster, never from invention.

    Written without gendered pronouns. The roster does not record gender and
    guessing it from a name gets people wrong — which matters more here than
    usual, because these lines get read back in Hebrew where the verb carries
    it."""
    role, company = person["role"], person["company"]
    tier, domain = person["tier"], person["domain"]

    if person["next_action"]:                     # a real one always wins
        return person["next_action"]

    if UNKNOWN.match(role or "") or not (role or company):
        return ("Roll-up — no verified role on file. What are they doing now, "
                "where are they heading, and what do they need?")

    where = f" at {company}" if company else ""
    if tier == "A":
        # Someone mid-build and someone who already built need opposite
        # conversations: one needs the help, the other is the help. Order
        # matters, and so does not over-claiming — "Building @ Wiz" means they
        # work at Wiz, not that they founded it.
        if IN_FLIGHT.search(f"{role} {company}"):
            return ("Founding track — building this year? What is the blocker, "
                    "is co-founder the gap, and who should they meet?")
        if FOUNDER_TITLE.search(role or ""):
            # Name the company only when the source attached it to the founder
            # title itself. The column is populated from "Role @ Company", so
            # anything else stays unnamed rather than credited to the wrong firm.
            named = f" — founded {company}" if company else ""
            return (f"Node candidate{named}. What can they open for our "
                    f"alumni, and would they give office hours?")
        return (f"Transition point{where} — what are they building or moving "
                f"toward, what is the blocker, and who should they meet?")
    if tier == "B":
        give = f" into {company}" if company else ""
        return (f"What can they give — office hours, referrals{give}, "
                f"mentoring? And what do they need from us right now?")
    return (f"Stay current — still{where}? What are they working on"
            f"{f' in {domain}' if domain else ''}, and what would help?")


def load_existing() -> dict[tuple[str, int], str]:
    """Previous run's statuses, keyed by (name, nth call of the year)."""
    if not TARGET.exists():
        return {}
    seen: dict[str, int] = defaultdict(int)
    out = {}
    with TARGET.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            seen[row["name"]] += 1
            if row.get("status"):
                out[(row["name"], seen[row["name"]])] = row["status"]
    return out


def build() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    tiers = config["tiers"]
    cadence = config["cadence"]
    off = {str(w) for w in (cadence.get("off_weeks") or [])}
    days = [WEEKDAY_INDEX[d] for d in cadence["call_days"]]

    with ROSTER.open(encoding="utf-8") as fh:
        people = list(csv.DictReader(fh))

    weeks = week_starts(off)
    n_weeks = len(weeks)

    # Every (person, occurrence) pair gets an ideal week: people of the same
    # tier are staggered by their position in the tier, and their repeat calls
    # are spaced a full cycle apart. Cohort is folded into the sort key so a
    # week's four calls come from different cohorts wherever possible.
    slots = []
    by_tier: dict[str, list[dict]] = defaultdict(list)
    for p in people:
        by_tier[p["tier"]].append(p)

    for tier, members in by_tier.items():
        per_year = tiers[tier]["calls_per_year"]
        cycle = n_weeks / per_year
        members.sort(key=lambda p: (p["cohort"], p["name"]))
        for i, p in enumerate(members):
            offset = (i / max(len(members), 1)) * cycle
            for occurrence in range(per_year):
                ideal = offset + occurrence * cycle
                slots.append({"person": p, "occurrence": occurrence + 1,
                              "ideal": ideal})

    # Deal them into weeks. Per-week capacity is fixed up front so the totals
    # match exactly and no week ends up light: with 189 calls over 52 weeks,
    # 33 weeks take 4 and 19 take 3 — all inside §5's "3–5 a week". The spare
    # calls are spread evenly rather than bunched at the front.
    base, extra = divmod(len(slots), n_weeks)
    capacity = [base + (1 if extra and (i * extra) % n_weeks < extra else 0)
                for i in range(n_weeks)]
    while sum(capacity) < len(slots):             # rounding slack
        capacity[capacity.index(min(capacity))] += 1

    load: dict[int, list[dict]] = defaultdict(list)
    for slot in sorted(slots, key=lambda s: s["ideal"]):
        target = min(int(slot["ideal"]), n_weeks - 1)
        for step in range(n_weeks):               # nearest week with room
            for candidate in ({target + step, target - step}
                              if step else {target}):
                if 0 <= candidate < n_weeks and len(load[candidate]) < capacity[candidate]:
                    load[candidate].append(slot)
                    break
            else:
                continue
            break

    existing = load_existing()
    rows = []
    for week_no, monday in enumerate(weeks, start=1):
        # Interleave cohorts inside the week so each one samples the network.
        members = sorted(load[week_no - 1],
                         key=lambda s: (s["person"]["cohort"], s["person"]["tier"]))
        for i, slot in enumerate(members):
            p = slot["person"]
            day = monday + dt.timedelta(days=(days[i % len(days)] + 1) % 7)
            rows.append({
                "date": day.isoformat(),
                "weekday": day.strftime("%A"),
                "week_no": week_no,
                "quarter": quarter_of(day),
                "name": p["name"],
                "cohort": p["cohort"],
                "tier": p["tier"],
                "channel": "phone" if p["phone"] else (
                    "email" if p["email"] else "linkedin"),
                "purpose": purpose_for(p),
                "phone": p["phone"],
                "email": p["email"],
                "status": existing.get((p["name"], slot["occurrence"]), ""),
            })

    rows.sort(key=lambda r: r["date"])
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    per_week = defaultdict(int)
    for r in rows:
        per_week[r["week_no"]] += 1
    counts = sorted(set(per_week.values()))
    print(f"wrote {len(rows)} calls to {TARGET.relative_to(ROOT)}")
    print(f"  {n_weeks} weeks, {min(counts)}–{max(counts)} calls/week "
          f"(§5 asks for 3–5)")
    print(f"  {sum(1 for r in rows if r['status'])} rows kept a previous status")
    if off:
        print(f"  {len(off)} weeks skipped as off-weeks")
    else:
        print("  no off-weeks set — add the חגים and vacation Sundays to "
              "cadence.off_weeks in network.yaml and re-run")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
