# Gmail Agent

A Claude Code agent that orchestrates email across three companies and personal
life, out of one Gmail account.

## Setup

None. It drives the Gmail connector already attached to the Claude Code
session — no OAuth, no deployment, no credentials in the repo.

## Use

```
/triage        # what needs you, ranked, grouped by company
/draft         # write the replies, in your voice, saved as drafts

/call-log      # a call summary → roster updated, follow-up drafted with real offers
/network-sync  # Avishag's mail + WhatsApp exports → the alumni roster
/weekly-brief  # Sunday briefing to Avishag · Thursday KPI report
```

For a full pass — triage, checkpoint, then draft the top items — ask for the
orchestrator agent.

A Routine runs the same pass automatically eight times a day and adds two more
outputs: suggested calendar events and Google Tasks per workstream. The two
weekly briefs to Avishag are scheduled separately, in the claude.ai Routines UI
rather than here — a Claude Code trigger cannot attach Gmail in this
organisation, and a brief that never becomes a draft is worthless. The prompts
to paste are in `plan/2026-2027/routine-prompts.md`. It also
reads WhatsApp exports dropped into a Drive folder, because commitments get
made in chat that never reach email. Chat is read-only — the runner never
replies into WhatsApp.

## The workstreams

**Apex** and **VelocityX** are run together and share staff, so they are
triaged and reported as one context under a single `Velocity + Apex` label.
**Tinu** is the GPU and data-centre business — DGX B300 procurement, the
Israeli buildout, and quoting compute to customers — and runs partly on US
Pacific hours. **Personal** has no label of its own; real personal threads are
marked IMPORTANT instead.

Routing lives in `config/workstreams.yaml` — domains, key people, topics, and
the disambiguation rules for the cases where the sender alone is not enough
(Avishag mails from both the Apex and VelocityX domains about either company).
Edit that file when routing gets something wrong; the skills read it and
hardcode nothing.

`config/voice.md` is the voice profile, taken from actual sent mail rather than
invented: short, no warm-up, dash-led asides, `דלג׳ו` in Hebrew and `Delgo` in
English, and the bare forward as a first-class move.

## The Apex network

Beyond mail, Nadav owns Apex's people — 97 alumni across three cohorts.
`config/network/roster.csv` records what each of them is doing, what they need,
where they can help others, and what happens next; `config/network/network.yaml`
holds the rules that govern it. `plan/2026-2027/` carries the yearly plan and a
dated rotation of 189 conversations, 3–4 a week, tiered so founders and people
at a transition point come round three times a year and the rest less often.

The loop is: call someone from today's schedule → paste the summary into
`/call-log` → the roster updates and a follow-up draft comes back carrying up
to three introduction offers matched from the other 96 alumni, each with a
stated reason why those two people should meet *now*. `/network-sync` keeps the
same roster current from Avishag's mail and from WhatsApp exports, so it does
not depend on him remembering to write things down.

Three scripts do the deterministic work: `build_roster.py` seeds the roster,
`build_schedule.py` generates the rotation, `parse_chat.py` normalises WhatsApp
exports (Android, iOS, Hebrew with its invisible RTL marks, and third-party
CSVs) — the last one is under test, because a silently half-parsed export would
write confident nonsense into the roster.

## Guarantees

- **Drafts only.** Nothing is ever sent. Nothing is trashed, marked read, or
  marked spam.
- **No invented facts.** Anything that needs a number or a date you have not
  supplied comes back as a `[[NADAV: ...]]` marker, not a plausible guess.
