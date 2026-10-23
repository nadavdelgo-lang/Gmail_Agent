# Scheduled tasks: state, faults and fixes

Five Routines exist. They were all failing, for three unrelated reasons. This
file is the record of what was wrong and what was done, because the failure mode
here is quiet: a Routine reports SUCCEEDED and produces nothing.

## The five

| Routine | Cron (UTC) | State |
|---|---|---|
| Sunday briefing to Avishag | `0 5 * * 0` | enabled, branch fix applied |
| Thursday weekly report | `0 5 * * 4` | enabled, branch fix applied |
| Avishag task register | `0 6 * * 0` | re-enabled, moved off the 05:00 collision |
| Inbox + chat runner, 8x daily | `0 1,4,7,10,13,16,19,23 * * *` | re-enabled |
| Daily Spanish content refresh | `30 6 * * *` | enabled, still broken, see below |

## Fault 1: the Routines fired against a branch that has none of the inputs

**The big one.** The repo's default branch is
`claude/multi-company-orchestrator-agent-wbahy5`. A scheduled session clones the
default branch. That branch does **not** contain:

- `.claude/skills/weekly-brief/SKILL.md`
- `config/network/network.yaml`
- `config/network/roster.csv`
- `plan/2026-2027/call-schedule.csv`

All of it lives on `claude/apex-velocity-yearly-plan-tv5ru8`, 16 commits ahead
and never merged. So the Thursday report fired on schedule, was told "read these
first, they are the source of truth, never work from memory", found none of
them, and ended two minutes later having written nothing. The run is recorded as
SUCCEEDED, because the session did not crash. Nothing was committed, no file
appeared in `logs/briefs/`, no draft was created.

**Fix applied:** both weekly prompts now begin with a fetch and checkout of the
feature branch, then verify `config/network/roster.csv` has 97 rows and STOP if
it does not, rather than improvising a report to Avishag from memory.

**The better fix, which needs Nadav's say-so:** merge
`claude/apex-velocity-yearly-plan-tv5ru8` into the default branch, or make it the
default. Then no prompt needs to know about branches at all. Pushing to another
branch is outside what this session was authorised to do, so it was not done.

## Fault 2: two Routines were simply switched off

The runner (8x daily) and the Avishag register were both paused, with no
`ended_reason` and no `suspension_reason`, which means a person paused them
rather than the system disabling them. The runner had not fired since its last
successful run in late August; the register had never fired at all.

**Fix applied:** both re-enabled. The register was also moved from 05:00 to 06:00
UTC, because it shared 05:00 Sunday with the Sunday briefing and the two would
have raced each other for the same mailbox.

Worth knowing: the runner fires **eight times a day with push notifications on**.
If that is why it was paused, turn notifications off or cut the cron down rather
than pausing it again.

## Fault 3: the Spanish refresh hangs, and this is NOT fixed

It fired on schedule and was fired again manually as a diagnostic. Both runs sat
at `ROUTINE_RUN_STATUS_PENDING` and never finished, and the calendar event was
never touched: its `updated` timestamp is still from the last manual edit. So
this Routine has been silently doing nothing since it was created.

Two candidate causes, not distinguished yet:
- the session has no Google Calendar connector and hangs rather than erroring, or
- the session hangs for an unrelated reason before reaching the calendar.

Note that `create_trigger` refuses the `connectors` parameter outright for this
organisation, so a Routine created from Claude Code cannot be given connectors at
creation time. Whether a fired session inherits any is unproven either way.

**Next step:** recreate it in the claude.ai Routines UI with Google Calendar
attached. If it works there, connectors are the answer and the two weekly briefs
should move to the UI as well.

## If the briefs need to move to the UI

Both weekly prompts are stored on the Routines themselves and can be copied out
of `list_triggers`. Attach **Gmail** and **Fireflies** (plus Google Calendar for
the Sunday one), keep the same cron, fresh session per firing.

Israel is UTC+3 in summer and UTC+2 in winter, so `0 5` is 08:00 local from late
March to late October and 07:00 the rest of the year. The UI has no timezone
field; if the winter hour matters, run two Routines and disable the out-of-season
one.

## How to tell whether a run actually did anything

Do not trust SUCCEEDED. Check the artefact instead:

- weekly briefs: a Gmail draft updated, or a file in `logs/briefs/` and a commit
- register: the register draft's timestamp moved
- runner: `Runner/Handled` labels applied, or an honest "nothing new" report
- Spanish: the calendar event's `updated` timestamp is today
