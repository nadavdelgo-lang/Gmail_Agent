# Routing

Who and what belongs to which workstream. This is the source of truth — never
classify a thread from memory when this document can answer it. When routing
comes out wrong, the fix is a change here, not a one-off exception.

Derived from a scan of `nadav.delgo@gmail.com`, sent mail and inbox, mid-2026.

## Me

| | |
|---|---|
| Name | Nadav Delgo |
| Hub account | `nadav.delgo@gmail.com` — everything lands here |
| Alias | `nadav.d@tinu.ai` — Tinu identity, forwards into the hub |
| Alias | `talent@apex.org.il` — Apex Talent & Network |
| Languages | Hebrew and English, both directions |

**Both aliases are me.** A thread answered from `talent@apex.org.il` does not
show as sent in the hub mailbox and will look completely unanswered. Check who
sent the newest message before concluding a thread is open.

## The four workstreams

Apex and VelocityX are run together and share staff. They are reported as one
section. Tinu and personal are separate.

### Apex — nonprofit / community organization

Hebrew-first. Domain `apex.org.il`.

- Key addresses: `avishag@apex.org.il`, `team@apex.org.il` (internal staff
  list), `talent@apex.org.il`, `dvir@apex.org.il`, `tamir@apex.org.il`,
  `buchman@apex.org.il`
- Partners: `cjp.org` — Combined Jewish Philanthropies, funder and partner
  (`avitals@`, `liork@`, `mayaz@`); `thecohns.us` — `michael@thecohns.us`,
  donor; `hoffmankofman.com` — community programming, sometimes personal, so
  check the content
- Topics: alumni community / קהילת הבוגרים · events and event summaries /
  אירוע, סיכום אירוע · delegations / משלחת · donor contributions · the closed
  community group / שבט · playbooks, registration, give-back
- Hebrew subject signals: אפקס, בוגרים, משלחת, אירוע, שבט, תרומה, קהילה
- English subject signals: apex, alumni, delegation, contribution, give-back,
  community

### VelocityX — venture capital fund

Hebrew internally, English with founders. Domain `velocityx.vc`. CRM: Affinity.

- Key address: `avishag@velocityx.vc`
- Topics: due diligence / DD · investment opportunities and deal flow · founder
  and investor intros · portfolio and co-investor coordination
- Counterparty domains seen in the deal flow: audiseai.com, pi.security,
  oz.security, joulix.ai, niv-ai.com, getimpala.ai, camelotbiocapital.com,
  overline.vc, tauventures.co.il, squaretower.xyz, stoaexchange.com
- Hebrew subject signals: הזדמנות, השקעה, בדיקת נאותות
- English subject signals: DD, due diligence, investment, opportunity, deck,
  term sheet, cap table, affinity, intro, portfolio

### Tinu — GPU and data-centre hardware

English with Ken and US counterparts, Hebrew with Israeli suppliers. Domain
`tinu.ai`. Ken works Pacific hours (`America/Los_Angeles`).

**What it actually is:** not a generic US venture. Tinu buys, builds and
resells GPU compute — NVIDIA DGX B300 procurement, an Israeli data-centre
buildout (potentially 16 MW), and quoting GPU capacity to customers who ask.
Threads about racks, PDUs, cooling, UPS, power, connectivity, Nvidia compliance
or a price per node are Tinu, whatever address they arrive from.

- Key addresses: `nadav.d@tinu.ai`, `ken@tinu.ai` (Ken Hu, co-principal),
  `ken.hu@princeton.edu`, `tinuai88@gmail.com`
- Supply side: **Amizur Kafri**, `amizurkafri@gmail.com` — main counterpart on
  the Israeli buildout. Equipment specs, vendor quotes, financing models,
  usually Hebrew, often a bare forward with a one-line note. High signal: his
  mail almost always carries a date or a decision. Vendors: Eaton (UPS and
  power), Bezeq / בזק (site connectivity)
- Demand side, customers asking to lease or buy compute: joulix.ai,
  solmate.com, niv-ai.com
- Topics: DGX B300 / H100 / H200 / B200 procurement and Nvidia compliance ·
  buildout — racks, PDU, cooling, UPS, power, connectivity · financing models
  and cost per kW · quoting GPU capacity · partner and customer calls, usually
  titled "`<Company> <> Ken/Nadav`"
