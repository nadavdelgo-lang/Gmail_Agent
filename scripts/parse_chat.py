#!/usr/bin/env python3
"""Normalise a WhatsApp export into JSONL: {timestamp, sender, text}.

WhatsApp's export format varies by platform, locale and phone language, and a
Hebrew export is full of invisible bidirectional control characters that a
naive regex trips over — the usual symptom is the whole file parsing as one
enormous message. Getting that wrong silently corrupts the roster, so the
parsing is done here, deterministically and under test, rather than by reading
the file and eyeballing it.

Handles:
  Android   06/08/2026, 14:32 - Sender: text
  iOS       [06/08/2026, 14:32:05] Sender: text
  12-hour   06/08/2026, 2:32 PM - Sender: text
  dotted    6.8.2026, 14:32 - Sender: text
  CSV       exports from third-party tools, columns sniffed from the header

Usage:
    python3 scripts/parse_chat.py <export.txt|export.csv> [--since ISO] [--stats]
"""

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

# Bidi and formatting marks WhatsApp sprinkles through Hebrew exports. They are
# invisible, they sit in front of timestamps and sender names, and they are the
# single most common reason a Hebrew export fails to parse.
INVISIBLE = dict.fromkeys(map(ord, "‎‏‪‫‬⁦"
                                   "⁧⁨⁩﻿"), None)

DATE = r"(?P<d>\d{1,2})[./-](?P<m>\d{1,2})[./-](?P<y>\d{2,4})"
TIME = r"(?P<H>\d{1,2}):(?P<M>\d{2})(?::(?P<S>\d{2}))?\s*(?P<ampm>[APap]\.?[Mm]\.?)?"

# Android: "06/08/2026, 14:32 - "   iOS: "[06/08/2026, 14:32:05] "
HEADERS = [
    re.compile(rf"^\[{DATE},?\s+{TIME}\]\s*(?P<rest>.*)$"),
    re.compile(rf"^{DATE},?\s+{TIME}\s+-\s*(?P<rest>.*)$"),
]

# "Sender: text". Sender names do not contain a colon; message bodies often do,
# so only the first colon counts and only when the name in front of it is short
# enough to actually be a name.
SENDER = re.compile(r"^(?P<sender>[^:\n]{1,60}?):\s(?P<text>.*)$", re.S)

# Dropped outright — these are WhatsApp talking, not a person.
SYSTEM = re.compile(
    r"end-to-end encrypted|joined using this group|left$|created group|"
    r"changed the subject|changed this group's icon|added you|removed|"
    r"changed their phone number|security code changed|"
    r"ההודעות והשיחות מוצפנות|הצטרף|הצטרפה|יצא מהקבוצה|יצאה מהקבוצה|"
    r"שינה את הנושא|שינתה את הנושא|הוסיף|הוסיפה",
    re.I)

# Kept as a message but with no usable content — recorded so the timeline stays
# honest about a gap, then ignored by the extraction layer.
EMPTY = re.compile(
    r"^<Media omitted>$|^<המדיה הושמטה>$|^This message was deleted$|"
    r"^You deleted this message$|^הודעה זו נמחקה$|^מחקת הודעה זו$|"
    r"^null$|^<attached:.*>$",
    re.I)

CSV_FIELDS = {
    "timestamp": ["timestamp", "datetime", "date_time", "date and time", "when"],
    "date": ["date", "day", "תאריך"],
    "time": ["time", "שעה"],
    "sender": ["sender", "from", "author", "name", "contact", "user", "שולח"],
    "text": ["message", "text", "body", "content", "message_body", "הודעה"],
}


def clean(line: str) -> str:
    """Strip the invisible marks and normalise unicode spaces."""
    line = line.translate(INVISIBLE)
    line = "".join(" " if unicodedata.category(c) == "Zs" else c for c in line)
    return line.rstrip("\n\r")


