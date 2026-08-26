---
name: draft
description: Write Gmail replies and forwards in the user's own voice for Apex, VelocityX, Tinu or personal threads — bilingual Hebrew/English, short, saved as drafts and never sent. Use when the user asks to draft, reply to, answer, respond to, or forward an email, or says to clear the replies coming out of a triage run.
---

# Drafting in the user's voice

Turn a triaged thread into a draft the user can send with one glance and no
editing. The bar is: it reads as if they wrote it, so it does not need rewriting.

## Before you start

Read `config/voice.md` — the voice profile, taken from real sent mail. Read
`config/workstreams.yaml` for who the recipient is and which workstream's norms
apply. Load the Gmail tools via ToolSearch (`create_draft`, `reply`,
`update_draft`, `get_thread`); the server-id prefix changes between sessions.

## Step 1 — read the whole thread

`get_thread` with `PLAIN_TEXT`. Read every message, not the snippet. You need:

- What is actually being asked, and by when.
- What the user has already committed to earlier in the thread — a draft that
  contradicts or re-promises something is worse than no draft.
- The thread's language, and the recipient's gender for Hebrew verb forms.

If the thread references a document, a deck, or a prior meeting you cannot see,
say so rather than writing around the gap.

## Step 2 — decide the shape

| Situation | Shape |
|---|---|
| Belongs to Avishag or Ken | A **bare forward**, no covering note. This is the house style — see `voice.md`. Add one line only if there is a real instruction. |
| A direct question | One or two lines. Answer, then stop. |
| A scheduling ask | Propose concrete times. For Tinu, remember counterparts are on US Pacific and the user is on Israel time — offer slots that work for both and name the timezone. |
| An intro request | Two lines: who and why. Never send an intro without checking the thread shows the user actually agreed to make it. |
| Anything needing facts the user has not given you | Do not write it. See Step 4. |

## Step 3 — write it

Follow `config/voice.md` exactly. In practice this means:

- Open on the point. No "hope you're well", no restating their message.
- One to four lines. If the draft is longer, the thread probably needs a call,
  and saying that is often the better draft.
- Hebrew signs **דלג׳ו**; English signs **Delgo** or nothing on a short reply.
- Keep brand and jargon terms in English inside Hebrew text.
- Hand decisions back rather than closing them: "כמובן שמה שאת מרגישה".
- Do not over-polish Hebrew into formal register — that is the clearest tell of
  a machine-written draft.

## Step 4 — never invent

No date, number, price, commitment, or promise that is not already in the
thread or given by the user in this session. When the reply depends on
something only the user knows, leave an explicit marker and tell them:

```
[[NADAV: confirm the delegation headcount]]
```

A draft with a marker is fine. A draft with a plausible-sounding invented
figure is a real problem — this mail goes to funders, founders and government
offices.

## Step 4b — if the draft agrees a time, say so

When a draft proposes or accepts a specific date and time, add a one-line
calendar suggestion beside it in the report: what · when · who. The user is
about to commit to a slot, and the entry should not wait for a later pass.

Suggest only — never create the event, and never suggest a time the thread did
not actually put on the table. Add it as a Google Task too, same as triage —
see `calendar_suggestions` in the config — so it does not depend on the user
seeing this particular reply.

## Step 5 — save, never send

Create a **draft** on the thread. Never call a send tool. Never send.

After saving, report per draft in two lines: who it goes to, and the first line
of what it says. The user reviews in Gmail. If they want a change, use
`update_draft` on the same draft rather than stacking new ones.

When drafting a batch out of a triage run, do the highest-ranked items first
and report as you go, so the user can redirect before you write ten of them.

## Sensitive threads

Anything involving money, legal commitments, personnel, or government
paperwork: draft it, then say plainly that it is worth reading closely before
sending. Do not soften a hard message into vagueness — write what the user
means and flag it.