- English subject signals: tinu, GPU, DGX, B300, B200, H100, H200, nvidia,
  data center, datacenter, UPS, PDU, rack, kW, MW, quote, compute, `<> ken`
- Hebrew subject signals: דאטה סנטר, ארונות, מיזוג, אל פסק, מפרט, הצעה, בזק

### Personal — the fallback

Hebrew-first. Family and friends on consumer domains · government and
administrative paperwork (e.g. mops.gov.il) · personal finance, health, travel,
logistics · service notifications (github, google accounts, spotify, calendly,
drive shares, read.ai).

**A consumer-domain sender is not automatically personal.** Much of the Apex
community writes from personal addresses. Classify on content and fall back to
personal only when no work signal is present.

## Avishag

The single highest-volume correspondent, on both sides.

| | |
|---|---|
| Addresses | `avishag@apex.org.il`, `avishag@velocityx.vc` |
| Routing | On content, **never** on which domain she used |

She mails from the apex.org.il address about VelocityX matters and the reverse.
The address is a weak hint, not proof.

## Disambiguation — applied in order, first match wins

1. **Hardware topic → Tinu.** GPU/DGX hardware, buildout (racks, PDU, cooling,
   UPS, power, connectivity), Nvidia compliance, cost per kW, or quoting
   compute. True even from a consumer-domain sender such as Amizur.
2. **Tinu address → Tinu.** Any `tinu.ai` address, or `ken.hu@princeton.edu`.
3. **Avishag on either domain → decide from subject and body.** Money going
   *out* to a company, DD, deal flow, cap tables and founder intros are
   VelocityX. Community, events, delegations, alumni, staff coordination and
   money coming *in* as donations are Apex. If it genuinely spans both, tag it
   Apex + VelocityX and say so.
4. **Counterparty domain on the VelocityX list → VelocityX.**
5. **Apex partner domain (cjp.org, thecohns.us) → Apex.**
6. **No-reply or notification address → personal**, and almost always FYI, not
   action.
7. **Fallback → personal.**

## Labels

| Workstream | Label | ID |
|---|---|---|
| Apex + VelocityX | `Velocity + Apex` | `Label_2` |
| Tinu | `Tinu` | `Label_3` |
| Personal | IMPORTANT — no label of its own, by design | — |
| Processed, any workstream | `Runner/Handled` | `Label_5` |

A pre-existing label `Apex` (`Label_9131845736770565248`) predates this setup
and is left alone.

Rules: every thread read gets labelled before the pass ends, not only the ones
that produced a draft — an unlabelled thread is re-read from scratch next time.
Noise gets `Runner/Handled` and no workstream label. Never mark a newsletter
IMPORTANT to "label" it personal; IMPORTANT is the backbone of the candidate
set and polluting it breaks every future pass. Never put both workstream labels
on one thread — if it is genuinely both, it is `Velocity + Apex`.

Use label **display names** in queries, never IDs: `-label:Runner/Handled`
excludes correctly, `-label:Label_5` silently excludes nothing.

## The Avishag auto-reply lane

The general gate is `is:important newer_than:1d`. Avishag gets a second lane
that **drops `is:important`** and widens to 3 days, because Gmail does not
reliably flag her mail and the general gate missed most of it — which is
exactly what happened through August.

Every thread where her message is the newest and no draft already sits on it
gets a draft, unprompted. Route Apex vs VelocityX on content. She writes
Hebrew: reply in Hebrew, sign `דלג׳ו`.

The one exception: a thread where **he** is waiting on **her** gets no draft.
There is nothing to say yet — label it and move on.

Never send. Never stack a second draft on a thread that already has one. Never
invent a date, figure or commitment — use `[[NADAV: ...]]`.

## The GPU Compute Deal Tracker

Standing instruction: every Ken chat, and every Amizur mail, updates this.

