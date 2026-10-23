# Scheduled tasks

Every scheduled task on the account, live or dead, with its cron, timezone,
connector state and full prompt text. Captured 23 Oct 2026.

**All five are currently disabled.** They were switched off on 6 Sep 2026.

## The two faults to carry across

**1. Four of the five have no connectors attached.** Only the Spanish task
lists any. A task with no Gmail connector cannot read mail or create a draft —
so the 8×/day runner was firing on schedule and reporting success while
structurally unable to draft anything. This is a second, independent cause of
"the agent stopped answering mail", alongside the `is:important` gate. When
rebuilding in a Project, attach Gmail, Calendar, Drive and Sheets explicitly
and verify with one manual run before trusting the schedule.

**2. Every prompt below opens with a `STEP ZERO ... git checkout`.** That
existed only because the repository had no trunk and a scheduled session
cloned a default branch missing most of the inputs. The consolidation removed
the cause. **Delete those blocks when rebuilding** — in a Project they are
meaningless, and left in they will make the task fail looking for a branch.

## Timezone

All crons below are **UTC**. Israel is UTC+3 in summer and UTC+2 in winter, so
`0 5` is 08:00 local from late March to late October and 07:00 otherwise.
Set the timezone explicitly when rebuilding rather than hand-converting.

---

## 1. Inbox + chat runner — 8× daily

| | |
|---|---|
| ID | `trig_01DkkfWeXDk26CTtm8tenKax` |
| Cron | `0 1,4,7,10,13,16,19,23 * * *` (UTC) |
| Local | 04:00, 07:00, 10:00, 13:00, 16:00, 19:00, 22:00, 02:00 Israel summer |
| State | disabled 6 Sep 2026 · last fired 6 Sep 19:02 UTC, succeeded |
| Connectors | **none** |
| Notifications | push on, email off |
| Session | fresh per firing |

The odd hours are deliberate: he works at 02:00 and 04:00 and asked for the
schedule to cover them.

### Prompt

