---
name: deal-tracker
description: Update the GPU Compute Deal Tracker from a Ken chat or from Amizur Kafri on the Israeli buildout. Use whenever the user sends, pastes, forwards or exports a chat or mail from Ken Hu, a group Ken is in, or Amizur Kafri — the tracker is updated from it as a standing instruction, without being asked each time. Also use when the user asks to update the deal tracker, the GPU tracker, or the Tinu pipeline sheet.
---

# GPU Compute Deal Tracker

Two standing instructions. The user does not have to ask for either — signal
in, tracker updated, report what changed.

| Trigger | Goes to |
|---|---|
| A chat from **Ken Hu**, or a group Ken is in | whichever row the counterparty matches |
| Mail or a chat from **Amizur Kafri** | **row 10** — the Israeli site buildout |

Amizur is the supply side, not a customer. His mail is almost always about the
Migdal HaEmek / Nahalal site: equipment specs, vendor quotes, power approvals,
fibre, structural work. It carries dates and figures more reliably than anything
else in the inbox, and it moves one row rather than the whole sheet.

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

Three things that cost time the first run, all in the config:

- `worksheet` takes the **gid**, not the sheet name. "Deal Tracker" is
  `691243873`. Passing the name silently resolves to nothing.
- Resolve the enums in order — pass `drive: "My Drive"` and `spreadsheet`
  first, then `worksheet`, then re-inspect to get `dynamic_properties_schema`,
  which maps `COL$A`…`COL$J` to the headers.
- Column A is headed **`Deal Tracker ID`**, not `ID`. Header is row 1, so a
  deal with ID N lives on sheet row N+1.

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

## What to extract from Amizur (row 10)

He writes short Hebrew mail, usually a bare forward with a one-line note, and
almost every one carries something that changes a cell:

- **a vendor quote** — cabinets, PDU, cooling, UPS, CDUs, fibre
- **a power figure or an approval** — MVA/kVA available, the 910A/630kVA local
  approval, anything from the electric utility
- **a connectivity change** — the Bezeq 1000/1000 line, lead time from order,
  competing quotes
- **a lead time or a site date** — a survey, a delivery, an installation window
- **a named third party** — Eaton, Bezeq, Ziv Ben Yehuda (structural engineer)
- **a blocker** — land or building rights on plot 105B, CDU financing

Row 10 already carries the ~$27M B300 quote (~$600K/node), 1.2 MVA available
against a 4 MW target, and the ~1.5 month Bezeq lead time from order. Append
against those, do not replace them.

**The hard date on this row is 11/09/2026** — first set of 8 nodes live.
Anything in his mail that moves that date is the most important thing in it,
and belongs in the report even if it changes no cell.

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

**Amizur always means row 10** unless he is clearly talking about a different
site or a different deal — say so and stop rather than inventing a row.

For everything else, match on **counterparty first**, then product. The tracker already carries
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

## Dates go to the calendar too

Any date agreed in the source — a site survey, a delivery window, a call, an
expiry — also becomes a **calendar suggestion** in the same reply, AND a
Google Task in the matching list (Tinu for Ken/Amizur) per
`calendar_suggestions` in the config, so it survives past this reply. Suggest,
never create: creating an event mails invitations to other people. One line:
what · when · who · which row.

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
