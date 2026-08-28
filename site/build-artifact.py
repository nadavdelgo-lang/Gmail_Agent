#!/usr/bin/env python3
"""Strip the standalone document wrapper so the page can be published as an Artifact.

The Artifact host wraps the file it is given in its own <!doctype>/<head>/<body>
skeleton, so everything between the ARTIFACT markers ships as-is.
"""
import pathlib, sys

root = pathlib.Path(__file__).resolve().parent
src = (root / "index.html").read_text(encoding="utf-8")
start, end = "<!--ARTIFACT:START-->", "<!--ARTIFACT:END-->"
if start not in src or end not in src:
    sys.exit("markers missing from index.html")
body = src.split(start, 1)[1].split(end, 1)[0].strip() + "\n"
out = root / "artifact.html"
out.write_text(body, encoding="utf-8")
print(f"wrote {out} ({len(body):,} bytes)")
