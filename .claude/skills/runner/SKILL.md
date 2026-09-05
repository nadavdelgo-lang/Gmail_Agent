---
name: runner
description: One scheduled pass over new mail and WhatsApp exports — triage what arrived since the last run, suggest calendar events, add Google Tasks, and save reply drafts. Runs eight times a day on a Routine. Use when the scheduled runner fires, or when the user asks to run the runner, do a scheduled pass, or catch up on what came in since last time.
---

# Scheduled runner

Eight passes a day over what actually arrived since the last one. Each run ends
with three outputs: **calendar events suggested** (never created), **Google
Tasks added**, **drafts saved**.

The whole point is that the eight runs feel like one assistant rather than
eight duplicate ones. At this cadence most runs should find nothing and say so
in one line — that is the design working, not the runner failing. Read the
state rules before anything else.

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

Two lanes, both run every pass. Lane B is not optional and does not depend on
lane A finding anything.

**Lane A — the general gate:**

```
in:inbox is:important newer_than:1d -label:Runner/Handled
```

One day of overlap with the label as the real filter, so nothing slips through
a gap between runs and nothing gets handled twice. Never widen to `is:unread` —
tens of thousands of threads sit unread and that is not a work queue.

**Lane B — the always-draft correspondents** (`auto_reply` in the config):

```
(from:avishag@apex.org.il OR from:avishag@velocityx.vc) newer_than:3d -label:Runner/Handled
```

Note what is **absent**: no `is:important`. Gmail does not reliably flag
Avishag's mail as important, so the general gate misses most of it — that is
why her threads sat unanswered through August while the runner reported "quiet"
eight times a day. Lane B exists to close exactly that hole. Run it every pass,
even when lane A is empty, and never add `is:important` back to it.

Read every lane-B thread in full with `get_thread` before judging it. Search
previews show only the ~5 **oldest** messages and give no truncation marker, so
a thread that looks open in the preview may already be closed, and one that
looks handled may have a newer message waiting.

If **both** lanes are empty, still check chat sources (step 2b), then stop.
Report "nothing new" and do nothing else. A quiet run is a correct run — do not
go looking for work to justify the pass. Most runs will still be quiet; the
difference is that a quiet run now means quiet, rather than unread Avishag mail.

## Step 2 — triage

Follow the triage skill. Classify by workstream, assign a state
(`needs-reply` / `waiting-on` / `route` / `fyi` / `noise`), rank.

The rules that matter most here:
- Hardware, GPU, data-centre and quoting topics are **Tinu**, whatever address
  they came from.
- Avishag is not a routing signal — decide Apex vs VelocityX on content.
- Newsletters are `noise`. Never mark one important; `is:important` scopes
  every future run and polluting it breaks the next one.

## Step 2b — chat sources (WhatsApp)

Read `chat_sources` in the config. Personal WhatsApp cannot be read by any
API, so the source is a manual export the user drops into the Drive folder
named there (default: `WhatsApp Exports`).

Each run, list that folder and look for files added or modified since the last
pass. For each new export:

- Read it with the Drive tools. The format is WhatsApp's plain-text export:
  `DD/MM/YYYY, HH:MM - Sender: message`, one line per message, continuation
  lines wrapped. Hebrew and English both appear, often in one message.
- Only look at messages newer than the newest one you have already handled.
  The filename usually carries the chat name; use the timestamps inside to
  bound what is new.
- Route the chat to its workstream from the `watched` list. A chat that is not
  listed still gets processed — classify it on content and say it was not in
  the config so the user can add it.

Chat earns its place because **commitments get made there that never reach
email** — a date agreed with Avishag, a price Ken accepted. Pull out exactly
three things and nothing else:

1. commitments made (who owes what, by when)
2. dates and times agreed
3. asks directed at the user that have no answer yet

Do not summarise the conversation. Do not carry gossip, personal remarks, or
anything unrelated into a task or a draft.

**Never reply into WhatsApp.** There is no supported write path, and the user
did not ask for one. Chat is read-only history that feeds tasks and drafts.

When an export contradicts email, the newer source wins — and say which you
used, because an export is stale from the moment it is taken.

## Step 3 — suggest calendar events (do NOT create them)

