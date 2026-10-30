#!/usr/bin/env python3
"""Converts a built volume (dist/<name>.html) into a page for publishing as a claude.ai Artifact:
strips the document skeleton, adds the title, fonts and viewport-fit meta, and prepends a status banner.

Usage: python3 build/make_artifact.py <dist/name.html> <out.html> "<Title>" "<banner html>"
"""
import re
import sys
from pathlib import Path

src, out, title, banner = sys.argv[1:5]
html = Path(src).read_text()
styles = "\n".join(re.findall(r"<style[^>]*>.*?</style>", html, re.S))
body = re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)
head = (f"<title>{title}</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700'
        '&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap">\n')
Path(out).write_text(head + styles + "\n" + banner + "\n" + body)
print(f"wrote {out} ({Path(out).stat().st_size/1e6:.1f} MB)")
