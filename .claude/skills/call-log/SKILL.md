---
name: call-log
description: Turn a call or meeting summary with an Apex alum into a roster update and a follow-up draft that carries real introduction offers — job opportunities and technical connections drawn from the rest of the community. Use whenever the user uploads, pastes or forwards a call summary, meeting notes, a Fireflies transcript, or says he just spoke to someone from Apex. Also when he asks to log a call, update someone's record, or find who to connect a person to.
---

# Call log

One alum, one conversation, four outputs: the roster row updated, a follow-up
draft in his voice carrying at most three real offers, a Google Task for the
next action, and a durable record on disk.

This is the skill that makes the network compound. A call that produces no
`next_action` and no offer was, in §7's terms, just a contact-list entry.

## Ground truth

- `config/network/network.yaml` — tiers, the six call questions, the matching
  gate, the extraction contract. Read it every run; hardcode nothing from here.
- `config/network/roster.csv` — the people. Source of truth.
- `config/voice.md` + `.claude/skills/draft/SKILL.md` — how he writes.
- `config/workstreams.yaml` — routing, and `calendar_suggestions`.

Gmail, Calendar, Drive and Zapier tool names carry a server-id prefix that
changes between sessions. Resolve them with ToolSearch every run.

## Step 1 — identify the person

Match the summary against `roster.csv` on `name`, then `name_he`. Hebrew
summaries name people in Hebrew and the roster is in English — check both, and
when you resolve one, **write the Hebrew spelling into `name_he`** so the next
match is free.

- **One match** → proceed.
- **No match** → stop and say so. Offer to add a row, showing what you would
  put in it. Never create a person silently; who counts as "APEX's people" is
  a scoping decision (§1) and it is his.
- **Ambiguous** (two Michaels) → ask. Writing a call onto the wrong row is
  worse than not writing it.

If a Fireflies transcript is available for the meeting, prefer it over a
summary — it is the primary source. Fetch it rather than working from memory
of what the summary said.

## Step 2 — extract the six things

§6 — the conversation should not have felt like a questionnaire, but by the end
these should be answerable:

| Field | The question |
|---|---|
| `current_goal` | עכשיו — what are they doing right now? |
| — | השלב הבא — where do they want to get to? |
| — | חסם — what is stopping them? |
| `needs` | אנשים — who do they need to meet? |
| `can_help` | נתינה — where can they help others? |
| — | APEX — what can APEX do for them, and what would they want to do with us? |

**Whatever the summary does not say stays empty.** An inferred need produces an
introduction built on nothing, and the person on the other end finds out.

Fold the next step, the blocker and the APEX ask into `current_goal` and
`notes` — they are context, not separate columns.

## Step 3 — update the roster row

Write:

- `last_contact` — the date of the conversation, not today's date
- `last_source` — `call <date>`
- `current_goal`, `needs`, `can_help` — only what was actually said
- `next_action` — **required.** The most important field in the file (§7).
  Start it with a verb and make it something you could do tomorrow: "Intro to
  Dolev on cloud security hiring", not "follow up".
- `next_action_due` — only if a date was stated
- `location` — if they mentioned moving, especially to SF (§11)
- `notes` — append, never overwrite. Prefix with the date.

**Propose, never apply**, for two fields:
- `tier` — a C who turns out to be founding should be A, but that is his call.
- `tie_strength` — moving someone to Contributor or Node is a judgement (§8).

Say what you would change and why, and leave it.

Append one line per changed field to `logs/roster-log.md`:
`date | person | field | old → new | source`.

## Step 4 — find the matches

Scan the other 96 rows in both directions:

1. **Who can serve this person's `needs`?**
2. **Whose `needs` can this person serve?** — this is the half that gets
   forgotten, and it is how an alum becomes a Contributor (§4).

Two kinds, both of which he asked for by name:

**Job opportunities.** Match `needs` mentioning a role, a move or a search
against other alumni's `company`. The roster carries real referral paths —
Wiz, Cyera, Breeze Security, Snyk, Datadog, Palo Alto, Orca, Zafran, Claroty,
Vayyar, Remitly, Walmart, Intel, Miggo, Akeyless, Eon, Edwin, Sayata, Protai
and more. The offer is *a warm introduction to someone inside*, never a job.

**Technological connections.** Match on `domain` plus the specifics in `role`
and `notes`: security research, AI infra, ML, quantum, fusion, DNA storage,
POMDP planning, embedded, cloud, health-bio.

