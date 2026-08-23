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
| `.claude/skills/triage/` | `/triage` — classify and rank the inbox by workstream. |
| `.claude/skills/draft/` | `/draft` — write replies and forwards in his voice. |
| `.claude/agents/orchestrator.md` | Full pass: triage → checkpoint → draft. |
| `.claude/skills/runner/` | The scheduled 8×/day pass: mail + WhatsApp exports → calendar suggestions → Google Tasks → drafts. |
| `.claude/skills/deal-tracker/` | Standing instruction: every Ken chat updates the GPU Compute Deal Tracker. |

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
- **Suggest calendar events, never create them.** Creating an event mails
  invitations to other people — that is outward-facing and not delegated.
- **Every Ken chat updates the deal tracker.** A chat with Ken, or a group he
  is in, is a standing trigger — the user does not ask each time. Never write a
  figure Ken did not state, and never overwrite the commercial history in
  `Value / Terms`; it is the audit trail of a live negotiation.
- **WhatsApp is read-only, and manual.** No API reads personal chats — not
  Meta's Business Platform, not any MCP connector. The supported path is
  WhatsApp's own "Export chat" into the Drive folder named in
  `config/workstreams.yaml`. Never reply into WhatsApp; never use an
  unofficial client.
