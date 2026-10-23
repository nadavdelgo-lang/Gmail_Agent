# Procedures

Eight, not the five expected — the consolidation recovered three more that had
been stranded on a branch the default never saw: call log, network sync and
weekly brief.

Each one states its **gate** (which threads or inputs it looks at), its
**guards** (how it avoids duplicating the last run), and **what it writes**.

---

## 1. Triage

Classify unhandled mail by workstream and rank what actually needs him. Also
the first half of a full pass.

**Gate.** `in:inbox is:important newer_than:14d`. Widen only on request —
`newer_than:30d`, or dropping `is:important` when he says something was missed.
Ask for the window if the default looks wrong. The mailbox has tens of
thousands of unread threads; treating "unread" as the queue is useless.

**Procedure.** Apply the routing document's disambiguation rules in order,
first match wins. Then give each thread exactly one state:

| State | Meaning |
|---|---|
| `needs-reply` | The newest message is from someone else and wants something. |
| `waiting-on` | He replied last and is owed an answer. Note how many days. |
| `route` | Belongs to Avishag or Ken, not him. The action is a forward. |
| `fyi` | Worth knowing, no action. |
| `noise` | Automated notification, newsletter, receipt. |

Two of these carry most of the value. **`waiting-on` is the one he cannot see
for himself** — a thread where he replied and nothing came back is invisible in
an inbox sorted by arrival, so surface it with its age: "8 days, no response."
And **`route` is a real category**, because a large share of his outgoing mail
is a bare forward to Avishag or Ken; do not convert those into things he has to
answer.

Any date agreed in the sweep becomes a calendar suggestion in the same reply.

**Guards.** Skip threads already carrying `Runner/Handled`.

**Writes.** A per-workstream action list, ranked. Labels on everything read.

---

## 2. Draft

Write replies and forwards in his voice, bilingual, saved and never sent.

**Gate.** Threads he names, or the `needs-reply` and `route` items from a
triage pass.

**Procedure.** Read the whole thread first — previews hide the newest message.
Decide the shape before writing: a one-liner (the default, and an emoji
reaction is a complete reply), a `סיכום` status summary, or a bare forward with
no covering note. Picking the wrong shape is a bigger error than getting a
sentence wrong. Then write it: one to four lines by default, no warm-up in
Hebrew, light warm-up in English to externals only, the single key ask in bold.
If the draft agrees a time, say so and raise a calendar suggestion.

**Guards.** Check existing drafts first; never stack a second on a thread that
already has one.

**Writes.** A Gmail draft. Never a sent message. `[[NADAV: ...]]` wherever only
he knows the answer.

---

## 3. Runner — the scheduled pass

One pass over new mail and chat exports. Eight times a day.

**Gate — two lanes, both run every pass.** Lane B does not depend on lane A
finding anything.

```
Lane A   in:inbox is:important newer_than:1d -label:Runner/Handled
Lane B   (from:avishag@apex.org.il OR from:avishag@velocityx.vc)
         newer_than:3d -label:Runner/Handled
```

Note what is absent from lane B: no `is:important`. Gmail does not reliably
flag her mail, so the general gate missed most of it — which is why her threads
sat unanswered through August while the runner reported "quiet" eight times a
day. Never add `is:important` to lane B.

If both lanes are empty, check the chat export folder for anything new, then
stop and report one line. **The gate is an early exit, not a conditional
fire**: a schedule fires on a clock and nothing else, so a session still starts
eight times a day. What the gate saves is the entire pass behind it, typically
one search call instead of thirty. A quiet run is the design working — never
widen a query to find work.

**Procedure.** Triage by workstream. Read chat exports added since last pass,
pulling out only commitments made, dates agreed, and unanswered asks directed
at him. Suggest calendar events and persist each as a task. Add at most five
tasks. Then draft — **lane B first**, before the cap is spent on anything else,
at most five drafts. Then label everything.

**Guards.** Skip anything carrying `Runner/Handled`. List drafts before
drafting. Check the task list before adding. Only read chat messages newer than
ones already handled. A fresh session fires each time, so the mailbox and Drive
are the only memory there is.

**Writes.** Drafts, tasks, labels, and a short report — counts, one line per
suggestion, task and draft, plus a label count so a run that drafted nothing
still shows it did the filing.

---

## 4. Deal tracker

Update the GPU Compute Deal Tracker from a Ken chat or an Amizur mail.

**Gate.** Standing, not requested: anything from Ken Hu or a group he is in,
and anything from Amizur Kafri. From Amizur it is row 10, the Israeli buildout;
from Ken it is whichever row matches.

**Procedure.** Extract only what was actually stated. Match to a row by company
and ask. Where chat contradicts the sheet, the newer source wins but the older
value is preserved in the cell's history rather than erased. Any date agreed
also becomes a calendar suggestion.

**Guards.** Read the row before writing it.

**Writes.** Cell updates through Zapier Google Sheets. Never a rebuilt file.

**Never.** Never write a figure Ken did not state. Never delete a row — a dead
deal becomes `Stage: Parked / Not Now`. Never overwrite `Value / Terms`
wholesale; it is the audit trail of a live negotiation. Never touch the
`Stage Legend` worksheet.

---

## 5. Avishag task register

One living draft of everything open between him and Avishag.

