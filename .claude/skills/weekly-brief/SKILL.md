---
name: weekly-brief
description: Produce the Monday briefing to Avishag or the Thursday weekly report for Apex — Top People, Opportunities, Risks, what needs Avishag, the week's calls, the KPI table, the dependency and funnel numbers, and the three closing lines. Built from the roster and the call schedule, saved as a Gmail draft. Runs on a Routine Sunday evening and Thursday afternoon. Use when the scheduled brief fires, or when the user asks for his weekly briefing, the Monday brief, the weekly report, or his KPIs.
---

# Weekly brief

Two reports, one skill. Both are Gmail drafts to Avishag, never sent, and both
are built from `roster.csv` and `call-schedule.csv` rather than from memory —
which is what makes them cost minutes instead of an evening.

Pick the mode from what he asked for, or from the day: Sunday/Monday → the
briefing; Thursday/Friday → the report. If it is ambiguous, ask.

## Ground truth

- `config/network/network.yaml` — the `reporting` block holds both formats and
  every KPI definition. Read it; do not reproduce the numbers from here.
- `config/network/roster.csv`, `plan/2026-2027/call-schedule.csv`
- `logs/roster-log.md`, `logs/calls/` — what actually happened this week
- `config/voice.md` — how he writes

Resolve Gmail tool names with ToolSearch every run.

## One living draft

Follow the `avishag-register` discipline. `list_drafts` first:

- **Draft with this week's subject exists** → `update_draft` in place.
- **Already sent** → start a fresh draft for the new week.
- **Neither** → create it.

Never stack two briefings. Two is worse than none.

## Step 0 — gather what actually happened

Run this before either mode. It is what stops the brief from being a
restatement of the plan.

**1. Call summaries the user wrote or was sent.** Search mail for a real
summary — one someone typed, not a notification:

```
(from:me OR to:me) (סיכום OR summary OR "notes from" OR "call with") newer_than:10d
```

Anything that reads as an account of a conversation with an alum is a
summary. Run it through `/call-log` first if the roster has not been updated
from it — the brief reports what the roster knows, so the roster comes first.

**2. Fireflies.** Meeting recordings live there, and the recap mail Fireflies
sends is a link with no content in it — the body is boilerplate, so never try
to read a summary out of the email itself. Use the connector:
`fireflies_get_transcripts` for the window, then `fireflies_get_summary` per
meeting.

Two things to check before trusting one:
- **`Summary Status`.** `skipped` means Fireflies generated nothing and the
  "summary" field is empty. Say so rather than reporting silence as calm.
- **Transcript quality.** A short meeting can come back as a handful of
  single words — real audio was not captured. That is not a summary of
  anything; do not extract facts from it.

Match the meeting to a roster row by participant email, then by title. A
meeting whose participants are Tinu or VelocityX counterparties is not alumni
work — the workstream firewall in `network.yaml` applies here too.

**3. The roster and the schedule.** `last_contact`, `next_action` and the
Call Schedule's status column are the record of what was actually done.

**When all three come back empty, the brief says so in one line** and reports
the week from the schedule and the roster alone. An honest "no calls logged
this week" is the finding; inventing activity to fill the format is the one
thing this skill must never do.

---

# Mode A — Monday briefing (§16)

Sent **before** the Weekly People Review, so the hour is spent on people,
opportunities, judgement and decisions — never on transferring information.
That is the entire reason this document exists.

Subject: `בריפינג שבועי — אנשים · <date>`

### Top People — up to 5

The people she needs to know about this week. Draw from: rows whose
`current_goal` or `needs` changed in the last seven days (check
`logs/roster-log.md`), anyone who moved toward founding, and anyone with a live
`next_action` that concerns her.

`Name | Cohort | what changed | what they need | who owns it`

> דנה | Cohort 2 | עוזבת Meta ומתחילה חברה | מחפשת co-founder טכני | נדב מטפל

The "who owns it" clause is the point — it is where the dependency KPI comes
from. Default to "נדב מטפל".

### Opportunities — up to 3

An alum starting a company; a significant researcher who wants to connect to
APEX; someone in the SF network willing to give office hours; two alumni it is
right to introduce. Each with the "why now".

### Risks / Weak Signals — up to 3

