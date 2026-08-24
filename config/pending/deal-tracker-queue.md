# Deal Tracker — pending writes

Rows extracted from Ken chats that could not be written because the tracker is
still an uploaded `.xlsx` (see `deal_tracker.writable` in `workstreams.yaml`).

Once the tracker is a native Google Sheet, apply these with the Zapier Google
Sheets actions, then delete the entry from this file. Do not re-apply an entry
that is already in the sheet — check by counterparty before writing.

---

## PENDING — new row, ID 13
**Source:** WhatsApp export "Ken x Liran", 20–23/08/2026 (uploaded 24/08/2026)
**Plus:** Google Doc "GB300 Access & Going forward" sent by Or Wilder 23/08 23:59
`https://docs.google.com/document/d/1nEydTFwknXNw7lMF8vFUL76KXm_bi8YpTQFBra2tIjk/edit`

| Column | Value |
|---|---|
| ID | 13 |
| Deal / Lead | GB300 cluster access for security research (Exploration → Deep Research) |
| Company / Counterparty | `[[NADAV: company name never stated in the chat — Liran Markin + Or Wilder. Possibly Mantissa, from the "Inception- Mantissa" mail thread, but unconfirmed. Confirm before writing.]]` |
| Contact(s) | Liran Markin, Or Wilder; Ken Hu (Tinu side); intro'd by Nadav 20/08 |
| Product / Ask | Bare-metal access to the GB300 cluster + BMC admin console. Explicitly **not** a compute purchase — "we don't currently require compute itself" (Or, chat 22/08) |
| Volume / Scope | Phase 1 Exploration: cluster-level and single-tenant access, management console, low-level CPU/BMC, CVE and version querying. Phase 2 Deep Research: may need to modify, partition or download firmware/software and run vulnerability assessment — scope to be proposed and agreed with Ken first. They state they will change nothing without prior authorization. |
| Value / Terms | Not quoted. **Partnership model for the exploration phase is an open question from them to Ken** (doc Q2). Ken raised InfiniBand as a possible separate opportunity for them (chat 23/08). |
| Stage | Discovery |
| Last Contact | 23/08/2026 |
| Next Step | Ken to answer the 7 exploration questions in Or's doc: (1) bare-metal + BMC admin access, (2) partnership model, (3) what access is normally given and who else is on the cluster, (4) access period, (5) which security methods to test — Ken raised orchestration layer and zero trust, (6) how GPU compute would be coordinated if needed, (7) who administers the cluster and at what permission level. Confirm company name. |

**Flag for Nadav, not for the sheet:** this asks for BMC-level admin access to a
live cluster that other tenants are running on — Ken probed exactly that on
22/08 and got "we won't change anything that might affect others". Phase 2
contemplates firmware modification and vulnerability assessment. Pearl
Research's POC1 runs to 04/09 and that is a $28M prospect. Worth deciding
deliberately which cluster this access is on before answering question 1.
