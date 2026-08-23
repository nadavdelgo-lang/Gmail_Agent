---
name: triage
description: Triage the inbox across Apex, VelocityX, Tinu and personal — classify unhandled threads by workstream, rank what actually needs the user, and produce a per-company action list. Use when the user asks to triage, go through, sort, or catch up on email, or asks what needs a reply or what they are behind on. Also the first half of a full orchestrator run.
---

# Cross-company inbox triage

Produce one ranked picture of what needs the user across all four workstreams,
so they can context-switch once instead of four times.

## Before you start

Read `config/workstreams.yaml`. It holds the routing table, the people, the
disambiguation rules and the label names. Do not classify from memory — the
config is the source of truth and the user edits it.

The Gmail MCP tool names carry a server-id prefix that changes between
sessions. Find them with ToolSearch (`select:search_threads,get_thread,...` or
a keyword search for "gmail") rather than assuming a prefix.

## Step 1 — pull the candidate set

The mailbox has tens of thousands of unread threads. Treating "unread" as the
work queue is useless. Scope to threads that plausibly need the user:

```
in:inbox is:important newer_than:14d
```

Widen only on request — `newer_than:30d`, or dropping `is:important` when the
user says something was missed. Ask for the window if the user did not say one
and the default looks wrong for their situation.

Use `search_threads` with `THREAD_VIEW_METADATA_ONLY` for the sweep. Large
results are written to a file instead of returned — when that happens, use `jq`
on the file rather than trying to read it whole.

## Step 2 — classify

For each thread, apply `disambiguation` from the config in order, first match
wins. The rules that actually matter in practice:

- **Anything touching a tinu.ai address or Ken is Tinu.**
- **Avishag is not a routing signal.** She works across both Apex and
  VelocityX and mails from either address about either company. Decide from
  subject and body: deal flow, DD, cap tables, founder intros and money going
  out are VelocityX; community, events, delegations, alumni, staff and money
  coming in are Apex.
- **Consumer-domain senders are not automatically personal.** Much of the Apex
  community writes from personal Gmail addresses.
- When a thread genuinely spans Apex and VelocityX, tag it `apex_velocityx`
  and say so — do not force a side.

Read the thread body with `get_thread` (`PLAIN_TEXT`) before classifying
anything you cannot place from metadata. Guessing from a subject line is how
this goes wrong.

## Step 3 — assign a state

Per thread, exactly one:

| State | Meaning |
|---|---|
| `needs-reply` | The last message is from someone else and wants something from the user. |
| `waiting-on` | The user replied last and is owed an answer. Note how many days. |
| `route` | Belongs to Avishag or Ken, not the user. The action is a forward. |
| `fyi` | Worth knowing, no action. |
| `noise` | Automated notification, newsletter, receipt. |

Two things to get right, because they are where the value is:

- **`waiting-on` is the one the user cannot see for themselves.** A thread
  where they replied and nothing came back is invisible in an inbox sorted by
  arrival. Surface it with the age: "8 days, no response."
- **`route` is a real category here.** A large share of this user's outgoing
  mail is a bare forward to Avishag or Ken. Do not turn those into
  needs-reply items for the user.

## Step 4 — rank

Within each workstream, order by: an explicit ask with a deadline, then a
person waiting on the user, then age. Across workstreams, do not interleave —
the user thinks in companies, so keep the sections separate.

## Step 5 — report

Group by workstream, in this order: **Apex + VelocityX** (the two together,
since they are run together), **Tinu**, **Personal**. Under each:

```
### Apex
1. [needs-reply] Avishag — סיכום אירוע 5/8 · asks for numbers by Sunday · 2d
2. [waiting-on]  avitals@cjp.org — no answer on the visit dates · 8d
```

One line per thread: state, who, what it wants, age. No paragraphs. Put the
count of `noise` at the end as a single number, not a list.

Close with a **cross-company** note only when there is something real to say —
a collision between two companies' deadlines in the same day, or the same
person waiting on two threads in different streams. Skip the section when
there is nothing; an empty "no conflicts" line every run trains the user to
stop reading.

## Labelling (optional, ask first)

Applying Gmail labels changes the user's live mailbox. Offer it, do not do it
unprompted:

> Want me to label these in Gmail so the split persists?

On a yes: `list_labels` first, create only the missing ones from the config's
`labels` block (`Apex` already exists), then `label_thread`. Never remove a
label the user put there.

## What not to do

- Do not read 40,000 unread threads. The candidate set is the skill.
- Do not send anything. Triage classifies; `/draft` writes; the user sends.
- Do not mark anything read, trash, or spam.
