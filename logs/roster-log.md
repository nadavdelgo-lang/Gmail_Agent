# Roster provenance log

Append-only. One line per field change, newest at the bottom:

```
date | person | field | old → new | source
```

`source` is one of `call <date>`, `avishag-mail <date>`, `chat <file> <date>`,
`contacts-merge`, or `manual`.

This exists so that when a roster fact turns out to be wrong, it is possible to
see where it came from — whether the user heard it himself, Avishag mentioned
it in passing, or it was pulled out of a group chat. Second-hand facts are the
ones most likely to be stale, and without this column they are indistinguishable
from first-hand ones a month later.

Never rewrite or tidy a line. A correction is a new line.

---

2026-08-30 | — | — | roster seeded, 97 alumni | build_roster.py from Apex_Master_150726.xlsx