| | |
|---|---|
| Title | GPU Compute Deal Tracker |
| File ID | `10_6E3oLHeQ2T8aTeM_aIkQG8-BhQF-XIEkdYRbw-lJA` |
| URL | https://docs.google.com/spreadsheets/d/10_6E3oLHeQ2T8aTeM_aIkQG8-BhQF-XIEkdYRbw-lJA/edit |
| Format | Native Google Sheet (converted 24/08/2026; writes confirmed) |
| Superseded xlsx | `1yI5bB7hoFYWWH8ml4vgsFKeHt0gbtH-P` — frozen snapshot, do not write |
| Worksheet gids | `Deal Tracker` = 691243873 · `Stage Legend` = 1719303824 |
| Header row | 1 — data starts at row 2, so ID *N* sits on row *N+1* |

Columns, in order: Deal Tracker ID (column A's header is literally this, not
"ID") · Deal / Lead · Company / Counterparty · Contact(s) · Product / Ask ·
Volume / Scope · Value / Terms · Stage · Last Contact · Next Step.

Stage is a controlled vocabulary in priority order — never invent one:
Committed/Closing · Quote Sent · Negotiating · Active - POC Running · Meeting
Scheduled · Discovery · Backlog · Parked / Not Now.

Write path: Zapier Google Sheets (`GoogleSheetsV2CLIAPI`) — `lookup_row`,
`update_row`, `add_row`. The connection for `nadav.delgo@gmail.com` is already
authorised. The Sheets API cannot address an uploaded .xlsx, which is why the
file had to become a native Sheet. Never rebuild it by re-uploading bytes: it
breaks the link and risks a live commercial record.

Row 10 is the Israeli buildout — everything from Amizur routes there.

Never write a figure Ken did not state, and never overwrite the commercial
history in `Value / Terms`. It is the audit trail of a live negotiation.

## Calendar suggestions

Events are **suggested, never created** — creating one mails invitations to
other people. A suggestion that lives only in a chat reply is invisible the
moment that session ends, and the runner fires eight times a day as fresh
sessions, so every suggestion also becomes a Google Task in the matching
workstream list.

| | |
|---|---|
| Persist as | Google Task |
| Title format | `📅 {who}, {when} — add to calendar?` |
| Due | the suggested event's date |
| Notes | source thread link plus one line of context |
| Lists | `Velocity + Apex` · `Tinu` · `Personal` |

Dedupe on who + when before adding; never stack duplicates for the same event.
The user dismisses a suggestion by deleting the task — do not recreate one that
was deleted for the same who + when in the same thread.

## Chat sources — WhatsApp

No API reads personal WhatsApp chats. Meta's Business Platform only exposes
messages sent *to* a business number inside a 24-hour window; it cannot see a
1:1 with Avishag or Ken, or an arbitrary group. There is no WhatsApp connector.
Anything claiming otherwise is an unofficial client that violates WhatsApp's
terms and risks the number.

The supported path is WhatsApp's own export: chat → ⋮ → More → Export chat →
Without media → save to Drive, into the folder **`WhatsApp Exports`**. A `.csv`
from a third-party tool is also accepted; the parser sniffs the header for
date/time/sender/message columns and refuses rather than guessing a column
order it does not recognise.

**Always parse an export with the parser script, never by reading the file.**
WhatsApp's format varies by platform, locale and phone language, and Hebrew
exports carry invisible bidirectional marks that defeat a naive read. The
symptom is the whole file parsing as a single enormous message, which then
writes nonsense into the roster with nothing looking broken.

Watched chats: **Avishag Bohbot** → Apex + VelocityX (most of the real traffic
happens here rather than in mail; decisions land in chat and only the artefacts
reach email). **Ken Hu** → Tinu (GPU procurement and customer quotes, Pacific
hours; every Ken chat also updates the deal tracker).

Rules: an export is read-only history, never reply into WhatsApp. Chat is a
**people** source as well as a task source — alumni news lands here that never
reaches email. An export is stale the moment it is taken, so trust email over
an older export when they conflict, and say which you used. A date agreed in
chat is a real date; a date guessed from chat is not.

## The Apex alumni roster

97 alumni with tier, tie strength, cadence, what each needs and can give, last
contact and next action. It is the source of truth for people — never answer
"what is X doing now" from memory.

Columns: id · name · name_he · cohort · founder_track · track · company · role ·
location · domain · tier · tie_strength · current_goal · needs · can_help ·
last_contact · last_source · next_action · next_action_due · linkedin · email ·
phone · source_note · notes.
