#!/usr/bin/env python3
"""Rewrites the section list of each drafted chapter in docs/project/01-master-toc.md
from the chapter's actual `## N.M` headings (end matter excluded)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOC = ROOT / "docs" / "project" / "01-master-toc.md"
SKIP = re.compile(r"Learning objectives|Prerequisites|Summary|Knowledge checkpoint|Interview questions|"
                  r"Practical exercises|Design challenges|References|Open verification", re.I)

toc = TOC.read_text()
changed = 0
for f in sorted((ROOT / "manuscript").glob("book*/[0-9][0-9]-*.md")):
    num = int(f.name[:2])
    secs, in_code = [], False
    for ln in f.read_text().splitlines():
        if ln.startswith("```"):
            in_code = not in_code
            continue
        m = None if in_code else re.match(r"^##\s+(\d+\.\d+)\s+(.+)$", ln)
        if m and not SKIP.search(m.group(2)):
            secs.append(f"{m.group(1)} {m.group(2).strip()}")
    mm = re.search(r"(\*\*Ch " + str(num) + r" — [^\n]*\n)([^\n]*\n)", toc)
    if mm and secs:
        toc = toc[:mm.start(2)] + " · ".join(secs) + "\n" + toc[mm.end(2):]
        changed += 1
TOC.write_text(toc)
print(f"synced {changed} chapter(s)")
