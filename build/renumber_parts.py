#!/usr/bin/env python3
"""Renumber figures and tables in a chapter's part-B file so they continue part A.

Part B authors number figures and tables from N.101. This script finds the highest
figure and table numbers used in part A (NN-*.md) and rewrites every N.1xx figure or
table reference in part B (NNb-*.md) to continue the sequence.

Usage: python3 build/renumber_parts.py 91 [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "manuscript" / "book3-interviews"


def main():
    num = int(sys.argv[1])
    dry = "--dry-run" in sys.argv
    part_a = sorted(BOOK.glob(f"{num:02d}-*.md"))
    part_b = sorted(BOOK.glob(f"{num:02d}b-*.md"))
    if len(part_a) != 1 or len(part_b) != 1:
        sys.exit(f"expected one part A and one part B file for chapter {num}")
    a_text, b_text = part_a[0].read_text(), part_b[0].read_text()

    def max_used(text, kind):
        nums = [int(m) for m in re.findall(rf"\*\*{kind}\s+{num}\.(\d+)", text)]
        return max([n for n in nums if n < 100], default=0)

    offsets = {"Figure": max_used(a_text, "Figure"), "Table": max_used(a_text, "Table")}
    token = re.compile(rf"(?<![\d.]){num}\.(1\d\d)(?!\d)")
    kind_word = re.compile(r"(Figures?|Fig\.|Tables?)", re.I)
    changes = {"Figure": {}, "Table": {}}

    def repl(m):
        # Decide whether this number is a figure or a table from the nearest keyword before it.
        window = b_text[max(0, m.start() - 60):m.start()]
        kinds = kind_word.findall(window)
        if not kinds:
            raise SystemExit(f"ambiguous reference {m.group(0)} near: {window!r}")
        kind = "Table" if kinds[-1].lower().startswith("tab") else "Figure"
        old = int(m.group(1))
        new = offsets[kind] + (old - 100)
        changes[kind][old] = new
        return f"{num}.{new}"

    new_b = token.sub(repl, b_text)
    for kind, mapping in changes.items():
        if mapping:
            print(f"{kind}s: part A ends at {num}.{offsets[kind]}; part B "
                  f"{num}.{min(mapping)}–{num}.{max(mapping)} → {num}.{mapping[min(mapping)]}–{num}.{mapping[max(mapping)]}")
    if not dry:
        part_b[0].write_text(new_b)
        print(f"rewrote {part_b[0].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