```
Run one scheduled pass over mail and chat for Nadav Delgo (nadav.delgo@gmail.com).

Follow `.claude/skills/runner/SKILL.md` in this repo exactly — read it first, along with `config/workstreams.yaml` (routing, `auto_reply`, `labelling`, chat sources) and `config/voice.md` (how he writes). Do not classify or draft from memory; the config is the source of truth.

Resolve Gmail, Google Calendar, Google Drive and Zapier tool names with ToolSearch — their server-id prefixes change between sessions, so never assume one.

STEP 0 — THE GATE. Two lanes. Run BOTH every pass. Lane B does not depend on lane A finding anything.

Lane A, the general gate:
    in:inbox is:important newer_than:1d -label:Runner/Handled

Lane B, Avishag, who is drafted for automatically as a standing instruction:
    (from:avishag@apex.org.il OR from:avishag@velocityx.vc) newer_than:3d -label:Runner/Handled

Note what is absent from lane B: no `is:important`. Gmail does not reliably flag her mail important, so the general gate misses most of it — that is why her threads sat unanswered through August while this runner reported "quiet" eight times a day. NEVER add `is:important` to lane B. Use label display names, never IDs: `-label:Runner/Handled` excludes correctly, `-label:Label_5` silently excludes nothing.

Read every lane-B thread in full with `get_thread` before judging it. Search previews show only the ~5 OLDEST messages with no truncation marker, so a thread that looks open may already be closed and one that looks handled may have a newer message waiting.

If BOTH lanes are empty, make one more check: list the Drive folder named in `chat_sources` for an export added since the last pass. If that is empty too, STOP. Report one line — `Runner HH:MM · nothing new` — and end. A quiet run is the design working. Never widen a query to find work.

Only if something opened, run the pass:

1. Triage by workstream: Apex and VelocityX together, Tinu, Personal. Hardware/GPU/data-centre/quoting topics are Tinu whatever address they came from. Avishag mails from both domains, so route her on content, never on sender.

2. Chat sources: read any export added or modified since the last pass. Pull out only commitments made, dates agreed, and unanswered asks directed at him. Do not summarise conversations, and never reply into WhatsApp — read-only history. If mail and an export cover the same thing, the newer wins; say which you used.

3. SUGGEST calendar events — never create them. Creating an event mails invitations to other people, which is not delegated. Include times agreed in chat that have no calendar entry. Persist each as a Google Task, since a suggestion that lives only in one run's report is invisible.

4. Add Google Tasks (Zapier, GoogleTasksCLIAPI, action `task`) to the list matching the workstream: "Velocity + Apex", "Tinu", or "Personal". Max 5 per run.

5. DRAFTS. Lane B is drafted FIRST, before the cap is spent on anything else. Every Avishag thread where her message is the newest and no draft already sits on that threadId gets a draft — he does not ask each time, this is standing. Her mail is Hebrew: reply in Hebrew, sign דלג׳ו, one to four lines, flowing prose, never bullets or bolded headers. The one exception: a thread where HE is waiting on HER gets no draft — if his message is the newest and he asked her something, there is nothing to say yet, so just label it. Never send. Max 5 drafts per run. No invented dates, figures or commitments — leave [[NADAV: ...]] markers.

6. LABELLING IS MANDATORY and is the last thing to skip, never the first. Every thread you read this run gets its workstream label before the run ends, not only the ones that produced a draft or a task:
   - Apex or VelocityX  -> "Velocity + Apex"
   - Tinu               -> "Tinu"
   - Personal, genuinely -> IMPORTANT
   - Noise (newsletters, notifications) -> no workstream label, but still Runner/Handled
   Then Runner/Handled on all of them, including the noise. A thread read and left unlabelled is re-read from scratch next run — that is how Runner/Handled ended up on 10 threads while 44,000 sat untouched. Never mark a newsletter IMPORTANT to "label" it personal: IMPORTANT is the backbone of lane A and polluting it breaks every future run. Never put both workstream labels on one thread; if it is genuinely both, it is "Velocity + Apex".

State guards, all required — a fresh session fires each time, so the mailbox and Drive are the only memory:
- Skip threads already carrying Runner/Handled.
- Call list_drafts before drafting and never stack a second draft on a thread that already has one.
- Check the task list before adding, and skip duplicate titles.
- Only read chat messages newer than ones already handled.

Never send mail, accept an invite, create a calendar event, reply into WhatsApp, trash, mark read, or mark a newsletter important.

Report short: counts, then one line per calendar suggestion, task and draft, plus a label-count line so a run that drafted nothing still shows it did the filing. Do not manufacture work to fill the report.
```

---

## 2. Avishag task register — weekly refresh

| | |
|---|---|
| ID | `trig_01HWi5wYhVB2iFFcaRgdLV2a` |
| Cron | `0 6 * * 0` (UTC) — Sunday |
| Local | 09:00 Israel summer |
| State | disabled 6 Sep 2026 · last fired 6 Sep 06:07 UTC, succeeded |
| Connectors | **none** |

### Prompt

```
Refresh the Apex + VelocityX task register that Nadav Delgo (nadav.delgo@gmail.com) keeps with Avishag Bohbot.

Follow `.claude/skills/avishag-register/SKILL.md` in this repo exactly — read it first, along with `config/workstreams.yaml` (routing) and `config/voice.md` (how he writes). Resolve Gmail and Google Calendar tool names with ToolSearch; their server-id prefixes change between sessions.

In short:
1. `list_drafts` and find the draft with subject "אפקס + Velocity — כל המשימות בינינו במקום אחד". Update it in place with `update_draft`. Never create a second register — if the draft is gone but a sent message with that subject exists, he sent it: start a fresh one covering only what changed since, and say so.
2. Re-read `(from:avishag OR to:avishag) newer_than:14d` with `get_thread` in full — search previews hide newer messages and will make you miss the reply that closed an item. Also pick up anything from team@apex.org.il that assigns either of them an action.
3. Reconcile rather than rebuild. Items answered in the past week move to נסגר and keep their line. Items still open stay. Items he pinged again with no reply get the waiting time marked — that is the most valuable part of the register. Never silently drop a line.
4. Only track things with an owner and an outcome: an unanswered ask, a commitment, a decision waiting on someone, a name or document one owes the other. Not FYIs or forwards.
5. Any date agreed in the week's mail with no calendar entry comes out as a calendar SUGGESTION in the report — suggest, never create, since creating an event mails invitations to other people. Dates do not go in the register itself.
6. Never send. Never invent an item, a date or an owner — if a thread is ambiguous about who owes what, say so instead of assigning it.

Report only what moved: counts, what closed, what is new, what is still waiting and for how long. If nothing moved, say that in one line and leave the draft untouched.
```

