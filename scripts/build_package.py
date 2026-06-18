#!/usr/bin/env python3
"""
build_package.py — package this skill into an installable, versioned .docx-safe zip.

WHY THIS EXISTS
Windows PowerShell 5.1's `Compress-Archive` writes BACKSLASH path separators inside
the zip. The ZIP spec requires forward slashes, so skill installers reject such files
with "Zip file contains path with invalid characters." This script builds the archive
with Python's zipfile and forces forward-slash entry names, then verifies none slipped
through — so the package installs cleanly every time.

WHAT IT DOES
- Reads `name` and `version` from SKILL.md's frontmatter.
- Bundles SKILL.md + assets/ + references/ + scripts/ under a top-level folder named
  for the skill (so it installs under the right name), excluding build artifacts.
- Writes `<name>-v<major>.zip` (e.g. extend-brd-v1.zip) to the skill root.

USAGE (run from anywhere; paths are resolved relative to this file)
    python scripts/build_package.py            # -> extend-brd-v1.zip
    python scripts/build_package.py --full-version   # -> extend-brd-v1.0.0.zip
    python scripts/build_package.py --out dist/skill.zip
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCLUDE = ["SKILL.md", "assets", "references", "scripts"]
EXCLUDE_DIRS = {"__pycache__", ".git", ".claude", "memory", ".ipynb_checkpoints"}
EXCLUDE_FILES = {".DS_Store"}


def read_frontmatter():
    """Return (name, version) from SKILL.md's YAML frontmatter (no PyYAML needed)."""
    path = os.path.join(SKILL_ROOT, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        sys.exit("SKILL.md has no frontmatter block (expected leading '---').")
    block = m.group(1)
    name = re.search(r"^name:\s*(.+?)\s*$", block, re.MULTILINE)
    version = re.search(r"^version:\s*(.+?)\s*$", block, re.MULTILINE)
    if not name:
        sys.exit("SKILL.md frontmatter is missing a 'name:' field.")

    # Guard: the skill installer rejects descriptions longer than 1024 chars.
    dm = re.search(r"^description:\s*>-?\s*\n(.*?)(?=^\S)", block + "\n", re.DOTALL | re.MULTILINE)
    if dm:
        desc = " ".join(ln.strip() for ln in dm.group(1).splitlines() if ln.strip())
        if len(desc) > 1024:
            sys.exit(f"SKILL.md description is {len(desc)} chars; the installer limit "
                     f"is 1024. Trim it by {len(desc) - 1024}+ chars before packaging.")

    return name.group(1).strip(), (version.group(1).strip() if version else None)


def files_to_add():
    for item in INCLUDE:
        p = os.path.join(SKILL_ROOT, item)
        if os.path.isfile(p):
            yield p, item
        elif os.path.isdir(p):
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
                for f in filenames:
                    if f in EXCLUDE_FILES:
                        continue
                    full = os.path.join(dirpath, f)
                    yield full, os.path.relpath(full, SKILL_ROOT)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full-version", action="store_true",
                    help="Name the zip with the full version (v1.0.0) instead of major only (v1).")
    ap.add_argument("--out", default=None, help="Explicit output path (overrides the derived name).")
    args = ap.parse_args(argv)

    name, version = read_frontmatter()
    if args.out:
        out = os.path.abspath(args.out)
    else:
        if version:
            tag = version if args.full_version else "v" + version.split(".")[0]
            if not tag.startswith("v"):
                tag = "v" + tag
        else:
            tag = "v0"
        out = os.path.join(SKILL_ROOT, f"{name}-{tag}.zip")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        os.remove(out)

    entries = sorted(files_to_add(), key=lambda t: t[1])
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for full, rel in entries:
            arc = name + "/" + rel.replace(os.sep, "/")  # forward slashes, always
            z.write(full, arc)

    # verify: forward slashes only, expected root, non-empty
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        bad = [n for n in names if "\\" in n]
        if bad:
            sys.exit(f"ERROR: {len(bad)} entries still contain backslashes: {bad[:3]}")
        if not all(n.startswith(name + "/") for n in names):
            sys.exit(f"ERROR: not all entries are under '{name}/'.")

    print(f"Built {out} ({os.path.getsize(out) // 1024} KB, {len(names)} entries) "
          f"— skill '{name}'" + (f" v{version}" if version else ""))
    for n in names:
        print("  ", n)
    print("Path separators OK (forward slashes); ready to install.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
