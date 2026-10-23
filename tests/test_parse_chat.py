#!/usr/bin/env python3
"""Regression tests for scripts/parse_chat.py.

The failure mode this guards against is silent: a Hebrew export whose bidi
marks defeat the header regex parses as one giant message, and the extraction
layer downstream then writes nonsense into the roster without anything looking
broken. So the assertions are about message *counts* and boundaries, not just
"it ran".

    python3 tests/test_parse_chat.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import parse_chat                                            # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
failures: list[str] = []


def check(label: str, actual, expected) -> None:
    if actual != expected:
        failures.append(f"{label}\n     expected: {expected!r}\n     actual:   {actual!r}")
    print(f"  {'ok  ' if actual == expected else 'FAIL'} {label}")


def test_android_en() -> None:
    msgs = parse_chat.parse(FIXTURES / "android_en.txt")
    check("android: 4 real messages, system lines dropped", len(msgs), 4)
    check("android: encryption notice dropped",
          any("end-to-end" in m["text"] for m in msgs), False)
    check("android: join notice dropped",
          any("joined using" in m["text"] for m in msgs), False)
    check("android: <Media omitted> dropped",
          any("Media omitted" in m["text"] for m in msgs), False)
    check("android: multi-line message stays whole",
          msgs[2]["text"].count("\n"), 2)
    check("android: sender parsed", msgs[0]["sender"], "Avishag Bohbot")
    check("android: apostrophe in body survives", msgs[1]["text"],
          "Not yet. I'll chase her today.")
    check("android: timestamp is day-first", msgs[0]["timestamp"],
          "2026-08-06T09:15:00")


def test_ios_hebrew() -> None:
    msgs = parse_chat.parse(FIXTURES / "ios_he.txt")
    # The whole point: RTL marks must not collapse the file into one message.
    check("hebrew: 4 messages, not 1", len(msgs), 4)
    check("hebrew: sender has no invisible marks", msgs[0]["sender"],
          "אבישג בוחבוט")
    check("hebrew: sender name is not mangled", msgs[1]["sender"], "נדב דלג׳ו")
    check("hebrew: multi-line stays whole", msgs[2]["text"].count("\n"), 1)
    check("hebrew: deleted-message placeholder dropped",
          any("נמחקה" in m["text"] for m in msgs), False)
    check("hebrew: media placeholder dropped",
          any("הושמטה" in m["text"] for m in msgs), False)
    check("hebrew: iOS seconds parsed", msgs[0]["timestamp"],
          "2026-08-06T09:14:02")
    check("hebrew: latin brand names survive mid-Hebrew",
          "AI Infra" in msgs[2]["text"], True)


def test_twelve_hour_and_dotted() -> None:
    msgs = parse_chat.parse(FIXTURES / "android_12h.txt")
    check("12h: 3 messages", len(msgs), 3)
    check("12h: AM parsed", msgs[0]["timestamp"], "2026-08-06T09:14:00")
    check("12h: PM parsed", msgs[1]["timestamp"], "2026-08-06T14:32:00")
    check("12h: 11:59 PM does not wrap to midday", msgs[2]["timestamp"],
          "2026-08-06T23:59:00")
    check("12h: unsaved contact kept as a phone number", msgs[0]["sender"],
          "+972 54-123-4567")


def test_csv() -> None:
    msgs = parse_chat.parse(FIXTURES / "export.csv")
    check("csv: 3 messages, placeholder dropped", len(msgs), 3)
    check("csv: columns sniffed from a non-standard header",
          msgs[0]["sender"], "Avishag Bohbot")
    check("csv: date + time columns combined", msgs[0]["timestamp"],
          "2026-08-06T09:15:00")


def test_since_filter() -> None:
    msgs = parse_chat.parse(FIXTURES / "android_en.txt",
                            since="2026-08-06T23:59:00")
    check("since: only the later day survives", len(msgs), 1)
    check("since: idempotent re-read yields nothing",
          len(parse_chat.parse(FIXTURES / "android_en.txt",
                               since="2026-08-07T11:02:00")), 0)


def test_colon_in_body() -> None:
    """A message body full of colons must not be mistaken for a sender."""
    msgs = parse_chat.parse_text(
        "06/08/2026, 09:15 - Nadav Delgo: Meeting: Tuesday: 11:00 sharp\n")
    check("colons: sender is the name, not the first word",
          msgs[0]["sender"], "Nadav Delgo")
    check("colons: body kept intact", msgs[0]["text"],
          "Meeting: Tuesday: 11:00 sharp")


if __name__ == "__main__":
    for test in (test_android_en, test_ios_hebrew, test_twelve_hour_and_dotted,
                 test_csv, test_since_filter, test_colon_in_body):
        print(f"\n{test.__name__}")
        test()
    print()
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("all parser tests passed")
