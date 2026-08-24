# Deal Tracker — pending writes

Rows extracted from Ken chats that could not be written because the tracker was
not writable (see `deal_tracker.writable` in `workstreams.yaml`).

Append here when a write is impossible so the extraction is not lost. On a later
run, if the tracker is writable, flush the queue into the sheet — matching by
counterparty so an entry already applied is not written twice — then delete what
you applied.

**Queue is empty.** Row 13 (GB300 cluster access for security research, Liran
Markin / Or Wilder) was written to the sheet on 24/08/2026.
