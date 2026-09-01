---
name: weekly-brief
description: Produce the Sunday briefing to Avishag or the Thursday weekly report for Apex — Top People, Opportunities, Risks, what needs Avishag, the week's calls, the KPI table, the dependency and funnel numbers, and the three closing lines. Built from the week's correspondence with Avishag on both her addresses, plus the roster and the call schedule, and saved as a Gmail draft. Use when the scheduled brief fires, or when the user asks for his weekly briefing, the Sunday brief, the Thursday report, or his KPIs.
---

# Weekly brief

Two reports, one skill. Both are Gmail drafts to Avishag, never sent.

The structure is **not ours to design**. Avishag specified both formats in the
role definition (§16, §17, §21) and the user pasted them back verbatim with
"זאת התבנית". Follow them exactly: same sections, same order, same caps, same
Hebrew. What this skill supplies is the *content* — and the content comes from
the mail, the roster and the schedule, never from memory.

Pick the mode from what he asked for, or from the day: Sunday/Monday → the
briefing; Thursday/Friday → the report. If it is ambiguous, ask.

## Ground truth

- `config/network/network.yaml` — `reporting` holds both formats and every KPI
  target. Read them from there; never retype a number into this file.
- `config/network/roster.csv`, `plan/2026-2027/call-schedule.csv`
- `logs/roster-log.md`, `logs/calls/` — what actually happened this week
- The `avishag-register` draft — the live list of who owes what
- `config/voice.md` — how he writes

Resolve Gmail tool names with ToolSearch every run; the server-id prefix changes
between sessions.

## One living draft

Follow the `avishag-register` discipline. `list_drafts` first:

- **Draft with this week's subject exists** → `update_draft` in place.
- **Already sent** → start a fresh draft for the new week.
- **Neither** → create it.

Never stack two briefings. Two is worse than none.

---

## Step 0 — gather what actually happened

Run this before either mode. It is what stops the brief from being a
restatement of the plan.

### 1. The correspondence with Avishag — both addresses

She runs Apex and VelocityX out of two mailboxes and writes about people from
either. Both are in scope; the user asked for this explicitly.

```
(from:avishag@apex.org.il OR to:avishag@apex.org.il OR
 from:avishag@velocityx.vc OR to:avishag@velocityx.vc) newer_than:7d -in:draft
```

Gmail's `from:avishag` would match the local part and cover both domains — the
addresses are written out anyway so the intent survives a future edit. Add
anything from `team@apex.org.il` that assigns either of them something.

Read every thread in full with `get_thread`. A search preview shows the oldest
messages and hides the reply that carries the news — which is usually the whole
point of the thread.

**The template is the filter.** From each thread take only what maps to a
section:

| What the thread carries | Where it goes |
|---|---|
| a fact about a person | **Top People**, and the roster |
| something newly possible | **Opportunities** |
| something going quiet, or a commitment with no reply | **Risks / Weak Signals** |
| something only she can unblock | **Avishag Needed** |

VelocityX mail is read, but it reaches the brief only when it touches a person,
an opportunity or a risk. A deal thread with no human angle is not a Top
Person — Avishag's template is about people, and padding it with fund business
is how a briefing stops being read. This is the one judgement call in the
skill; when a thread is borderline, leave it out and mention it in the report
back to the user rather than in the mail.

Anything that turns out to be a real roster fact goes through `/network-sync`
first, so the roster is current before the brief reports on it. Second-hand
rules apply in full: a fact Avishag relays about a third party is written with
its source and generates a verification action (`network.yaml` → `extraction`).

### 2. Call summaries the user wrote or was sent

```
(from:me OR to:me) (סיכום OR summary OR "notes from" OR "call with") newer_than:10d
```

Anything that reads as an account of a conversation with an alum is a summary.
Run it through `/call-log` first if the roster has not been updated from it —
the brief reports what the roster knows, so the roster comes first.

### 3. Fireflies

Meeting recordings live there, and the recap mail Fireflies sends is a link
with no content in it — the body is boilerplate, so never try to read a summary
out of the email itself. Use the connector: `fireflies_get_transcripts` for the
window, then `fireflies_get_summary` per meeting.

Two things to check before trusting one:

- **`Summary Status`.** `skipped` means Fireflies generated nothing and the
  "summary" field is empty. Say so rather than reporting silence as calm.
- **Transcript quality.** A short meeting can come back as a handful of single
  words — real audio was not captured. That is not a summary of anything; do
  not extract facts from it.

Match the meeting to a roster row by participant email, then by title. A
meeting whose participants are Tinu or VelocityX counterparties is not alumni
work — the workstream firewall applies here too.

### 4. WhatsApp exports

If the user has uploaded one, it has already been parsed by `/network-sync`
with `scripts/parse_chat.py` and landed in the roster — read the roster, not
the export. Never read an export file directly: Hebrew exports carry invisible
RTL marks that collapse the whole file into one message.

### 5. The roster, the schedule and the register

`last_contact`, `next_action` and the schedule's status column are the record
of what was done. The register draft (subject **אפקס + Velocity — כל המשימות
בינינו במקום אחד**) is the record of what is open.

**When everything comes back empty, the brief says so in one line** and reports
the week from the schedule and the roster alone. An honest "לא נרשמו שיחות
השבוע" is the finding; inventing activity to fill the format is the one thing
this skill must never do.

---

# Mode A — Sunday briefing (§16)

Sent **before** the Weekly People Review, so the hour is spent on people,
opportunities, judgement and decisions — never on transferring information.
That is the entire reason the document exists.

Subject: `בריפינג שבועי — אנשים · <date>`

Sections and caps exactly as specified: **Top People ≤5** · **Opportunities ≤3**
· **Risks / Weak Signals ≤3** · **Avishag Needed ≤3** · **This Week**.