**Founder support.** A founder or future founder meeting someone who has
already done what they are about to do. §5's highest-value shape, and with 27
tier-A alumni there is usually one.

### The gate — every one of these, or the offer does not ship

§3: *"we do not do introductions for the sake of introductions. Before
connecting you need to answer: why do these two need to know each other now?
If there is no good answer, we do not connect."*

- **A one-sentence "why these two, why now" exists**, and it goes in the email.
  If you cannot write that sentence, drop the offer.
- **Never propose someone whose `can_help` is empty.** That is a guess wearing
  a fact's clothing.
- **Never assert anything about the third person** beyond what their row says.
- **Maximum three offers.** Usually one or two is right. **Zero is a correct
  outcome** and should be reported plainly, not padded.
- **Contributor load** (§12) — if you have proposed the same person three times
  this quarter, say so instead of proposing them a fourth. Their time is a
  scarce resource and burning them costs more than a missed match.
- **§14 escalation** — an exceptional person, a founder worth pulling close, a
  donor or strategic partner, a sensitive relationship, or an intro where
  Avishag's connection genuinely changes the odds: surface it as a
  recommendation with who / why now / why her / what exactly / how long. Do not
  action it, and do not put it in the alum's email.

## Step 5 — draft the follow-up

Follow `.claude/skills/draft/SKILL.md` and `config/voice.md` exactly. In
practice:

- Match the language of the conversation. Hebrew signs **דלג׳ו**; English
  signs **Delgo** or nothing.
- Open on the point. No "great speaking with you today" warm-up.
- One to four lines plus the offers. If it runs longer, it is wrong.
- **Offer, never announce.** "רוצה שאחבר?" — never "חיברתי אותך". The other
  side has not agreed yet, and saying otherwise commits them.
- Hand the decision back: "תגיד לי מה מתאים לך", "let me know which of these
  is useful".
- Do not formalise the Hebrew. Formal register is the clearest tell of a
  machine-written draft.

Shape:

```
[one line picking up the thing that actually mattered in the call]

[the offers, one line each — name, one clause of why them, and the ask]

[the decision handed back]

דלג׳ו
```

Never invent a figure, date or commitment. Anything that needs something only
he knows goes in as `[[NADAV: ...]]`.

Save as a **draft**. Never send. Before drafting, `list_drafts` and check the
thread does not already carry one — never stack a second.

## Step 6 — persist it

**Google Task** in the `Velocity + Apex` list: the `next_action`, verb first,
with the person's name and a link to the call log in the notes. Check the list
first and skip a duplicate title.

**If a date was agreed** — a coffee, a follow-up call, an event — that is a
calendar suggestion *now*, per the standing rule in `CLAUDE.md`. One line:
what · when · who. Suggest, never create: creating an event mails invitations.
Add it as a Google Task too (see `calendar_suggestions` in
`config/workstreams.yaml`), dedupe on who+when.

**If the person is founding, joining a founding team, or raising** — flag the
VelocityX bridge: propose the Affinity entry, and flag it as a §14 moment.

## Step 7 — record it

Write `logs/calls/YYYY-MM-DD-<name>.md`:

```markdown
# <Name> · <date> · <cohort>, tier <X>

**Now:** …
**Next step:** …
**Blocker:** …
**Needs:** …
**Can help:** …
**APEX:** …

**Next action:** …
**Offers made:** … (or: none — nothing met the gate)
**Roster changes:** …
```

Then mark the matching row in `plan/2026-2027/call-schedule.csv` as `done`.

## Report

Short. What changed, not a retelling of the call:

```
Ilan Voronel · #2 · tier B · 28.8

Roster
  needs        → ML infra role, wants out of Glassbox by Q1
  can_help     → ML pipelines, interviewing
  next_action  → Intro to Guy Goldenberg (Wiz) on the ML infra opening

Offers in the draft (2 of 4 considered)
  • Guy Goldenberg, Wiz — Wiz is hiring in ML infra and Ilan wants to move now
  • Gil Raytan, Remitly — ran the same research-to-production move two years ago
  dropped: Georgy Melamed (can_help empty), Matan Shoef (no "why now")

Draft saved · Task added · No date agreed
```

## Never

- Never send. Drafts only.
- Never add a person to the roster without being asked.
- Never write a fact the summary did not state, or infer a need from tone.
- Never make an introduction the user has not agreed to — the draft offers it.
- Never change `tier` or `tie_strength` on your own.
- Never create a calendar event.
- Never carry personal remarks, health, family or money matters into the
  roster. It gets shared.