---

## 3. APEX — Sunday briefing to Avishag

| | |
|---|---|
| ID | `trig_01Uu11zHda7UFY6HoPRMMqaV` |
| Cron | `0 5 * * 0` (UTC) — Sunday |
| Local | 08:00 Israel summer |
| State | disabled 6 Sep 2026 · last fired 6 Sep 05:04 UTC, succeeded |
| Connectors | **none** — and the prompt itself names this as the reason it had to write a file instead of a draft |

### Prompt

```
Produce Nadav Delgo's **Sunday briefing to Avishag** for APEX, per the
/weekly-brief skill. It goes out before their Monday people review, so the
meeting is spent on judgement and decisions rather than transferring information.

STEP ZERO, BEFORE ANYTHING ELSE. Get onto the branch that holds this work. The
repo's default branch (claude/multi-company-orchestrator-agent-wbahy5) does NOT
contain the roster, the network config, the call schedule or the weekly-brief
skill. They live on a feature branch. Without this you will find nothing.

    git fetch origin claude/apex-velocity-yearly-plan-tv5ru8
    git checkout claude/apex-velocity-yearly-plan-tv5ru8

Then verify `config/network/roster.csv` exists and has 97 data rows. If it does
not, STOP and report that the checkout failed. Do not improvise a briefing from
memory: a fabricated briefing to Avishag is far worse than no briefing.

Now read these; they are the source of truth:
- .claude/skills/weekly-brief/SKILL.md — the procedure and the §16 format
- config/network/network.yaml — reporting block, tiers, cadence, KPI definitions
- config/network/roster.csv — the 97 alumni
- plan/2026-2027/call-schedule.csv — the rotation
- logs/roster-log.md — what changed about people this week
- config/voice.md — how he writes: Hebrew, informal-direct, feminine forms for
  Avishag, signs דלג׳ו, brand terms in English, never formal register

HOUSE STYLE, set by Nadav and non-negotiable:
- No date references in the body. Relative time only ("השבוע", "בימים הקרובים").
  A deadline keeps its urgency and loses its number; give the number to him in
  the chat report instead so it is not lost.
- No en dash and no em dash anywhere, including inside table cells. The Hebrew
  maqaf is fine.
- Every Apex alum's name is a hyperlink on the name itself, pointing at the
  `linkedin` column of their roster row. Never a bare URL in a sentence. A name
  with no LinkedIn on file goes in unlinked with a [[NADAV: ...]] asking for it.

Establish what tools you actually have. Call ToolSearch for "gmail create draft"
and "fireflies transcripts". Connector tool names carry a server-id prefix that
changes between sessions, so resolve them every run and never hardcode one.

- **If Gmail tools are available**: leave the briefing as a Gmail DRAFT to
  avishag@apex.org.il, subject "בריפינג שבועי, אנשים". Check list_drafts first
  and update this week's draft in place rather than stacking a second. NEVER send.
- **If Gmail tools are NOT available**: do not fail silently. Produce the
  identical briefing, save it to logs/briefs/YYYY-MM-DD-sunday.md, commit and
  push on the branch you checked out. Then say clearly that no Gmail draft was
  created because this Routine has no Gmail connector, and that the fix is to
  recreate it from the claude.ai Routines UI with Gmail attached.

Step 0 of the skill, before writing anything:
1. The week's correspondence with Avishag across BOTH her addresses
   (avishag@apex.org.il and avishag@velocityx.vc), plus anything from
   team@apex.org.il that assigns either of them something. Read every thread in
   full with get_thread; previews hide the newest message, which is usually the
   one that matters. The template is the filter: VelocityX mail reaches the
   briefing only when it carries a person, an opportunity or a risk.
2. Real call summaries someone typed, not notifications.
3. Fireflies: transcripts for the last 7 days, then the summary per meeting.
   Check Summary Status; "skipped" means nothing was generated, and a very short
   meeting returning single words is not a summary of anything.
4. The roster's last_contact and next_action, and the Call Schedule status column.

Then the §16 briefing, caps enforced because the caps are the point:
Top People (max 5, format "שם | Cohort | מה השתנה | מה הם צריכים | מי מטפל"),
Opportunities (max 3, each with a why now), Risks and Weak Signals (max 3),
מה אני צריך ממך (max 3, ideally zero, each carrying מי / למה עכשיו / למה דווקא
היא / מה בדיוק / כמה זמן), and השבוע, the coming week's calls from the schedule
with the purpose of each rather than the calendar entry.

Compute the risks rather than recalling them: a tier-A alum whose last_contact is
older than their cadence is exactly §16's "בוגר חזק שלא היה בקשר חמישה חודשים".

Hard rules: never send. Never invent a person, number, risk or opportunity to
fill a section. An empty section is a finding, and if the week produced no logged
calls, say so in one line rather than dressing it up.

Finish with a short chat report: which branch you ended up on, what went into the
briefing, what was left empty for lack of data, and whether a Gmail draft was
created or a file was written instead.
```

