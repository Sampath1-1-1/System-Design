#!/usr/bin/env python3
"""Extracts every fenced code block in a programming language from the manuscript into
code/chNN/listing-KK-<section>.<ext>, so examples can be run and updated outside the book.
Regenerated on each run; the manuscript stays the source of truth."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXT = {"python": "py", "go": "go", "java": "java", "c": "c", "sql": "sql", "bash": "sh",
       "javascript": "js", "protobuf": "proto", "proto": "proto", "graphql": "graphql", "yaml": "yaml"}
COMMENT = {"py": "#", "sh": "#", "yaml": "#", "graphql": "#", "sql": "--"}
BLOCK = re.compile(r"^```(\w+)[^\n]*\n(.*?)^```\s*$", re.S | re.M)

for f in sorted((ROOT / "manuscript").glob("book*/[0-9][0-9]*-*.md")):
    num = int(f.name[:2])
    out = ROOT / "code" / f"ch{num:02d}"
    text = f.read_text()
    blocks = [(m.start(), m.group(1).lower(), m.group(2)) for m in BLOCK.finditer(text) if m.group(1).lower() in EXT]
    if not blocks:
        continue
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("listing-*"):
        old.unlink()
    for k, (pos, lang, code) in enumerate(blocks, 1):
        secs = re.findall(r"^#{2,3}\s+(\d+\.\d+(?:\.\d+)?)\s", text[:pos], re.M)
        sec = secs[-1] if secs else str(num)
        ext = EXT[lang]
        c = COMMENT.get(ext, "//")
        header = f"{c} Extracted from {f.relative_to(ROOT)} §{sec} (listing {k}). Edit the manuscript, not this file.\n"
        (out / f"listing-{k:02d}-s{sec.replace('.', '_')}.{ext}").write_text(header + code)
    print(f"ch{num:02d}: {len(blocks)} listing(s)")
