#!/usr/bin/env python3
"""Build the publishable page from index.html.

Two things happen here:

1. The standalone <!doctype>/<head> wrapper is stripped, because the Artifact
   host wraps the file it is given in its own skeleton.
2. The page is given a base64 copy of its own source, in the #shell slot. That
   is what lets a viewer's edit publish a complete replacement document: the
   page fills %%STATE%% with the new content and %%SHELL%% with the shell
   again, so every generation can rebuild the next one.
"""
import base64, pathlib, sys

root = pathlib.Path(__file__).resolve().parent
src = (root / "index.html").read_text(encoding="utf-8")

start, end = "<!--ARTIFACT:START-->", "<!--ARTIFACT:END-->"
if start not in src or end not in src:
    sys.exit("markers missing from index.html")

shell = src.split(start, 1)[1].split(end, 1)[0].strip() + "\n"
for slot in ("%%SHELL%%", "%%STATE%%"):
    if shell.count(slot) != 1:
        sys.exit(f"expected exactly one {slot} in index.html, found {shell.count(slot)}")

packed = base64.b64encode(shell.encode("utf-8")).decode("ascii")
out_text = shell.replace("%%SHELL%%", packed).replace("%%STATE%%", "{}")

out = root / "artifact.html"
out.write_text(out_text, encoding="utf-8")
print(f"wrote {out} ({len(out_text):,} bytes; shell {len(shell):,})")