---

## 4. APEX — Thursday weekly report + KPIs

| | |
|---|---|
| ID | `trig_01QodELhUzm9Fm17NcMm3Yiw` |
| Cron | `0 5 * * 4` (UTC) — Thursday |
| Local | 08:00 Israel summer |
| State | disabled 6 Sep 2026 · last fired 3 Sep 05:07 UTC, succeeded |
| Connectors | **none** |

### Prompt

```
Produce Nadav Delgo's **Thursday weekly report** for APEX, per the /weekly-brief skill.

STEP ZERO, BEFORE ANYTHING ELSE. Get onto the branch that holds this work. The
repo's default branch (claude/multi-company-orchestrator-agent-wbahy5) does NOT
contain the roster, the network config, the call schedule or the weekly-brief
skill. They live on a feature branch. Previous runs of this Routine skipped this,
found nothing, and ended having produced nothing at all.

    git fetch origin claude/apex-velocity-yearly-plan-tv5ru8
    git checkout claude/apex-velocity-yearly-plan-tv5ru8

Then verify `config/network/roster.csv` exists and has 97 data rows. If it does
not, STOP and report that the checkout failed. Do not improvise a report from
memory: a fabricated report to Avishag is far worse than no report.

Now read these; they are the source of truth:
- .claude/skills/weekly-brief/SKILL.md — the procedure and the §17/§21 format
- config/network/network.yaml — reporting block, KPI targets, tiers, cadence
- config/network/roster.csv — the 97 alumni
- plan/2026-2027/call-schedule.csv — the rotation
- logs/roster-log.md and logs/calls/ — what actually changed this week
- config/voice.md — how he writes: Hebrew, informal-direct, feminine forms for
  Avishag, signs דלג׳ו, brand terms in English, never formal register

HOUSE STYLE, set by Nadav and non-negotiable:
- No date references in the body. Relative time only ("השבוע", "בימים הקרובים").
  A deadline keeps its urgency and loses its number; give the number to him in
  the chat report instead so it is not lost.
- No en dash and no em dash anywhere, including inside table cells. The Hebrew
  maqaf is fine.
- Every Apex alum's name is a hyperlink on the name itself, pointing at the
  `linkedin` column of their roster row. Never a bare URL in a sentence. A name
  with no LinkedIn on file goes in unlinked with a [[NADAV: ...]] asking for it.

Establish what tools you actually have. Call ToolSearch for "gmail create draft"
and "fireflies transcripts". Connector tool names carry a server-id prefix that
changes between sessions, so resolve them every run and never hardcode one.

- **If Gmail tools are available**: leave the report as a Gmail DRAFT to
  avishag@apex.org.il, subject "דוח שבועי". Check list_drafts first and update
  this week's draft in place rather than stacking a second. NEVER send.
- **If Gmail tools are NOT available**: do not fail silently. Produce the
  identical report, save it to logs/briefs/YYYY-MM-DD-thursday.md, commit and
  push on the branch you checked out. Then say clearly in your report that no
  Gmail draft was created because this Routine has no Gmail connector, and that
  the fix is to recreate it from the claude.ai Routines UI with Gmail attached.

Step 0 of the skill — gather what actually happened: the week's correspondence
with Avishag across BOTH her addresses (avishag@apex.org.il and
avishag@velocityx.vc), read in full with get_thread because previews hide the
newest message; real call summaries someone typed; Fireflies via the connector
(check Summary Status, "skipped" means nothing was generated, and a very short
meeting returning single words is not a summary; the Fireflies recap EMAILS
carry only a link); and the roster's last_contact / next_action plus the Call
Schedule status column.

Then the report:
1. **The KPI table**, week and month, against the targets in network.yaml. Count
   from the data. A number you cannot source is left blank, never estimated. Say
   plainly which KPIs have no data behind them yet. Repeat the framing: not every
   number rises every week, we are looking for trend and quality.
2. **Dependency (§18)** — what share of the week's items closed without Avishag.
   100% is not the goal.
3. **The funnel (§19)** — Alumni, Engaged, Helped, Contributors, Nodes, counted
   off tie_strength. Report it thin if it is thin; it is the baseline the year is
   measured against.
4. **Connection quality (§20)** — of the introductions made, what came of them.
   Say it needs a tail before it means anything, until it has one.
5. **The three lines (§21)** — מה למדתי (a pattern, not a list) · מה אני ממליץ
   (never a problem without a recommendation) · מה אני צריך ממך (max three).

Hard rules: never send. Never estimate a KPI, this goes to the person the number
is about. Never invent activity to fill the format.

Finish with a short chat report: which branch you ended up on, the headline
numbers, which KPIs had no data, and whether a Gmail draft was created or a file
was written instead.
```

