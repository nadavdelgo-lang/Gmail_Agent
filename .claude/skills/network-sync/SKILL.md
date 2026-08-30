---
name: network-sync
description: Keep the Apex alumni roster current from mail with Avishag and from WhatsApp exports — extract what changed about people, apply it with provenance, and report what needs a decision. Runs daily on a Routine. Use when the scheduled sync fires, when the user uploads or points at a WhatsApp export (.txt or .csv), or when he asks to sync the network, update the roster from mail, or catch up on what has changed with people.
---

# Network sync

`/call-log` handles the person he just spoke to. This handles everything else:
the news that arrives second-hand in Avishag's mail, and the commitments made
in WhatsApp that never reach email.

Most alumni news is relayed, not witnessed — *"דנה עוזבת את Meta"*, *"יואב עובר
ל־SF באוקטובר"*. That is exactly §2's "APEX needs to know its people at every
moment", and it is the highest-yield source in the system because it costs him
nothing. It is also someone else's account of a third party, which is why every
fact from it is labelled and verified rather than simply believed.

## Ground truth

- `config/network/network.yaml` — the `extraction` block is the contract. Read
  it every run.
- `config/network/roster.csv` — the people.
- `config/network/sync-state.yaml` — what has already been read.
- `config/workstreams.yaml` — routing, and the firewall between Apex/VelocityX.
- `scripts/parse_chat.py` — the export parser. Never parse a chat by eye.

Resolve Gmail and Drive tool names with ToolSearch every run.

## State — read this first

There is no memory between runs. `config/network/sync-state.yaml` is the whole
state store:

```yaml
last_mail_sweep: 2026-08-29
chat_exports:
  "WhatsApp Chat with Avishag Bohbot.txt":
    last_message: "2026-08-28T20:06:00"
```

Nothing outside that file tells you what you have already seen. Read it before
anything else and write it back at the end — a sync that forgets produces a
second copy of every fact it found yesterday.

## Step 1 — mail with Avishag

```
(from:avishag OR to:avishag) newer_than:14d
```

Plus anything from `team@apex.org.il` that concerns a person. Fourteen days
against a daily run is deliberate overlap; `sync-state` and the roster's own
values are what actually prevent duplicates.

Read threads in full with `get_thread` — a search preview shows the oldest
message and will hide the reply carrying the news.

`avishag-register` reads the same window for a different purpose. Both are
read-only on mail, so the overlap is harmless — do not try to coordinate them.

## Step 2 — chat exports

Read `chat_sources` in `config/workstreams.yaml` for the Drive folder. List it
and take anything added or modified since the last run.

**Parse with `scripts/parse_chat.py`, never by reading the file directly.**
WhatsApp's format varies by platform, locale and phone language, and Hebrew
exports carry invisible bidirectional marks that make a naive read collapse the
whole file into one message. The script handles Android, iOS, 12- and 24-hour
clocks, dotted dates, multi-line messages, system notices, and CSV exports from
third-party tools:

```
python3 scripts/parse_chat.py "<file>" --since <last_message> --stats
python3 scripts/parse_chat.py "<file>" --since <last_message>
```

Only look at messages newer than `last_message` for that file. If the parser
reports far fewer messages than the file's size suggests, or the CSV mapping
fails, **say so and stop on that file** rather than working from a partial
read — a half-parsed export produces confident, wrong roster entries.

Unsaved contacts appear as raw phone numbers in the sender field. Match them
against `roster.csv` only once the phone column is populated; otherwise report
the number and leave it.

## Step 3 — extract

Pull only what maps to a roster field. From `network.yaml`:

- role or company change
- a location move, SF especially (§11)
- founding, or considering founding
- looking for a co-founder
- a raise, or fundraising underway
- a stated need — investor, researcher, mentor, customer, compute, a hire
- an offer to help, mentor, speak, or give office hours
- an ask directed at APEX