### Top People — up to 5

The people she needs to know about this week. Draw from: this week's
correspondence, rows whose `current_goal` or `needs` changed in the last seven
days (`logs/roster-log.md`), anyone who moved toward founding, and anyone with
a live `next_action` that concerns her.

`שם | Cohort | מה השתנה | מה הם צריכים | מי מטפל`

> דנה | Cohort 2 | עוזבת Meta ומתחילה חברה | מחפשת co-founder טכני | נדב מטפל

The "מי מטפל" clause is the point — it is where the dependency KPI comes from.
Default to "נדב מטפל".

At least one line should trace to a specific thread from the last seven days.
If none does, the sweep did not do its job — go back to Step 0.

### Opportunities — up to 3

An alum starting a company; a significant researcher who wants to connect to
APEX; someone in the SF network willing to give office hours; two alumni it is
right to introduce. Each with the "why now".

### Risks / Weak Signals — up to 3

**Compute these, do not recall them.** The most valuable lines in the document
and the easiest to generate mechanically:

- A tier-A alum whose `last_contact` is older than their cadence — precisely
  §16's "בוגר חזק שלא היה בקשר חמישה חודשים", found by arithmetic rather than
  by remembering.
- Someone we want to keep close who is moving to another organisation.
- A commitment in the correspondence that has gone unanswered for a week.
- A contributor receiving too many requests (§12) — check how often they have
  been proposed in `logs/calls/`.

### Avishag Needed — up to 3, ideally zero

Each one must carry all five: **מי · למה עכשיו · למה דווקא היא · מה בדיוק ·
כמה זמן**.

> Ariel | רוצה להגיע לחוקר ב־OpenAI סביב research collaboration ספציפי | אין
> לנו path אחר כרגע | צריך intro אחד מאבישג | זמן נדרש: כ־3 דקות

If you cannot fill all five, it does not belong here — it belongs to him (§14).
Follow-up, scheduling, understanding what someone needs, keeping in touch, or
an intro he can make himself is never an Avishag item.

### This Week — the 3–5 calls, action items, weekly plan

The calls come straight from `call-schedule.csv` for the coming week, with the
**purpose**, not the calendar entry. Never "קפה עם תום":

> תום | להבין אם הוא באמת מתכנן להקים השנה, האם החסם הוא co-founder והאם נכון
> לחבר אותו ל־X

Sharpen the schedule's default purpose with anything the roster now knows.

**Action items are read from the register draft**, filtered to what is live
this week — do not recompute them. Two lists that disagree are worse than one,
and the register is the one he and Avishag both look at.

---

# Mode B — Thursday report (§17, §21)

Subject: `דוח שבועי · <date>`

### The KPI table

Nine rows, in this order, with week and month columns. Targets come from
`network.yaml` → `reporting.thursday_report.kpis`, read at run time so the
mail and the workbook cannot drift:

| KPI | שבוע | חודש |
|---|---|---|
| שיחות בוגרים משמעותיות | 4 | 15 |
| בוגרים עם מידע מעודכן במערכת | +4 | 72% |
| חיבורים איכותיים שבוצעו | 3 | 11 |
| חיבורים שהובילו לתוצאה | 1 | 5 |
| בוגרים שעזרו לבוגר אחר | 2 | 7 |
| Contributors / Office Hours | +1 | 12/20 |
| קשרים חדשים ב־SF | 1 | 6 |
| קשרים שעברו מאבישג לנדב | 2 | 9 |
| דברים שבאמת דרשו את אבישג | 2 | — |

Those are the **targets**. The actuals are counted from the data:

| KPI | Counted from |
|---|---|
| שיחות בוגרים משמעותיות | `logs/calls/` this week |
| בוגרים עם מידע מעודכן | `logs/roster-log.md` |
| חיבורים איכותיים | offers accepted in `logs/calls/` |
| חיבורים שהובילו לתוצאה | `notes` recording an outcome |
| בוגרים שעזרו לבוגר אחר | `can_help` acted on |
| Contributors / Office Hours | the office-hours roster |
| קשרים חדשים ב־SF | `location` = SF, new rows |
| קשרים שעברו מאבישג לנדב | roster-log `last_source` transitions |
| דברים שבאמת דרשו את אבישג | the briefing's "Avishag Needed" |

**A number you cannot source is a dash, never an estimate.** This mail goes to
the person the numbers are about, and early on most rows will have no data
behind them. Report the gap; a fabricated trend line is worse than an honest
blank.

Carry his framing every week, in his words:
*לא צריך שכל המספרים יעלו כל שבוע. אנחנו מחפשים מגמה ואיכות.*

### Dependency (§18)

> 87% טופל עצמאית | 3 נושאים הועלו להחלטה | חיבור אחד דרש את אבישג

Denominator is every item handled this week; numerator is those closed without
her. 100% is not the goal.

### The funnel (§19)

Counted off `tie_strength`:

```
97 Alumni → N Engaged → N Helped → N Contributors → N Nodes
```

Far more meaningful than "עשיתי 17 שיחות" — and early on it will look thin.
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
office hours, KPI, SF, Cohort. Do not formalise it.

These are longer than his usual mail because the format demands it — that is
fine. Keep each *line* short.

## Never

- Never send. Drafts only.
- Never estimate a KPI. A dash and a note beats a plausible number.
- Never exceed a cap. The caps are the point: five things she must know, not
  everything that happened.
- Never report a fact from the correspondence without having read the thread it
  came from in full.
- Never let a VelocityX deal thread into the brief unless it carries a person.
- Never use the briefing to report activity. It exists so the meeting does not
  have to (§22).
- Never invent a risk or an opportunity to fill a section. Empty is a finding.