**Compute these, do not remember them.** The most valuable line in the document
and the easiest to generate:

- A tier-A alum whose `last_contact` is older than their cadence — this is
  §16's "very strong alum, no contact in five months", found mechanically.
- Someone we want to keep close who is moving to another organisation.
- A contributor receiving too many requests (§12) — check how often they have
  been proposed in `logs/calls/`.

### Avishag Needed — up to 3, ideally zero

Each one must carry all five: **who · why now · why her specifically · what
exactly · how long it takes.**

> Ariel | רוצה להגיע לחוקר ב־OpenAI סביב research collaboration ספציפי | אין
> לנו path אחר כרגע | צריך intro אחד מאבישג | זמן נדרש: כ־3 דקות

If you cannot fill all five, it does not belong here — it belongs to him (§14).
Anything that is follow-up, scheduling, understanding what someone needs,
keeping in touch, or an intro he can make himself is not an Avishag item.

### This Week — the 3–5 calls

Straight from `call-schedule.csv` for the coming week, with the **purpose**,
not the calendar entry. Never "Coffee with Tom":

> Tom | להבין אם הוא באמת מתכנן להקים השנה, האם החסם הוא co-founder והאם נכון
> לחבר אותו ל־X

Sharpen the schedule's default purpose with anything the roster now knows.

---

# Mode B — Thursday report (§17, §21)

Subject: `דוח שבועי · <date>`

### The KPI table

Week and month columns, targets from `network.yaml`. Count from the data, never
estimate:

| Source of truth | KPI |
|---|---|
| `logs/calls/` this week | meaningful conversations |
| `logs/roster-log.md` | alumni with updated info |
| offers accepted in `logs/calls/` | quality connections made |
| `notes` recording an outcome | connections that led to an outcome |
| `can_help` acted on | alumni who helped another alum |
| office-hours roster | contributors |
| `location` = SF, new rows | new SF relationships |
| roster-log `last_source` transitions | relationships moved from Avishag to Nadav |
| the briefing's "Avishag Needed" | things that genuinely required her |

**A number you cannot source is left blank with a dash**, not estimated. Say
plainly when a KPI has no data behind it yet — several will not, early on, and
a fabricated trend line is worse than an honest gap.

Note the framing every time: not every number rises every week; we are looking
for **trend and quality**.

### Dependency (§18)

> 87% טופל עצמאית | 3 נושאים הועלו להחלטה | חיבור אחד דרש את אבישג

Denominator is every item handled this week; numerator is those closed without
her. 100% is not the goal.

### The funnel (§19)

Counted off `tie_strength`:

```
97 Alumni → N Engaged → N Helped → N Contributors → N Nodes
```

Far more meaningful than "I did 17 calls" — and early on it will look thin.
Report it thin. It is the baseline the whole year is measured against.

### Connection quality (§20)

Of the introductions made: how many went to a second conversation, a
collaboration, a job, a design partnership, and how many went nowhere. This
needs a tail before it means anything — say so until it does.

### The three lines (§21)

- **מה למדתי** — what did I learn about our people this week? A pattern, not a
  list. *"שלושה מהבוגרים החזקים של Cohort 2 חושבים על founding, ואצל כולם החסם
  הוא co-founder."*
- **מה אני ממליץ** — what should APEX do about it? *"ארוחת ערב קטנה של שמונה
  potential founders, לא עוד אירוע רחב."* Never bring a problem without a
  recommendation (§22).
- **מה אני צריך מאבישג** — max three. Zero is better.

---

## Voice

Follow `config/voice.md`. Hebrew, informal-direct, feminine forms for Avishag,
signs **דלג׳ו**. Brand and jargon terms stay in English mid-Hebrew — co-founder,
office hours, KPI, SF. Do not formalise it.

These are longer than his usual mail because the format demands it — that is
fine. Keep each *line* short.

## Never

- Never send. Drafts only.
- Never estimate a KPI. A dash and a note beats a plausible number — this goes
  to the person the number is about.
- Never put more than three items in a capped section. The caps are the point:
  five things she must know, not everything that happened.
- Never use the briefing to report activity. It exists so the meeting does not
  have to (§22).
- Never invent a risk or an opportunity to fill a section. Empty is a finding.