Plus, from chat specifically, the three things the runner already looks for:
commitments made, dates agreed, and unanswered asks directed at him.

### The rules

- **Stated facts only.** *"דנה עוזבת את Meta"* is a fact. "Dana sounded
  restless" is not, and never becomes one. Do not summarise a mood into a need.
- **Second-hand is labelled second-hand.** A fact relayed by Avishag is written
  with `last_source: avishag-mail <date>` and generates a verification
  `next_action` — "confirm with Dana directly". §23 is *know the people
  deeply*, not know what someone said about them. A message the alum wrote
  themselves is first-hand; someone describing them in a group is not.
- **Never carry gossip**, personal remarks, health, family or money matters
  into the roster. The runner already applies this to chat; here it matters
  more, because this file gets shared.
- **Workstream firewall.** Avishag's mail carries VelocityX deal flow, donors,
  staff coordination and Apex logistics. Route with `workstreams.yaml`; only
  alumni and network content reaches the roster. **A donor is not an alum.**
  A portfolio founder who is not an APEX alum is not an alum either.
- **Never invent a person.** An unrecognised name is reported for his decision.

## Step 4 — write

Apply directly and commit, one commit per sync, with the diff in the report.
Git is the review mechanism — a second pending queue that nobody opens is worse
than none.

For every field changed, append to `logs/roster-log.md`:
`date | person | field | old → new | source`.

`notes` is appended to with a dated line, never overwritten. `next_action` is
replaced only when the new one supersedes the old; if both are live, keep the
older and mention the new one in the report.

**Three things escalate instead of being written:**

1. **A person not in the roster** — report the name and the context, ask
   whether to add them.
2. **`tier` or `tie_strength`** — propose with a reason, never apply.
3. **Anything hitting §14** — an exceptional person, a founder worth pulling
   close, a donor or strategic partner, a sensitive relationship. Report it
   with who / why now / why Avishag / what exactly / how long.

## Step 5 — dates and tasks

A date agreed anywhere becomes a **calendar suggestion immediately**, per the
standing rule in `CLAUDE.md` — mail, chat, or a passing line in either. Read
the calendar first so the suggestion accounts for what is booked. Suggest,
never create. Persist it as a Google Task in `Velocity + Apex` per
`calendar_suggestions`, deduped on who+when.

A new `next_action` becomes a Google Task in the same list, verb first, deduped
on title. **Cap: five tasks per sync.** If more qualify, take the five most
time-sensitive and say how many you left.

## Step 6 — report

```
Network sync 21:00 · Avishag mail 4 threads · 1 export (Avishag Bohbot, 62 new)

Roster updated (3)
• Dana Levi — company: Meta → leaving, founding · needs: technical co-founder
  ↳ second-hand via Avishag 28.8 — next action: confirm with her directly
• Yoav Bar — location: → SF (October) · needs: 3 AI-infra connections
• Tomer Goren — last_contact: 27.8 (chat, first-hand)

Needs a decision (2)
• "מיכל מהמחזור השני" appears in chat, not in the roster — add her?
• Guy Yoshpe reads as tie_strength 4 now (introduced two alumni himself) — promote?

Worth Avishag (1)
• Meir Adest offered to host an alumni evening | needs an answer this week |
  her call whether we take it | 5 minutes

Calendar: Coffee Club #2, Tue 15.9 10:00 — agreed in chat, no entry yet
Tasks added (3) · Committed a1b2c3d
```

If nothing changed, one line saying so is the entire report. At a daily cadence
most syncs should be quiet — that is the design working.

## Never

- Never reply into WhatsApp. There is no supported write path and he did not
  ask for one. Chat is read-only history.
- Never send mail, or create a calendar event.
- Never add a person, change a tier, or change a tie strength on your own.
- Never write a fact a source did not state.
- Never move VelocityX deal flow, donor or staff content into the roster.
- Never parse a chat export by reading it instead of running the parser.