---

## 5. Daily Spanish practice content refresh

Not part of this system — recorded only because it exists on the account.

| | |
|---|---|
| ID | `trig_013pCthQTxcAzYzjpKajdGv4` |
| Cron | `30 6 * * *` (UTC) |
| State | disabled 6 Sep 2026 · last run **abandoned** |
| Connectors | Calendar, Spotify, Gmail, Clay, Drive, Zapier, Notion, Fireflies |
| Model | `claude-sonnet-5` |

### Prompt

```
Daily job. Nadav (calendarId nadav.delgo@gmail.com on Google Calendar) has a recurring Spanish-practice event today, titled either "Spanish: video lesson" (Mondays/Thursdays) or "Spanish: Duolingo + ChatGPT" (other days). He is prepping for a Peru/Argentina/Chile trip around February 2027.

1. Find today's event on that calendar with a title starting "Spanish:".
2. Generate 3 NEW Spanish sentences useful for travel in Peru, Argentina, or Chile. Rotate topics day to day so they don't repeat too much: greetings, directions, food and restaurants, lodging, transport, money and bargaining, emergencies, small talk, hiking and outdoors, shopping.
3. For each sentence give: the Spanish sentence, then its Hebrew translation, then its English translation, in that order, separated by " — ".
4. Update that event's description: keep the first two lines (the practice-method instructions) exactly as they are, and replace everything from "Today's 3 sentences:" onward with the 3 new numbered sentences plus the line "(Refreshed daily.)" at the end.
5. If no event titled "Spanish:" exists for today, do nothing and end quietly. Do not ask for confirmation — just update the event.
```

---

## Rebuilding

Four tasks to recreate, not five — the Spanish one is unrelated.

For each: strip the `STEP ZERO` git block, attach Gmail, Calendar, Drive and
Sheets explicitly, set the timezone rather than hand-converting the cron, and
replace every `read file X` instruction with a reference to the corresponding
knowledge document. Run each once by hand and read the output before switching
the schedule on.
