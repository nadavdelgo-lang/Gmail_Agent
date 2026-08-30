#!/usr/bin/env python3
"""Generate the daily APEX calendar blocks as JSON, ready to create.

Three blocks a working day, Sunday–Thursday:

  10:30  Daily brief        — what today needs, against the yearly roadmap
  11:30  Alumni call        — the person from the rotation, with their details
  16:30  Follow-through     — closing loops from earlier calls

The brief and the follow-through are identical every day, so they emit as two
recurring events. The 11:30 block carries a different person each day and has
to be one event per day.

Nothing here touches the calendar — it prints JSON for the caller to create,
so the payloads can be read before anything is written.

    python3 scripts/build_calendar_blocks.py --until 2026-11-30 > blocks.json
"""

import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "network" / "network.yaml"
ROSTER = ROOT / "config" / "network" / "roster.csv"
SCHEDULE = ROOT / "plan" / "2026-2027" / "call-schedule.csv"

TZ = "Asia/Jerusalem"
BRIEF_AT = "10:30"
CALL_AT = "11:30"
FOLLOW_AT = "16:30"
WORKDAYS = [6, 0, 1, 2, 3]          # Sun–Thu, Python weekday numbering


def block(start: dt.date, at: str, minutes: int = 30) -> tuple[str, str]:
    h, m = map(int, at.split(":"))
    begin = dt.datetime.combine(start, dt.time(h, m))
    return begin.isoformat(), (begin + dt.timedelta(minutes=minutes)).isoformat()


def contact_lines(person: dict) -> str:
    """LinkedIn and phone, honest about what is missing. An empty phone field
    is stated as empty rather than left out — a blank line reads as an
    oversight, and the reason it is blank is actionable."""
    linkedin = (f'<a href="{person["linkedin"]}">{person["linkedin"]}</a>'
                if person["linkedin"] else
                "— not on file (no LinkedIn in the roster)")
    phone = person["phone"] or (
        "— not on file · export your contacts and run "
        "<code>scripts/merge_contacts.py</code>")
    email = person["email"] or "—"
    return (f"<b>Contact</b><br>"
            f"LinkedIn: {linkedin}<br>"
            f"Phone: {phone}<br>"
            f"Email: {email}")


