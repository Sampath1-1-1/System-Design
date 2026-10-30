#!/usr/bin/env python3
"""Builds a multi-page site for publishing as one claude.ai Artifact:
an index page (contents + status) and one standalone HTML page per part.

Usage: python3 build/make_artifact_site.py <out_dir>
Then publish <out_dir>/index.html with files={"part-NN.html": "<out_dir>/part-NN.html", ...}.
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
manifest = yaml.safe_load((BUILD / "book.yaml").read_text())
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

chapters = {c[0]: c for c in manifest["chapters"]}
part_starts = [p[0] for p in manifest["parts"]] + [max(chapters) + 1]
parts = []
for i, (start, title) in enumerate(manifest["parts"]):
    nums = list(range(start, part_starts[i + 1]))
    written = [n for n in nums if list((ROOT / "manuscript" / chapters[n][3]).glob(f"{n:02d}-*.md"))]
    parts.append((i + 1, title, nums, written))

pages = {}
for idx, title, nums, written in parts:
    if not written:
        continue
    name = f"part-{idx:02d}"
    rng = ",".join(str(n) for n in written)
    subprocess.run([sys.executable, str(BUILD / "build.py"), "--chapters", rng, "--name", name, "--formats", "html"],
                   check=True, capture_output=True)
    html = (ROOT / "dist" / f"{name}.html").read_text()
    (ROOT / "dist" / f"{name}.html").unlink()
    back = ('<p style="font-family:Inter,sans-serif;font-size:.9rem"><a href="index.html">← All parts</a></p>')
    html = html.replace("<title>The Complete System Design Knowledge Base — Preview</title>", f"<title>{title}</title>")
    html = re.sub(r"(<body[^>]*>)", r"\1" + back, html, count=1)
    (out / f"{name}.html").write_text(html)
    pages[name] = out / f"{name}.html"

subprocess.run(["git", "checkout", "--", "manuscript/appendices"], cwd=ROOT, check=False)

rows = []
for idx, title, nums, written in parts:
    items = []
    for n in nums:
        label = f"{n}. {chapters[n][2]}"
        items.append(f"<li class=\"{'done' if n in written else 'todo'}\">{label}</li>")
    head = (f'<a href="part-{idx:02d}.html">{title}</a>' if written else f"<span>{title}</span>")
    status = (f"{len(written)} of {len(nums)} chapters" if written else "planned")
    rows.append(f'<section class="part"><h2>{head}</h2><p class="status">{status}</p><ol>{"".join(items)}</ol></section>')

total = sum(len(p[3]) for p in parts)
index = f"""<title>System Design Knowledge Base</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Source+Serif+4:wght@400;600&display=swap">
<style>
/* Layout: single reading column; parts as a list of sections with chapter lists */
:root {{ --navy:#1B2A4A; --blue:#1F5FA8; --teal:#127A7A; --muted:#5B6574; --rule:#D8DEE6; --bg:#FFFFFF; --fg:#1F2328; --chip:#EEF4FB;
  --display:"Source Serif 4", Georgia, serif; --ui:Inter, "DejaVu Sans", sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --navy:#A9C1EC; --blue:#7FB0F0; --teal:#6CC7C7; --muted:#A8B0BA; --rule:#333A44; --bg:#121519; --fg:#E6E8EB; --chip:#17243A; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --navy:#A9C1EC; --blue:#7FB0F0; --teal:#6CC7C7; --muted:#A8B0BA; --rule:#333A44; --bg:#121519; --fg:#E6E8EB; --chip:#17243A; color-scheme: dark; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--ui); margin:0; }}
main {{ max-width:46rem; margin:0 auto; padding-block:2.5rem 4rem; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); display:grid; gap:1.25rem; }}
h1 {{ font-family:var(--display); color:var(--navy); font-size:2.1rem; margin:0; text-wrap:balance; }}
.lede {{ color:var(--muted); line-height:1.55; margin:0; }}
.part {{ border-top:1px solid var(--rule); padding-top:1rem; }}
.part h2 {{ font-size:1.05rem; margin:0; color:var(--navy); }}
.part h2 a {{ color:var(--blue); text-decoration:none; }}
.part h2 a:hover, .part h2 a:focus-visible {{ text-decoration:underline; }}
.status {{ font-size:.75rem; letter-spacing:.06em; text-transform:uppercase; color:var(--teal); margin:.3rem 0 .5rem; }}
ol {{ margin:0; padding-left:1.2rem; columns:2 18rem; column-gap:2rem; font-size:.88rem; line-height:1.6; list-style:none; padding-left:0; }}
li.todo {{ color:var(--muted); }}
li.done::before {{ content:"●"; color:var(--teal); font-size:.6rem; margin-right:.45rem; vertical-align:middle; }}
li.todo::before {{ content:"○"; font-size:.6rem; margin-right:.45rem; vertical-align:middle; }}
</style>
<main>
  <h1>System Design Knowledge Base</h1>
  <p class="lede">Preview edition. {total} of {len(chapters)} chapters are drafted and have passed cross-chapter review. Open a part to read it; each part page has its own table of contents. Filled dots mark written chapters.</p>
  {"".join(rows)}
</main>
"""
(out / "index.html").write_text(index)
print("pages:", ", ".join(sorted(pages)))
for p in sorted(pages.values()):
    print(f"  {p.name}: {p.stat().st_size / 1e6:.1f} MB")
