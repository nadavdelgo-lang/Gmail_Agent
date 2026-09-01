# The two weekly Routines

Both briefs are Gmail drafts, and a Routine fired from Claude Code cannot reach
Gmail: attaching connectors to a trigger is blocked for this organisation
(`create_trigger` returns *"the connectors parameter is not available for this
organization"*). A Routine created here would fire on time and produce nothing.

So these two live in the **claude.ai Routines UI**, where Gmail can be attached
to the schedule. The prompts below are the whole configuration — paste them in.

| | Sunday briefing | Thursday report |
|---|---|---|
| When | Sunday 08:00 Israel | Thursday 08:00 Israel |
| Cron (UTC) | `0 5 * * 0` | `0 5 * * 4` |
| Session | fresh each firing | fresh each firing |
| Connectors | **Gmail**, Google Calendar, Fireflies | **Gmail**, Fireflies |

Israel is UTC+3 in summer and UTC+2 in winter, so `0 5` is 08:00 from late
March to late October and 07:00 the rest of the year. If the winter hour
matters, run two Routines and disable the one that is out of season — the UI
has no timezone field.

---

## Sunday 08:00 — the week ahead (§16)

```
Run the /weekly-brief skill in Mode A — the Sunday briefing to Avishag for the
week starting today.

Repo: nadavdelgo-lang/gmail_agent, branch claude/apex-velocity-yearly-plan-tv5ru8.
Read .claude/skills/weekly-brief/SKILL.md first and follow it exactly; it is the
specification, not a suggestion.

Do Step 0 in full before writing anything:
1. Sweep the week's correspondence across BOTH of Avishag's addresses —
   (from:avishag@apex.org.il OR to:avishag@apex.org.il OR
    from:avishag@velocityx.vc OR to:avishag@velocityx.vc) newer_than:7d -in:draft
   plus anything from team@apex.org.il that assigns either of them something.
   Read every thread in full with get_thread — search previews hide the newest
   message, which is usually the one that matters.
2. Call summaries: (from:me OR to:me) (סיכום OR summary OR "notes from" OR
   "call with") newer_than:10d
3. Fireflies for the window — check Summary Status before trusting a summary.
4. config/network/roster.csv, plan/2026-2027/call-schedule.csv,
   logs/roster-log.md, logs/calls/
5. The register draft, subject אפקס + Velocity — כל המשימות בינינו במקום אחד

Then write the briefing with exactly these sections and caps: Top People (≤5),
Opportunities (≤3), Risks / Weak Signals (≤3), מה אני צריך ממך (≤3, ideally 0),
השבוע. Pipe format for Top People. Every Avishag item carries all five parts:
מי · למה עכשיו · למה דווקא היא · מה בדיוק · כמה זמן. Risks are computed from
last_contact against tier cadence, not remembered.

Hebrew, informal-direct, feminine forms, signs דלג׳ו — config/voice.md.

list_drafts first: update this week's draft in place if it exists, create it if
not. Never stack two. Draft only — do not send.

Report back: which threads fed which section, and anything you left out and why.
```

---

## Thursday 08:00 — the week's numbers (§17, §21)

```
Run the /weekly-brief skill in Mode B — the Thursday report to Avishag.

Repo: nadavdelgo-lang/gmail_agent, branch claude/apex-velocity-yearly-plan-tv5ru8.
Read .claude/skills/weekly-brief/SKILL.md first and follow it exactly.

Do Step 0 in full — the same correspondence sweep across both of Avishag's
addresses, call summaries, Fireflies, the roster and the call log.

Then the nine-row KPI table in this order, targets read from
config/network/network.yaml → reporting.thursday_report.kpis:
שיחות בוגרים משמעותיות · בוגרים עם מידע מעודכן במערכת · חיבורים איכותיים
שבוצעו · חיבורים שהובילו לתוצאה · בוגרים שעזרו לבוגר אחר · Contributors /
Office Hours · קשרים חדשים ב-SF · קשרים שעברו מאבישג לנדב · דברים שבאמת
דרשו את אבישג.

Count every actual from the data. A number you cannot source is a dash and a
one-line explanation — never an estimate. This mail goes to the person the
numbers are about.

Then §18 dependency, §19 funnel off tie_strength, §20 connection quality, and
§21's three lines: מה למדתי · מה אני ממליץ · מה אני צריך מאבישג.

Carry the framing every week: לא צריך שכל המספרים יעלו כל שבוע. אנחנו מחפשים
מגמה ואיכות.

Hebrew, informal-direct, feminine forms, signs דלג׳ו — config/voice.md.

list_drafts first: update this week's draft in place if it exists. Draft only —
do not send.

Report back: which KPIs had real data behind them and which were dashed.
```

---

## If the two Claude Code Routines still exist

`trig_01Uu11zHda7UFY6HoPRMMqaV` (Sunday) and `trig_01QodELhUzm9Fm17NcMm3Yiw`
(Thursday) were created before the connector limit was known. They fire without
Gmail and produce nothing. Delete them so the UI Routines are the only ones
running — two schedules for one brief is how you end up with two drafts.
