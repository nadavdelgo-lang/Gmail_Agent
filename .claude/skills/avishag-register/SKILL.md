---
name: avishag-register
description: Refresh the Apex + VelocityX task register shared with Avishag — re-read the correspondence, update who owes what, and keep one living draft rather than stacking new ones. Runs weekly on a Routine. Use when the scheduled refresh fires, or when the user asks to update the register, refresh the Avishag task list, or check what is open between him and Avishag.
---

# Avishag task register

One living list of everything open between the user and Avishag across Apex and
VelocityX, kept current in a single Gmail draft. Refreshed weekly so the list
he is sitting on never goes stale.

## The register

A draft to `avishag@apex.org.il`, subject **אפקס + Velocity — כל המשימות בינינו במקום אחד**,
organised by owner: **עליי** / **עלייך** / **ביחד** / **נסגר**.

Ground truth for routing and voice: `config/workstreams.yaml`, `config/voice.md`.

## Step 1 — find the existing register

`list_drafts` and look for that subject.

- **Draft still there** → update it in place with `update_draft`. Never create a
  second one; two registers is worse than none.
- **No draft, and a sent message with that subject exists** → he sent it. Start
  a fresh draft covering only what changed since it went out, and say in the
  report that you started a new one and why.
- **Neither** → build it from scratch per the structure above.

## Step 2 — re-read the correspondence

```
(from:avishag OR to:avishag) newer_than:14d
```

Read threads in full with `get_thread` — search previews show only the oldest
messages and will hide the reply that closed an item. Fourteen days against a
weekly refresh gives overlap, which is what you want: better to re-see an item
than to miss one.

Also pick up anything from `team@apex.org.il` that assigns the user or Avishag
an action.

## Step 3 — reconcile, do not rebuild

The register's value is that it is cumulative. For each item already in it:

- **Answered or done in the last week** → move it to **נסגר**, keep the line.
- **Still open** → leave it, and refresh the date or detail if it moved.
- **Pinged again with no reply** → mark how long it has been waiting. This is
  the highest-value column in the whole register and the reason it exists.

Then add whatever is new. Never silently drop a line — an item that vanishes
reads as done when it may just have been missed.

## Step 4 — what counts as an item

Only things with an owner and an outcome:

- an ask one of them made of the other that has no answer
- a commitment either of them made
- a decision waiting on one of them
- a name, intro or document one owes the other

Not: FYIs, forwards with no ask, calendar invitations, or anything already
closed in the thread itself.

## Step 5 — dates

Any date agreed in the week's mail that has no calendar entry comes out as a
**calendar suggestion** in the report — suggest, never create. Do not put it in
the register; the register is asks and commitments, not a schedule.

## Step 6 — report

Short. What moved, not the whole register:

```
Register refreshed · 6 items moved
  → נסגר (3): CJP call booked · Affinity account opened · deck notes sent
  → new (2): JD for the 2 Apex roles · Technion LabAI follow-up
  → still waiting (1): the 9 give-back calls summary — 15 days
Calendar: Avital, Tue 8.9 11:00 — no entry yet
```

If nothing moved, say that in one line and leave the draft alone.

## Never

- Never send. The register is a draft the user sends when he chooses.
- Never stack a second register draft.
- Never invent an item, a date or an owner. If a thread is ambiguous about who
  owes what, say so in the report rather than assigning it.
- Never delete a line to tidy the list.
