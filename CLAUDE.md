# Gmail Agent — multi-company orchestrator

Nadav Delgo runs three work contexts out of one Gmail account
(`nadav.delgo@gmail.com`), plus personal mail:

- **Apex** — nonprofit / community organization, Hebrew-first (`apex.org.il`)
- **VelocityX** — venture fund (`velocityx.vc`)
- **Tinu** — GPU / data-centre hardware with Ken Hu: DGX B300 procurement,
  an Israeli buildout, and quoting compute to customers (`tinu.ai`)
- **Personal** — everything else

Apex and VelocityX are run **together** and share staff — most notably Avishag,
who mails from both domains about either company. They are reported as one
section; Tinu and personal are separate.

## Layout

| Path | What it is |
|---|---|
| `config/workstreams.yaml` | Routing table: domains, people, topics, disambiguation rules, label names. Source of truth. |
| `config/voice.md` | How the user writes, observed from real sent mail. |
| `config/network/network.yaml` | The **people** table: tiers, call cadence, the matching gate, KPI definitions, the standing Apex projects. Source of truth. |
| `config/network/roster.csv` | 97 Apex alumni — what each needs, can give, and what happens next. |
| `plan/2026-2027/` | The Apex yearly plan and the dated call rotation. |
| `.claude/skills/triage/` | `/triage` — classify and rank the inbox by workstream. |
| `.claude/skills/draft/` | `/draft` — write replies and forwards in his voice. |
| `.claude/agents/orchestrator.md` | Full pass: triage → checkpoint → draft. |
| `.claude/skills/runner/` | The scheduled 8×/day pass: mail + WhatsApp exports → calendar suggestions → Google Tasks → drafts. |
| `.claude/skills/deal-tracker/` | Standing instruction: every Ken chat, and every Amizur mail, updates the GPU Compute Deal Tracker. |
| `.claude/skills/avishag-register/` | Weekly refresh of the task register shared with Avishag. |
| `.claude/skills/call-log/` | `/call-log` — a call summary becomes a roster update plus a follow-up draft carrying real intro offers. |
| `.claude/skills/network-sync/` | Daily: Avishag's mail and WhatsApp exports update the alumni roster. |
| `.claude/skills/weekly-brief/` | The Sunday briefing to Avishag and the Thursday KPI report. |
| `plan/2026-2027/routine-prompts.md` | The two weekly Routines — they live in the claude.ai UI, not in this repo. |
| `plan/2026-2027/briefs/` | Each week's briefing and report, as written. |

## Working rules

- **The config is the source of truth.** Never classify from memory. When
  routing turns out wrong, fix `workstreams.yaml` rather than special-casing.
- **Draft, never send.** Every outgoing message is saved as a Gmail draft for
  the user to review and send.
- **Never invent facts.** No dates, figures, or commitments not already in the
  thread. Leave `[[NADAV: ...]]` markers instead.
- **Bilingual.** Hebrew and English both, matching the thread. Hebrew signs
  `דלג׳ו`; English signs `Delgo`. Do not formalize the Hebrew.
- **Gmail MCP tool names carry a server-id prefix that changes between
  sessions.** Resolve them with ToolSearch; never hardcode the prefix.
- **Scope the mailbox.** ~45k threads sit unread in the inbox — "unread" is not
  a work queue. Default candidate set is
  `in:inbox is:important newer_than:14d`.
- **Read-only by default.** No trashing, no marking read, no spam. Labelling
  touches the live mailbox, so offer it rather than assuming.
- **Two labels, not four.** `Velocity + Apex` and `Tinu`. Personal threads are
  marked IMPORTANT instead. Never mark a newsletter important — `is:important`
  is what scopes every triage run, and polluting it breaks the next one.
- **Hardware topics are Tinu** wherever they come from, including Hebrew mail
  from consumer addresses (Amizur Kafri on the buildout).
- **The runner has no memory between runs.** A fresh session fires each time,
  so the mailbox is the state store: the `Runner/Handled` label, plus a
  `list_drafts` check before drafting and a task-list check before adding.
  Without those guards four runs a day produce four copies of everything.
