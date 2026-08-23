# Gmail Agent

A Claude Code agent that orchestrates email across three companies and personal
life, out of one Gmail account.

## Setup

None. It drives the Gmail connector already attached to the Claude Code
session — no OAuth, no deployment, no credentials in the repo.

## Use

```
/triage      # what needs you, ranked, grouped by company
/draft       # write the replies, in your voice, saved as drafts
```

For a full pass — triage, checkpoint, then draft the top items — ask for the
orchestrator agent.

## The workstreams

**Apex** and **VelocityX** are run together and share staff, so they are
triaged and reported as one context. **Tinu** is US-facing and runs on Pacific
hours. **Personal** is the fallback.

Routing lives in `config/workstreams.yaml` — domains, key people, topics, and
the disambiguation rules for the cases where the sender alone is not enough
(Avishag mails from both the Apex and VelocityX domains about either company).
Edit that file when routing gets something wrong; the skills read it and
hardcode nothing.

`config/voice.md` is the voice profile, taken from actual sent mail rather than
invented: short, no warm-up, dash-led asides, `דלג׳ו` in Hebrew and `Delgo` in
English, and the bare forward as a first-class move.

## Guarantees

- **Drafts only.** Nothing is ever sent. Nothing is trashed, marked read, or
  marked spam.
- **No invented facts.** Anything that needs a number or a date you have not
  supplied comes back as a `[[NADAV: ...]]` marker, not a plausible guess.
