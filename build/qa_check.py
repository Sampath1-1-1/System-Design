#!/usr/bin/env python3
"""Automated QA checks (supports Reviews 1, 4, 5, 7) and progress-tracker generation.

  python3 build/qa_check.py            # print findings per chapter
  python3 build/qa_check.py --tracker  # also regenerate docs/project/progress-tracker.md

Manual review status lives in build/status.yaml (research/draft/diagrams/review/final per chapter).
"""
import argparse
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript"
BUILD = ROOT / "build"
TRACKER = ROOT / "docs" / "project" / "progress-tracker.md"

REQUIRED_END = ["Summary", "Knowledge checkpoint", "Interview questions", "Practical exercises",
                "Design challenges", "References", "Open verification items"]
CALLOUT_CLASSES = {"definition", "concept", "example", "formula", "tip", "recommendation",
                   "mistake", "warning", "industry", "note", "summary"}
TERM_AVOID = [r"\bmaster/slave\b", r"\bslave\b", r"\boptimis", r"\bbehaviour\b", r"\butilis"]


def check_chapter(num, files):
    text = "\n".join(f.read_text() for f in files)
    lines = text.splitlines()
    findings = []
    in_code = False
    h1, last_level = 0, 0
    for ln in lines:
        if ln.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s", ln)
        if m:
            level = len(m.group(1))
            if level == 1:
                h1 += 1
            if last_level and level > last_level + 1:
                findings.append(f"heading level skip: {ln[:60]}")
            last_level = level
    if h1 != 1:
        findings.append(f"expected exactly one H1, found {h1}")

    h2 = re.findall(r"^##\s+(.+)$", text, re.M)
    for req in REQUIRED_END:
        if not any(req.lower() in h.lower() for h in h2):
            findings.append(f"missing end-matter section: {req}")

    mermaid = [m.start() for m in re.finditer(r"^```mermaid", text, re.M)]
    for pos in mermaid:
        before = text[max(0, pos - 600):pos]
        end = text.find("\n```", pos + 10)
        if not re.search(r"\*\*Figure\s+\d+\.\d+", before):
            findings.append(f"diagram without Figure caption near offset {pos}")
        if "Reading the diagram" not in text[end:end + 3000]:
            findings.append(f"diagram without 'Reading the diagram' near offset {pos}")

    figs = [int(n) for c, n in re.findall(r"\*\*Figure\s+(\d+)\.(\d+)", text) if int(c) == num]
    wrong = [c for c, _ in re.findall(r"\*\*Figure\s+(\d+)\.(\d+)", text) if int(c) != num]
    if wrong:
        findings.append(f"figure numbers with wrong chapter prefix: {sorted(set(wrong))}")
    if figs and figs != list(range(1, len(figs) + 1)):
        findings.append("figure numbers not sequential")
    tables = [int(n) for c, n in re.findall(r"\*\*Table\s+(\d+)\.(\d+)", text) if int(c) == num]
    if tables and tables != list(range(1, len(tables) + 1)):
        findings.append("table numbers not sequential")

    for m in re.finditer(r"^:::\s*\{?\.?([a-z]+)\}?\s*$(.*?)^:::\s*$", text, re.S | re.M):
        cls, body = m.group(1), m.group(2)
        if cls not in CALLOUT_CLASSES:
            findings.append(f"unknown callout class: {cls}")
        if cls == "industry" and "Evidence:" not in body:
            findings.append("industry callout without evidence label")
        if cls == "formula" and "|" not in body:
            findings.append("formula callout without variable table")

    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    for pat in TERM_AVOID:
        hits = re.findall(pat, prose, re.I)
        if hits:
            findings.append(f"terminology: '{hits[0]}' ×{len(hits)} (see terminology.md)")

    stats = {
        "words": len(re.findall(r"\w+", prose)),
        "figures": len(mermaid),
        "tables": len(tables),
        "formulas": len(re.findall(r"^:::\s*formula", text, re.M)),
        "industry": len(re.findall(r"^:::\s*industry", text, re.M)),
    }
    return stats, findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", action="store_true")
    args = ap.parse_args()
    manifest = yaml.safe_load((BUILD / "book.yaml").read_text())
    status_file = BUILD / "status.yaml"
    status = yaml.safe_load(status_file.read_text()) if status_file.exists() else {}
    status = status or {}

    rows, total_words = [], 0
    for num, slug, title, book, level, track in manifest["chapters"]:
        folder = MANUSCRIPT / book
        files = sorted(folder.glob(f"{num:02d}-*.md")) + sorted(folder.glob(f"{num:02d}[a-z]-*.md"))
        st = status.get(num, {})
        if files:
            stats, findings = check_chapter(num, files)
            total_words += stats["words"]
            print(f"Ch {num:>2} {title[:48]:<48} {stats['words']:>6} w  {stats['figures']:>2} fig  "
                  f"{len(findings)} finding(s)")
            for f in findings:
                print(f"        - {f}")
        else:
            stats, findings = None, []
        rows.append((num, title, level, track, stats, findings, st))

    if args.tracker:
        out = ["# Progress Tracker", "",
               "Generated by `python3 build/qa_check.py --tracker`. Automatic columns come from the manuscript; "
               "status columns come from `build/status.yaml`.",
               "", "Legend: ✅ done · 🟡 in progress · ⬜ not started · 🔁 needs revision", "",
               f"**Manuscript size:** {total_words:,} words "
               f"(≈ {total_words // 450:,} printed pages) across "
               f"{sum(1 for r in rows if r[4])} of {len(rows)} chapters.", "",
               "| Ch | Title | Lvl | Research | Draft | Diagrams | Review | Final | Words | Figs | Tables | QA flags |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        icon = {"done": "✅", "wip": "🟡", "todo": "⬜", "revise": "🔁"}
        for num, title, level, track, stats, findings, st in rows:
            cols = [icon.get(st.get(k, "todo"), "⬜") for k in ("research", "draft", "diagrams", "review", "final")]
            if stats:
                auto = [f"{stats['words']:,}", str(stats["figures"]), str(stats["tables"]), str(len(findings))]
            else:
                auto = ["—", "—", "—", "—"]
            out.append(f"| {num} | {title} | {level} | " + " | ".join(cols) + " | " + " | ".join(auto) + " |")
        out += ["", "## Appendices", "",
                "| Appendix | Status |", "|---|---|",
                "| A Glossary | ⬜ |", "| B Bibliography | ⬜ |",
                "| C Formula handbook | 🟡 auto-generated from chapters |",
                "| D Diagram collection | 🟡 auto-generated from chapters |",
                "| E Learning roadmap | ⬜ |", "| F Reference numbers | ⬜ |",
                "| G Comparison tables index | ⬜ |", "| H Unresolved questions | 🟡 `docs/project/unresolved-questions.md` |",
                "| I Index | ⬜ |", ""]
        TRACKER.write_text("\n".join(out))
        print(f"wrote {TRACKER}")


if __name__ == "__main__":
    main()