- **A date agreed anywhere becomes a calendar suggestion, immediately.** Mail,
  a WhatsApp export, a pasted thread, a deal-tracker update — if the source
  says a date and time were agreed and there is no calendar entry, surface it
  in that same reply. Do not wait for a scheduled runner pass; the runner is a
  safety net, not the only path.
- **Suggest calendar events, never create them.** Creating an event mails
  invitations to other people — that is outward-facing and not delegated.
  Read the calendar first so a suggestion accounts for what is already booked,
  and never suggest a date that was inferred rather than stated.
- **A suggestion is not real until it's a Google Task.** A date mentioned only
  in a chat reply disappears the moment that session ends — the runner alone
  fires 8x/day as fresh sessions, each producing output nobody may ever open.
  Every calendar suggestion also becomes a Task in the matching workstream
  list (see `calendar_suggestions` in `config/workstreams.yaml`), so there is
  one durable place to check it. Dedupe by who+when before adding; the user
  dismisses a suggestion by deleting the task.
- **Every Ken chat, and every Amizur mail, updates the deal tracker.** A chat
  with Ken or a group he is in routes to whichever row matches; anything from
  Amizur Kafri routes to row 10, the Israeli buildout. Both are standing
  triggers — the user does not ask each time. Never write a
  figure Ken did not state, and never overwrite the commercial history in
  `Value / Terms`; it is the audit trail of a live negotiation.
- **Nadav owns Apex's people.** Alongside the mail work he runs the Apex talent
  and alumni network: 97 alumni, 3–4 conversations a week, on a dated rotation
  in `plan/2026-2027/call-schedule.csv`. `config/network/roster.csv` is the
  source of truth for people — never answer "what is X doing now" from memory.
- **The two weekly briefs follow Avishag's templates verbatim.** §16 on Sunday,
  §17/§21 on Thursday — same sections, same order, same caps. The structure is
  hers; what this repo supplies is the content. And the content is built from
  the week's correspondence on **both** her addresses
  (`avishag@apex.org.il` and `avishag@velocityx.vc`), not from the roster
  alone. VelocityX mail reaches a brief only when it carries a person, an
  opportunity or a risk — a deal thread with no human in it is not a Top Person.
- **The weekly Routines live in the claude.ai UI, not in this repo.** Attaching
  connectors to a Claude Code trigger is blocked for this organisation, so a
  Routine fired from here has no Gmail and would produce nothing. The prompts
  to paste are in `plan/2026-2027/routine-prompts.md`.
- **Every call summary updates the roster and produces a draft.** A summary
  pasted, uploaded or forwarded is a standing trigger for `/call-log` — the
  user does not ask each time. The row gets a `next_action` or the call did not
  land; §7's "a database without a next action is just a contact list".
- **Mail with Avishag and every chat export are people sources, not just task
  sources.** They carry most alumni news. `/network-sync` extracts it daily.
  Parse chat exports with `scripts/parse_chat.py`, never by reading the file —
  Hebrew exports carry invisible RTL marks that make a naive read collapse the
  whole file into one message.
- **Second-hand facts are labelled and verified.** Anything relayed by Avishag
  or overheard in a group is written with its source and generates a
  verification action. Never record it as though the user learned it himself.
- **No introduction without a "why now".** Before proposing a connection, be
  able to say why these two people need to know each other *now*. No answer, no
  offer — zero offers is a correct outcome. And the email always offers, never
  announces: "רוצה שאחבר?", never "חיברתי אותך". The other side has not agreed.
- **Never add a person, change a tier or change a tie strength unasked.** Who
  counts as Apex's people, and how strong a relationship is, are the user's
  judgement calls. Propose them in the report.
- **WhatsApp is read-only, and manual.** No API reads personal chats — not
  Meta's Business Platform, not any MCP connector. The supported path is
  WhatsApp's own "Export chat" into the Drive folder named in
  `config/workstreams.yaml`. Never reply into WhatsApp; never use an
  unofficial client.