Creating an event sends invitations to other people. That is an outward-facing
act the user has not delegated, so the runner **proposes and stops**.

Read the calendar for the relevant days first, so a suggestion accounts for
what is already booked. Suggest an event only when the mail contains a real
commitment:

- an agreed meeting with no invite yet
- a deadline that needs blocked working time before it
- a site visit, a delivery, a travel date someone stated
- a time agreed in a WhatsApp export that has no calendar entry

Each suggestion, one line: **what · when · who · which thread**. Include the
timezone whenever the counterpart is not on Israel time — Tinu counterparts run
US Pacific.

Never suggest an event for a date you inferred. If the thread says "next week"
and nothing more, say so instead of picking a day.

**Persist every suggestion as a Google Task**, not just a line in this run's
report — this skill fires 8x/day as a fresh background session, and a
suggestion that only exists in one run's output is invisible unless the user
opens that exact run. Use `calendar_suggestions` in the config: title
`📅 who, when — add to calendar?`, due date the event date, notes with the
thread link. Check the target list first and skip a duplicate who+when. This
task IS the deliverable of this step — the report line is secondary.

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

**Lane B is drafted first, before the cap is spent on anything else.** Every
`auto_reply` thread where her message is the newest and no draft already sits on
that `threadId` gets one. This is a standing instruction — the user does not ask
each time.

The one exception: a thread where *he* is waiting on *her* gets no draft. If his
message is the newest and he asked her something, there is nothing to say yet;
label it and move on. Drafting a nudge to someone who already owes you an answer
is noise, not service.

Her mail is Hebrew — reply in Hebrew, sign `דלג׳ו`, and keep it to the one to
four lines `config/voice.md` describes. Flowing prose, never bullets or bolded
headers in a Hebrew message to her.

## Step 6 — label and report

**Labelling is mandatory and is the last thing that gets skipped, never the
first.** See `labelling` in the config. Every thread you read this run gets its
workstream label before the run ends — not only the ones that produced a draft
or a task:

| Classification | Label to apply |
|---|---|
| Apex or VelocityX | `Velocity + Apex` |
| Tinu — hardware, GPU, buildout, quoting | `Tinu` |
| Personal, genuinely | `IMPORTANT` |
| Noise — newsletters, notifications | nothing, but still `Runner/Handled` |

Then `Runner/Handled` on all of them, including the noise. A thread you read and
left unlabelled is a thread the next run reads again from scratch — that is how
`Runner/Handled` ended up on ten threads while forty thousand sat untouched.

Two rules that are easy to get wrong:

- **Never mark a newsletter `IMPORTANT` to "label" it as personal.** `IMPORTANT`
  is the backbone of lane A; polluting it breaks every future run. Noise gets
  `Runner/Handled` alone.
- **Never apply both workstream labels to one thread.** Pick one. If it is
  genuinely both companies, it is `Velocity + Apex` — that label already means
  both.

Report the label counts alongside everything else, so a run that drafted nothing
still shows it did the filing.

Then report, short:

```
Runner 12:00 · 6 new threads · 1 new chat export (Avishag)

Calendar (suggested → added as Tasks, not created as events)
• Bezeq site visit · Mon 24.8 · Amizur · thread abc123

Tasks added (3)
• Tinu — Reply to Amizur on UPS pricing
• Velocity + Apex — Send Avishag the SF October list

Drafts saved (3)
• Avishag — the questionnaire, confirms he is going through it
• Amizur — asks what connects the first set until Bezeq lands
• Gilad @ Joulix — reopens the quote after 31 days

Labelled (6)
• Velocity + Apex 3 · Tinu 2 · IMPORTANT 1 · Runner/Handled 6

From chat: Avishag agreed Tue 8.9 11:00 with Avital (no calendar entry).

Set aside: 14 newsletters (Runner/Handled, no workstream label).
```

Nothing else. No preamble, no "I hope this helps". If a run produced nothing,
one line saying so is the entire report.

## Never

- Never send mail, accept an invite, or create a calendar event.
- Never reply into WhatsApp, and never move chat content into a task or draft
  unless it is a commitment, a date, or an unanswered ask.
- Never trash, spam, or mark-read anything.
- Never mark a newsletter important.
- Never stack a second draft on a thread that already has one.