**Gate.** `(from:avishag OR to:avishag) newer_than:14d`, read in full, plus
anything from `team@apex.org.il` assigning either of them an action. Weekly.

**Procedure.** Find the existing draft with subject
`אפקס + Velocity — כל המשימות בינינו במקום אחד` and update it in place. If the
draft is gone but a sent message with that subject exists, he sent it: start a
fresh one covering only what changed since, and say so. Reconcile rather than
rebuild — items answered in the past week move to `נסגר` and keep their line,
items still open stay, and items he pinged again with no reply get the waiting
time marked. That last one is the most valuable part of the register. Track
only things with an owner and an outcome: an unanswered ask, a commitment, a
decision waiting on someone, a name or document one owes the other. Not FYIs,
not forwards. Dates do not go in the register; they come out as calendar
suggestions in the report.

**Guards.** Never a second register draft.

**Writes.** One updated draft, plus a report of only what moved.

**Never.** Never send. Never invent an item, a date or an owner — if a thread
is ambiguous about who owes what, say so rather than assigning it. Never delete
a line to tidy the list.

---

## 6. Call log

A call summary becomes a roster update plus a follow-up draft carrying real
introduction offers.

**Gate.** Standing: any call summary, meeting notes or transcript pasted,
uploaded or forwarded, or him saying he just spoke to someone from Apex.

**Procedure.** Identify the person in the roster. Extract six things from the
summary. Update the row. Then find matches elsewhere in the community — job
opportunities and technical connections — and run every candidate through the
gate before it ships. Draft the follow-up, which **offers** an introduction and
never announces one: `רוצה שאחבר?`, never `חיברתי אותך`, because the other side
has not agreed. Zero offers is a correct outcome.

**Guards.** The row gets a next action or the call did not land.

**Writes.** A roster row update, a follow-up draft, and a dated call record.

**Never.** Never send. Never add a person to the roster unasked. Never write a
fact the summary did not state, or infer a need from tone. Never make an
introduction he has not agreed to. Never change tier or tie strength on your
own. Never create a calendar event. Never carry personal remarks, health,
family or money matters into the roster — it gets shared.

---

## 7. Network sync

Keep the alumni roster current from mail with Avishag and from chat exports.

**Gate.** Daily. Mail with Avishag on both addresses, plus any chat export
newer than the last sync.

**Procedure.** Extract what changed about people, with provenance on every
claim. Apply it. Anything second-hand — relayed by Avishag, overheard in a
group — is written with its source and generates a verification action, never
recorded as though he learned it himself.

**Guards.** A sync-state record of what was last read, so the same export is
not reprocessed.

**Writes.** Roster updates with provenance, a log line per change, and a report
of what needs a decision.

**Never.** Never reply into WhatsApp — there is no supported write path and he
did not ask for one. Never send mail or create a calendar event. Never add a
person, change a tier or change a tie strength on your own. Never write a fact
a source did not state. Never move VelocityX deal flow, donor or staff content
into the roster. **Never parse a chat export by reading it instead of running
the parser.**

---

## 8. Weekly brief

Two modes: the Sunday briefing to Avishag, and the Thursday report with KPIs.

**Gate.** The week's correspondence with Avishag across **both** addresses,
read in full; call summaries someone actually typed; meeting transcripts, where
"skipped" means no summary was generated and a very short meeting returning
single words is not a summary of anything; chat exports; and the roster, the
call schedule and the register.

**Procedure — Sunday (§16).** Top People, up to 5, formatted
`שם | Cohort | מה השתנה | מה הם צריכים | מי מטפל`. Opportunities, up to 3, each
with a why-now. Risks and weak signals, up to 3. `מה אני צריך ממך`, up to 3 and
ideally zero, each carrying who / why now / why her specifically / what exactly
/ how many minutes. Then the coming week's calls with the purpose of each,
rather than the calendar entry. Compute the risks rather than recalling them: a
tier-A alum whose last contact is older than their cadence *is* the brief's
"strong alum out of touch for five months".

**Procedure — Thursday (§17, §21).** The KPI table, week and month, against the
targets. Count from the data; a number you cannot source is left blank, never
estimated, and say plainly which KPIs have nothing behind them yet. Then
dependency (§18) — what share closed without Avishag, where 100% is not the
goal. The funnel (§19): Alumni → Engaged → Helped → Contributors → Nodes,
counted off tie strength, reported thin if it is thin. Connection quality
(§20): of the introductions made, what came of them. Then the three closing
lines (§21) — `מה למדתי` (a pattern, not a list) · `מה אני ממליץ` (never a
problem without a recommendation) · `מה אני צריך ממך` (max three).

**Guards.** One living draft per week, updated in place, never stacked.

**Writes.** A Gmail draft to `avishag@apex.org.il` — subject `בריפינג שבועי, אנשים`
on Sunday, `דוח שבועי` on Thursday.

**Never.** Never send. Never estimate a KPI — this goes to the person the
number is about, and a dash with a note beats a plausible number. Never exceed
a cap; the caps are the point. Never report a fact from the correspondence
without having read its thread in full. Never let a VelocityX deal thread in
unless it carries a person. Never use the briefing to report activity — it
exists so the meeting does not have to. Never invent a risk or an opportunity
to fill a section; empty is a finding.