ASK = ("<b>Before you hang up</b> (§6)<br>"
       "עכשיו · השלב הבא · חסם · את מי צריך להכיר · איפה יכול לעזור · APEX<br><br>"
       "<b>Then</b> paste the summary into <code>/call-log</code> — it updates "
       "the roster and drafts the follow-up with intro offers.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", default="2026-09-06")
    ap.add_argument("--until", default="2026-11-30")
    args = ap.parse_args()

    start = dt.date.fromisoformat(args.start)
    until = dt.date.fromisoformat(args.until)

    cadence = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["cadence"]
    off_days = {str(d) for d in (cadence.get("off_days") or [])}
    off_weeks = {str(w) for w in (cadence.get("off_weeks") or [])}

    roster = {r["name"]: r for r in csv.DictReader(ROSTER.open(encoding="utf-8"))}
    calls: dict[str, list[dict]] = defaultdict(list)
    for row in csv.DictReader(SCHEDULE.open(encoding="utf-8")):
        calls[row["date"]].append(row)

    # Working days in range: Sun–Thu, minus חגים and any full off-week.
    days = []
    d = start
    while d <= until:
        sunday = d - dt.timedelta(days=(d.weekday() + 1) % 7)
        if (d.weekday() in WORKDAYS and d.isoformat() not in off_days
                and sunday.isoformat() not in off_weeks):
            days.append(d)
        d += dt.timedelta(days=1)

    skipped = sorted(off_days | off_weeks)
    exdates = []
    d = start
    while d <= until:
        sunday = d - dt.timedelta(days=(d.weekday() + 1) % 7)
        if d.weekday() in WORKDAYS and (d.isoformat() in off_days
                                        or sunday.isoformat() in off_weeks):
            exdates.append(d)
        d += dt.timedelta(days=1)

    until_rule = until.strftime("%Y%m%dT235959Z")
    recurrence = [f"RRULE:FREQ=WEEKLY;BYDAY=SU,MO,TU,WE,TH;UNTIL={until_rule}"]
    if exdates:
        stamps = ",".join(f"{x:%Y%m%d}T{BRIEF_AT.replace(':', '')}00"
                          for x in exdates)
        recurrence.append(f"EXDATE;TZID={TZ}:{stamps}")

    events = []

    # --- 1. the daily brief (one recurring event) --------------------------
    s, e = block(days[0], BRIEF_AT)
    events.append({
        "kind": "recurring",
        "summary": "APEX · Daily brief",
        "startTime": s, "endTime": e, "timeZone": TZ,
        "eventType": "FOCUS_TIME",
        "colorId": "5",
        "recurrenceData": recurrence,
        "description": (
            "<b>Today against the roadmap.</b><br><br>"
            "1. Today's call — open <code>plan/2026-2027/call-schedule.csv</code>, "
            "read the person's row in <code>config/network/roster.csv</code>.<br>"
            "2. Open next actions — Google Tasks, list <b>Velocity + Apex</b>.<br>"
            "3. Overdue — any tier-A alum not spoken to in 4 months, tier B in 6.<br>"
            "4. This quarter — Q1 is the 90-day test: all 27 tier-A called, "
            "the 16 unknowns resolved, 8 Office Hours contributors, SF phases 1–2.<br><br>"
            "<b>Sunday</b> also: write the Monday briefing for Avishag "
            "(<code>/weekly-brief</code>).<br>"
            "<b>Thursday</b> also: the weekly report and the three lines — "
            "מה למדתי · מה אני ממליץ · מה אני צריך מאבישג.<br><br>"
            "Ask <code>/weekly-brief</code> for either."),
    })

    # --- 2. the follow-through block (one recurring event) -----------------
    s, e = block(days[0], FOLLOW_AT)
    follow_rec = list(recurrence)
    if exdates:
        follow_rec[1] = follow_rec[1].replace(
            f"T{BRIEF_AT.replace(':', '')}00", f"T{FOLLOW_AT.replace(':', '')}00")
    events.append({
        "kind": "recurring",
        "summary": "APEX · Follow-through",
        "startTime": s, "endTime": e, "timeZone": TZ,
        "eventType": "FOCUS_TIME",
        "colorId": "5",
        "recurrenceData": follow_rec,
        "description": (
            "<b>Closing the loops from earlier calls.</b> This is where the "
            "network actually compounds — §3: וסוגרים מעגל, גם אם אבישג לא "
            "עונה, דלג׳ו הוא שמוודא שיש סגירת מעגל.<br><br>"
            "• Send the intro offers you agreed to make — and check the other "
            "side said yes first.<br>"
            "• Review drafts <code>/call-log</code> saved. Nothing sends itself.<br>"
            "• Anything promised on a call and not yet done.<br>"
            "• Roster rows with no <code>next_action</code>.<br><br>"
            "No introduction without an answer to: why do these two need to "
            "know each other <i>now</i>?"),
    })

    # --- 3. the named call blocks (one event per day) ----------------------
    for day in days:
        iso = day.isoformat()
        s, e = block(day, CALL_AT)
        todays = calls.get(iso, [])
        if todays:
            # Normally one person a day. If a regeneration ever puts two on the
            # same date, carry both into the block rather than silently
            # dropping the second — a lost call is invisible on a calendar.
            blocks = []
            for row in todays:
                person = roster.get(row["name"], {})
                blocks.append(
                    f"<b>{row['name']}</b> — Cohort {row['cohort']} · Tier "
                    f"{row['tier']}"
                    + (f" · {person.get('role')}" if person.get("role") else "")
                    + (f" @ {person.get('company')}" if person.get("company") else "")
                    + "<br><br>"
                    f"<b>Why this call</b><br>{row['purpose']}<br><br>"
                    f"{contact_lines(person)}")
            events.append({
                "kind": "call",
                "date": iso,
                "summary": "APEX call · " + " + ".join(r["name"] for r in todays),
                "startTime": s, "endTime": e, "timeZone": TZ,
                "colorId": "5",
                "description": "<br><hr><br>".join(blocks) + f"<br><br>{ASK}",
            })
        else:
            # No scheduled alum — the rotation runs 3–4 a week by design. Keep
            # the hour, and point it at work that is genuinely outstanding.
            week = [r for d2, rs in calls.items() for r in rs
                    if 0 <= (day - dt.date.fromisoformat(d2)).days <= 6]
            recent = ", ".join(r["name"] for r in week) or "—"
            events.append({
                "kind": "open",
                "date": iso,
                "summary": "APEX call · open slot",
                "startTime": s, "endTime": e, "timeZone": TZ,
                "colorId": "8",
                "description": (
                    "<b>No one scheduled today</b> — the rotation runs 3–4 "
                    "conversations a week, which is §5's range. Keep the hour "
                    "and use it for one of:<br><br>"
                    f"• A callback to someone from this week: {recent}<br>"
                    "• The most overdue tier-A alum — check "
                    "<code>last_contact</code> in the roster<br>"
                    "• Someone Avishag flagged, or a name from a chat export<br>"
                    "• An Office Hours contributor you have not yet recruited "
                    "(Q1 target: 8)<br><br>"
                    "If none of those are live, give the half hour back."),
            })

    print(json.dumps({
        "range": [args.start, args.until],
        "working_days": len(days),
        "named_calls": sum(1 for e in events if e["kind"] == "call"),
        "open_slots": sum(1 for e in events if e["kind"] == "open"),
        "skipped_for_holidays": skipped,
        "events": events,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