def parse_stamp(g: dict) -> datetime:
    year = int(g["y"])
    if year < 100:                       # "26" → 2026
        year += 2000
    hour = int(g["H"])
    if g.get("ampm"):
        meridiem = g["ampm"].replace(".", "").lower()
        hour = hour % 12 + (12 if meridiem == "pm" else 0)
    # WhatsApp writes day-first in every locale this account uses.
    return datetime(year, int(g["m"]), int(g["d"]), hour, int(g["M"]),
                    int(g["S"] or 0))


def parse_text(raw: str) -> list[dict]:
    messages: list[dict] = []
    for line in raw.splitlines():
        line = clean(line)
        for header in HEADERS:
            match = header.match(line)
            if match:
                break
        if not match:
            # No timestamp: this is the continuation of the previous message.
            # Blank lines inside a message are real and preserved.
            if messages:
                messages[-1]["text"] += "\n" + line
            continue

        rest = match.group("rest").strip()
        if SYSTEM.search(rest):
            continue
        body = SENDER.match(rest)
        if not body:
            continue                     # system notice with no sender
        messages.append({
            "timestamp": parse_stamp(match.groupdict()).isoformat(),
            "sender": body.group("sender").strip(),
            "text": body.group("text").strip(),
        })

    return [m for m in messages if not EMPTY.match(m["text"].strip())]


def _column(header: list[str], key: str) -> str | None:
    lowered = {h.strip().lower(): h for h in header}
    for candidate in CSV_FIELDS[key]:
        if candidate in lowered:
            return lowered[candidate]
    return None


def parse_csv(raw: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        raise SystemExit("CSV has no header row — cannot tell the columns apart.")

    header = list(reader.fieldnames)
    sender_col = _column(header, "sender")
    text_col = _column(header, "text")
    stamp_col = _column(header, "timestamp")
    date_col, time_col = _column(header, "date"), _column(header, "time")

    missing = [n for n, c in (("sender", sender_col), ("message", text_col))
               if not c]
    if missing or not (stamp_col or date_col):
        raise SystemExit(
            f"Cannot map this CSV. Found columns {header}; need a sender, a "
            f"message and either a timestamp or a date. Rename the columns or "
            f"say which is which — guessing the order would put the wrong "
            f"words in someone's mouth.")

    messages = []
    for row in reader:
        stamp = (row.get(stamp_col) or
                 f"{row.get(date_col, '')} {row.get(time_col, '')}").strip()
        stamp = clean(stamp)
        m = re.match(rf"^{DATE},?\s+{TIME}$", stamp)   # same date logic as .txt
        parsed = parse_stamp(m.groupdict()) if m else None
        if parsed is None:
            try:
                parsed = datetime.fromisoformat(stamp)
            except ValueError:
                continue                              # unparseable row, skip
        text = clean(row.get(text_col) or "").strip()
        sender = clean(row.get(sender_col) or "").strip()
        if not sender or SYSTEM.search(text) or EMPTY.match(text):
            continue
        messages.append({"timestamp": parsed.isoformat(), "sender": sender,
                         "text": text})
    return messages


def parse(path: Path, since: str | None = None) -> list[dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    messages = parse_csv(raw) if path.suffix.lower() == ".csv" else parse_text(raw)
    if since:
        messages = [m for m in messages if m["timestamp"] > since]
    return messages


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("--since", help="ISO timestamp; only messages after it")
    ap.add_argument("--stats", action="store_true",
                    help="summarise instead of printing the messages")
    args = ap.parse_args()

    messages = parse(args.path, args.since)
    if args.stats:
        senders: dict[str, int] = {}
        for m in messages:
            senders[m["sender"]] = senders.get(m["sender"], 0) + 1
        print(f"{len(messages)} messages")
        if messages:
            print(f"  {messages[0]['timestamp']} → {messages[-1]['timestamp']}")
        for sender, n in sorted(senders.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>5}  {sender}")
        return
    for m in messages:
        print(json.dumps(m, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
