---
name: runner
description: One scheduled pass over new mail — triage what arrived since the last run, suggest calendar events, add Google Tasks, and save reply drafts. Runs four times a day on a Routine. Use when the scheduled runner fires, or when the user asks to run the runner, do a scheduled pass, or catch up on what came in since last time.
---

# Scheduled runner

Four passes a day over what actually arrived since the last one. Each run ends
with three outputs: **calendar events suggested** (never created), **Google
Tasks added**, **drafts saved**.

The whole point is that the four runs feel like one assistant rather than four
duplicate ones. Read the state rules before anything else.

## Ground truth

- `config/workstreams.yaml` — routing table, people, disambiguation rules.
- `config/voice.md` — how the user writes.
- `.claude/skills/triage/SKILL.md` — classification procedure.
- `.claude/skills/draft/SKILL.md` — drafting procedure.

Gmail, Calendar and Zapier tool names carry a server-id prefix that changes
between sessions. Resolve them with ToolSearch every run; never hardcode one.

## State — read this before touching anything

There is no memory between runs. A fresh session fires each time, so the
mailbox itself is the state store. Three guards, all of them required:

1. **The `Runner/Handled` label.** Every thread you finish acting on gets it.
   Create the label if it does not exist. It is what stops run #2 from
   re-drafting everything run #1 already did.
2. **Existing drafts.** Before drafting on a thread, call `list_drafts` and
   check whether one already sits on that `threadId`. If it does, leave it
   alone — never stack a second draft on the same thread.
3. **Existing tasks.** Before adding a task, list the target list and skip
   anything with a matching title.

If any guard is unavailable, do less rather than more. A duplicate draft on a
live thread with a funder is worse than a missed one.

## Step 1 — candidate set

```
in:inbox is:important newer_than:1d -label:Runner/Handled
```

One day of overlap with the label as the real filter, so nothing slips through
a gap between runs and nothing gets handled twice. Never widen to `is:unread` —
tens of thousands of threads sit unread and that is not a work queue.

If the set is empty, stop. Report "nothing new" and do nothing else. A quiet
run is a correct run — do not go looking for work to justify the pass.

## Step 2 — triage

Follow the triage skill. Classify by workstream, assign a state
(`needs-reply` / `waiting-on` / `route` / `fyi` / `noise`), rank.

The rules that matter most here:
- Hardware, GPU, data-centre and quoting topics are **Tinu**, whatever address
  they came from.
- Avishag is not a routing signal — decide Apex vs VelocityX on content.
- Newsletters are `noise`. Never mark one important; `is:important` scopes
  every future run and polluting it breaks the next one.

## Step 3 — suggest calendar events (do NOT create them)

Creating an event sends invitations to other people. That is an outward-facing
act the user has not delegated, so the runner **proposes and stops**.

Read the calendar for the relevant days first, so a suggestion accounts for
what is already booked. Suggest an event only when the mail contains a real
commitment:

- an agreed meeting with no invite yet
- a deadline that needs blocked working time before it
- a site visit, a delivery, a travel date someone stated

Each suggestion, one line: **what · when · who · which thread**. Include the
timezone whenever the counterpart is not on Israel time — Tinu counterparts run
US Pacific.

Never suggest an event for a date you inferred. If the thread says "next week"
and nothing more, say so instead of picking a day.

## Step 4 — add Google Tasks

Google Tasks runs through the Zapier MCP (`GoogleTasksCLIAPI`, action `task`).
One list per workstream, matching the Gmail labels:

| List | For |
|---|---|
| `Velocity + Apex` | both companies, they are run together |
| `Tinu` | hardware, GPU, buildout, quotes |
| `Personal` | everything else |

Create a list only if it is missing. For each task:

- **Title**: the action, starting with a verb. "Reply to Amizur on UPS pricing",
  not "Amizur email".
- **Notes**: one line of context plus the Gmail thread link
  (`https://mail.google.com/mail/u/0/#inbox/<threadId>`).
- **Due**: only when the thread states a real date. Never invent one.

**Cap: five tasks per run.** If more qualify, take the top five by the triage
ranking and say how many you left. A task list nobody can face is the same as
no task list.

## Step 5 — save drafts

Follow the draft skill in full — the voice profile is not optional, and a draft
that needs rewriting is worse than none.

- `needs-reply` and `route` items only.
- Never send. Drafts only, always.
- Never invent a figure, date or commitment. Use `[[NADAV: ...]]` markers.
- **Cap: five drafts per run**, highest-ranked first.

## Step 6 — label and report

Apply `Runner/Handled` to every thread you acted on or judged noise, plus the
workstream label (`Velocity + Apex` or `Tinu`) where it is missing.

Then report, short:

```
Runner 12:00 · 6 new threads

Calendar (suggested, not created)
• Bezeq site visit · Mon 24.8 · Amizur · thread abc123

Tasks added (3)
• Tinu — Reply to Amizur on UPS pricing
• Velocity + Apex — Send Avishag the SF October list

Drafts saved (2)
• Amizur — asks what connects the first set until Bezeq lands
• Gilad @ Joulix — reopens the quote after 31 days

Set aside: 14 newsletters.
```

Nothing else. No preamble, no "I hope this helps". If a run produced nothing,
one line saying so is the entire report.

## Never

- Never send mail, accept an invite, or create a calendar event.
- Never trash, spam, or mark-read anything.
- Never mark a newsletter important.
- Never stack a second draft on a thread that already has one.
