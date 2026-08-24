---
name: deal-tracker
description: Update the GPU Compute Deal Tracker from a Ken chat. Use whenever the user sends, pastes, forwards or exports a WhatsApp chat with Ken Hu or a group Ken is in — the tracker is updated from it as a standing instruction, without being asked each time. Also use when the user asks to update the deal tracker, the GPU tracker, or the Tinu pipeline sheet.
---

# GPU Compute Deal Tracker

A standing instruction: **every time the user sends a chat from Ken, or from a
group Ken is in, update the tracker from it.** He does not have to ask. Ken
chat in → tracker updated → report what changed.

## The file

`config/workstreams.yaml` → `deal_tracker` holds the current file id and URL.

Two worksheets:

| Worksheet | Contents |
|---|---|
| `Deal Tracker` | one row per deal, columns below |
| `Stage Legend` | priority 1–8 and what each stage means |

Columns, in order:

`ID` · `Deal / Lead` · `Company / Counterparty` · `Contact(s)` ·
`Product / Ask` · `Volume / Scope` · `Value / Terms` · `Stage` ·
`Last Contact` · `Next Step`

## Reading and writing it

Read with the Google Drive tools (`read_file_content`).

Write with the Zapier Google Sheets actions (`GoogleSheetsV2CLIAPI`) —
`lookup_row` / `get_many_rows` to find the row, `update_row` to change it,
`add_row` for a new deal. The connection is already authorised.

**The file must be a native Google Sheet.** The Google Sheets API cannot
address an uploaded `.xlsx`, so if the tracker is still `.xlsx`, writing will
fail — say so rather than working around it. The exact error Google returns is:

> This operation is not supported for this document. The document must not be
> an Office file.

Check the format before writing: `get_file_metadata` on the file id, and look
at `fileExtension`. A `.xlsx` opens in the Sheets editor and gets a
`docs.google.com/spreadsheets/d/...` URL, so **the link looks native even when
it is not** — the tells are `rtpof=true` in the URL and an `.XLSX` badge beside
the title. Do not argue the point from the URL; check the metadata, or attempt
the write and quote the error.

The fix is the user's: File → Save as Google Sheets, which creates a new file
with a new id. Update `deal_tracker.file_id` and set `writable: true` when it
lands. Never rebuild the file by
re-uploading bytes: that fragments version history, breaks the link, and risks
corrupting a live commercial record.

**When you cannot write, do not throw the extraction away.** Append the fully
prepared row to `config/pending/deal-tracker-queue.md` so nothing is lost, and
tell the user it is queued. On any later run, check that file first: if the
tracker is now writable, flush the queue into the sheet — matching by
counterparty so an entry already applied is not written twice — and delete
what you applied.

## What to extract from a Ken chat

Ken talks in prices, lead times and allocations. Pull only what changes a
cell:

- **a price** — per system, per rack, per GPU-hour
- **a lead time or delivery date**
- **a stage change** — quoted, accepted, stalled, dead
- **a volume or scope change** — node counts, MW, rack counts
- **a new counterparty or contact**
- **an action item** for Ken or the user

Ignore everything else. Banter, logistics and opinions do not belong in a
deal tracker.

## Matching to a row

Match on **counterparty first**, then product. The tracker already carries
Joulix, Guy Solmate, Guy Marom, Idan Pearl Research, Coret AI, Yuval Steuer,
Blue Ocean, Isquered, Amizur Kafri, Sharon AI and Impala AI.

- Confident match → update that row.
- Genuinely new deal → new row, next free `ID`, `Stage: Discovery` unless the
  chat says otherwise.
- Same counterparty but a clearly different product or deal → new row, and say
  why you split it.
- Cannot tell which of two rows it belongs to → **do not guess.** Report both
  candidates and leave the sheet alone.

## Rules for writing cells

- **Never invent a number, date or term.** If Ken says "around 650" write
  `~$650K (Ken, chat DD/MM)`, not `$650,000`. If he is vague, leave the cell
  and note it in the report.
- **Attribute and date every figure** that came from chat, so a later reader
  knows where it came from: `$6.5/hr/GPU (Ken, chat 24/08)`.
- **Append, do not overwrite, the commercial history** in `Value / Terms`.
  That column is the audit trail of a live negotiation — the old number is
  how you know the deal moved. Add the new figure and keep the old one.
- **`Stage` is a controlled vocabulary.** Only the eight values in the
  `Stage Legend` worksheet. Never invent a stage.
- **`Last Contact`** becomes the date of the chat, in `DD/MM/YYYY`.
- **`Next Step`** should be rewritten to what is actually next after this
  chat, not accumulated forever.

## When chat contradicts the sheet

A live negotiation moves, so contradiction is normal and usually means the
chat is newer. But **flag it, do not silently overwrite** — the sheet holds
quoted prices that may already be out with a customer. Report it as
`was X → now Y (Ken, chat DD/MM)` and let the user confirm anything that
changes a price already quoted.

## Report

After writing, report per row changed:

```
Row 4 · Guy Marom · B300/GB300 offtaker
  Value / Terms  + hourly settled at $6.4/hr/GPU (Ken, chat 24/08)
  Stage          Negotiating → Committed/Closing
  Last Contact   20/08/2026 → 24/08/2026
  Next Step      rewritten: paperwork + first payment
```

Then one line for anything you deliberately did not write, and why.

## Never

- Never write a figure Ken did not state.
- Never delete a row. A dead deal becomes `Stage: Parked / Not Now`.
- Never overwrite `Value / Terms` wholesale.
- Never touch the `Stage Legend` worksheet.
