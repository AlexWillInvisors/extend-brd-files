#!/usr/bin/env python3
"""
scrape_extend_limits.py — offline maintenance crawler for Workday Extend limits.

WHAT IT DOES
Renders the public Workday developer documentation (a JavaScript SPA) with a real
headless browser, crawls seed + discovered pages under developer.workday.com, and
extracts every sentence that states a platform limit / maximum / threshold /
governor / quota. It writes the candidates to references/extend-limits.md, each one
quoted verbatim with its source URL, section heading, and the retrieval date, so the
extend-brd skill can cite a real, sourced constraint instead of guessing a number.

WHY A BROWSER (and not requests + BeautifulSoup)
developer.workday.com/documentation is a client-rendered SPA. A plain HTTP fetch
returns only the empty shell ("Workday Developers | Build on the Workday Platform")
with zero documentation text. Playwright runs the page's JavaScript so the real
content is in the DOM before we read it.

ONE-TIME SETUP (run on your own machine; this is NOT run during a BRD session)
    pip install playwright
    python -m playwright install chromium

USAGE
    # crawl the default seeds and discover outward, write the reference file
    python scripts/scrape_extend_limits.py

    # add specific known limit pages (paste the exact URLs you know about)
    python scripts/scrape_extend_limits.py \
        --seed https://developer.workday.com/documentation/extend/... \
        --seed https://developer.workday.com/documentation/...

    # tune the crawl
    python scripts/scrape_extend_limits.py --max-pages 120 --max-depth 4 --delay 1.0

    # see what would be crawled / extracted without writing the file
    python scripts/scrape_extend_limits.py --dry-run

OUTPUT
References/extend-limits.md has two zones separated by a sentinel marker:
  - Everything ABOVE  the AUTO-GENERATED marker is human-curated and PRESERVED across
    runs (put your hand-verified, canonical limits there).
  - Everything BELOW  the marker is regenerated on every run from the live crawl.
This lets you keep a trusted, edited top section while refreshing raw candidates.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Edit this list, or override per-run with --seed. The crawl starts here and
# follows in-scope links outward (seed + discover). Keep at least the docs root.
SEED_URLS = [
    "https://developer.workday.com/documentation",
]

# Only crawl pages on this host whose path starts with one of these prefixes.
# This keeps the crawler inside the documentation and off marketing/legal pages.
ALLOWED_HOST = "developer.workday.com"
ALLOWED_PATH_PREFIXES = ("/documentation",)

# robots.txt disallows these (verified 2026-06-17). Never crawl them.
DISALLOWED_PREFIXES = ("/terms/", "/extend-the-power-of-workday")

# Default output, relative to the skill root (this file lives in scripts/).
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "references" / "extend-limits.md"

AUTO_MARKER = "<!-- ===== AUTO-GENERATED BELOW THIS LINE — regenerated on every crawl; do not hand-edit ===== -->"

# ---------------------------------------------------------------------------
# Limit-sentence detection
# ---------------------------------------------------------------------------

# A candidate must contain BOTH a limit-signal word AND a number. This favors
# precision (real stated limits) over recall (everything that says "maximum").
_SIGNAL = re.compile(
    r"(?i)\b("
    r"limit(?:ed|s|ation)?|maximum|max\.?|minimum|min\.?|up to|no more than|"
    r"at most|cannot exceed|can\'?t exceed|exceeds?|capped? at|threshold|quota|"
    r"governor|restricted to|allowed|per (?:second|minute|hour|day|request|call|"
    r"transaction)|time(?:s)? out|timeout"
    r")\b"
)
# Units / nouns that make a number look like a real limit rather than a version etc.
_UNIT = re.compile(
    r"(?i)\b("
    r"second|minute|hour|day|row|record|field|object|attribute|character|byte|"
    r"kb|mb|gb|request|call|page|item|instance|entry|entries|transaction|concurrent"
    r")s?\b"
)
_HAS_NUMBER = re.compile(r"\d")


def looks_like_limit(sentence: str) -> bool:
    """True if a sentence plausibly states a platform limit."""
    s = sentence.strip()
    if len(s) < 12 or len(s) > 400:
        return False
    if not _HAS_NUMBER.search(s):
        return False
    if not _SIGNAL.search(s):
        return False
    # Require a unit OR an explicit "limit/maximum/quota" word to cut false hits
    # like "...in 2024 the maximum effort..." that have a number but no real cap.
    return bool(_UNIT.search(s) or re.search(r"(?i)\b(limit|maximum|quota|governor|cap)\b", s))


_SENT_SPLIT = re.compile(r"(?<=[.;:])\s+|\n+")


# A table whose header row contains one of these is a limits table: take EVERY data
# row, even rows with no signal word (e.g. "Number of business objects | 20 per app").
_LIMIT_HEADER = re.compile(r"(?i)\b(limit|maximum|max\.?|minimum|threshold|quota|cap)\b")


def table_candidates(tables) -> list[str]:
    """Build candidate lines from structured tables (list of tables; each a list of
    rows; each row a list of cell strings).

    - If the table's header row names a limit column, every data row with a number is
      a limit — joined as "label — value", no signal word required (catches the
      Model Components style: "Number of business objects | 20 per app").
    - Otherwise fall back to the prose heuristic on the joined row, so a stray limit
      in a non-limit table on a discovered page is still caught without dragging in
      every numeric table row.
    """
    out: list[str] = []
    for rows in tables or []:
        if not rows:
            continue
        header = rows[0]
        is_limit_table = any(_LIMIT_HEADER.search(c or "") for c in header)
        for row in rows[1:]:
            cells = [re.sub(r"\s+", " ", c).strip() for c in row if c and c.strip()]
            if not cells:
                continue
            line = " — ".join(cells)
            if not _HAS_NUMBER.search(line):
                continue  # skip header repeats / non-numeric rows
            if is_limit_table or looks_like_limit(line):
                out.append(line)
    return out


def extract_candidates(text: str, vetted_lines=None) -> list[str]:
    """Pull candidate limit statements out of a page, de-duplicated.

    `vetted_lines` are already-confirmed candidates (e.g. from `table_candidates`)
    added as-is — they are NOT re-tested against the prose heuristic, so a limit-table
    row that lacks a signal word survives.
    """
    seen: set[str] = set()
    out: list[str] = []

    def add(s: str):
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            return
        key = s.lower()
        if key not in seen:
            seen.add(key)
            out.append(s)

    for line in (vetted_lines or []):
        add(line)
    for chunk in _SENT_SPLIT.split(text):
        c = re.sub(r"\s+", " ", chunk).strip()
        if c and looks_like_limit(c):
            add(c)
    return out


# ---------------------------------------------------------------------------
# URL scope helpers
# ---------------------------------------------------------------------------

def in_scope(url: str) -> bool:
    try:
        p = urlparse(url)
    except ValueError:
        return False
    if p.scheme not in ("http", "https"):
        return False
    if p.netloc != ALLOWED_HOST:
        return False
    if any(p.path.startswith(d) for d in DISALLOWED_PREFIXES):
        return False
    return any(p.path.startswith(a) for a in ALLOWED_PATH_PREFIXES)


def normalize(url: str) -> str:
    """Drop fragments so #anchors on the same page aren't crawled as new pages."""
    return urldefrag(url)[0].rstrip("/")


# ---------------------------------------------------------------------------
# Crawl
# ---------------------------------------------------------------------------

def crawl(seeds, max_pages, max_depth, delay, headed, verbose):
    """BFS the docs with a headless browser. Returns {url: {title, candidates}}."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "Playwright is not installed. Run:\n"
            "    pip install playwright\n"
            "    python -m playwright install chromium"
        )
    import time

    results: dict[str, dict] = {}
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(normalize(u), 0) for u in seeds]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        page = browser.new_page()
        page.set_default_timeout(30000)

        while queue and len(visited) < max_pages:
            url, depth = queue.pop(0)
            if url in visited or not in_scope(url):
                continue
            visited.add(url)
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:  # noqa: BLE001 — keep crawling past a bad page
                if verbose:
                    print(f"  ! skip {url}: {e}", file=sys.stderr)
                continue

            title = (page.title() or url).strip()
            try:
                body_text = page.inner_text("body")
            except Exception:  # noqa: BLE001
                body_text = ""
            # Tables: limits are usually a "label | value" pair across cells, which
            # inner_text splits onto separate lines (losing the number from the label).
            # Pull the full structure (rows of cells) so table_candidates can detect a
            # limits table by its header and keep every data row, paired correctly.
            try:
                tables = page.evaluate(
                    "() => Array.from(document.querySelectorAll('table')).map("
                    "t => Array.from(t.querySelectorAll('tr')).map("
                    "tr => Array.from(tr.querySelectorAll('th,td')).map(c => c.innerText.trim())))"
                )
            except Exception:  # noqa: BLE001
                tables = []
            candidates = extract_candidates(body_text, vetted_lines=table_candidates(tables))
            if candidates:
                results[url] = {"title": title, "candidates": candidates}
            if verbose:
                print(f"  [{len(visited):>3}] depth {depth} +{len(candidates):>2} limits  {url}")

            if depth < max_depth:
                try:
                    hrefs = page.eval_on_selector_all(
                        "a[href]", "els => els.map(e => e.href)"
                    )
                except Exception:  # noqa: BLE001
                    hrefs = []
                for h in hrefs:
                    nu = normalize(urljoin(url, h))
                    if nu not in visited and in_scope(nu):
                        queue.append((nu, depth + 1))

            if delay:
                time.sleep(delay)

        browser.close()
    return results, visited


# ---------------------------------------------------------------------------
# Render the reference file
# ---------------------------------------------------------------------------

def render_auto_section(results, pages_crawled, run_date) -> str:
    total = sum(len(v["candidates"]) for v in results.values())
    lines = [
        AUTO_MARKER,
        "",
        f"## Auto-extracted limit candidates",
        "",
        f"> Crawled {pages_crawled} page(s) under {ALLOWED_HOST}; "
        f"found {total} candidate limit statement(s) on {len(results)} page(s).",
        f"> Retrieved: **{run_date}** via `scripts/scrape_extend_limits.py`.",
        "> Each line is quoted verbatim from the source page. These are *candidates* — "
        "confirm the value and context against the live doc before relying on it in a "
        "client BRD, then promote the trusted ones into the curated section above.",
        "",
    ]
    if not results:
        lines += [
            "_No limit statements were extracted on this run. The crawl may have been "
            "blocked, the seeds may be wrong, or the limit pages use wording the detector "
            "missed. Re-run with `--seed <exact-url>` and `--verbose`._",
            "",
        ]
        return "\n".join(lines)

    for url in sorted(results):
        entry = results[url]
        lines.append(f"### {entry['title']}")
        lines.append(f"Source: <{url}>")
        lines.append("")
        for c in entry["candidates"]:
            lines.append(f"- {c}")
        lines.append("")
    return "\n".join(lines)


CURATED_HEADER = """# Workday Extend — Platform Limits & Constraints

This is the extend-brd skill's source of truth for Workday Extend platform limits.
The skill consults it to (a) proactively flag, while authoring, any design element
that plausibly brushes a documented limit, and (b) run a full limits audit during a
BRD review. See SKILL.md ("Checking the design against Extend limits").

**Curated section (below, above the auto-generated marker): human-verified.**
Put limits you have confirmed against the live Workday documentation here, each with
its source URL and the date you verified it. This zone is PRESERVED across crawler
runs — the crawler only rewrites the auto-generated section beneath the marker.

Format each curated limit as:
- **<limit name>** — <value/threshold>. <scope / when it applies>. Source: <url> (verified <date>).

> Until a limit is verified here, treat any auto-extracted candidate below as
> unconfirmed and flag it in the BRD as `Open:`/`TBD` rather than asserting it.

## Curated limits (verified)

_None recorded yet — populate from the candidates below as you verify them._

"""


def write_reference(out_path: Path, auto_section: str):
    """Preserve the curated zone above the marker; replace the auto zone below it."""
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        if AUTO_MARKER in existing:
            curated = existing.split(AUTO_MARKER)[0].rstrip() + "\n\n"
        else:
            # First time the marker is introduced into an existing hand-written file:
            # keep all current content as the curated zone.
            curated = existing.rstrip() + "\n\n"
    else:
        curated = CURATED_HEADER
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(curated + auto_section + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", action="append", default=[], metavar="URL",
                    help="Add a seed URL (repeatable). Added to the built-in SEED_URLS.")
    ap.add_argument("--only-seeds", action="store_true",
                    help="Crawl ONLY the given/built-in seeds; do not discover links.")
    ap.add_argument("--max-pages", type=int, default=80, help="Max pages to visit (default 80).")
    ap.add_argument("--max-depth", type=int, default=3, help="Max link depth from seeds (default 3).")
    ap.add_argument("--delay", type=float, default=0.5, help="Seconds to wait between pages (default 0.5).")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"Output file (default {DEFAULT_OUT}).")
    ap.add_argument("--date", default=None, help="Override the retrieval date stamp (YYYY-MM-DD).")
    ap.add_argument("--headed", action="store_true", help="Run the browser visibly (debugging).")
    ap.add_argument("--dry-run", action="store_true", help="Crawl and print a summary; do not write the file.")
    ap.add_argument("--verbose", "-v", action="store_true", help="Print each page as it is crawled.")
    args = ap.parse_args(argv)

    seeds = SEED_URLS + args.seed
    max_depth = 0 if args.only_seeds else args.max_depth

    # Date is passed in (not derived) so output is reproducible and to avoid relying
    # on a wall clock; default to today via the date module only here at the edge.
    run_date = args.date
    if run_date is None:
        from datetime import date
        run_date = date.today().isoformat()

    print(f"Crawling from {len(seeds)} seed(s); max_pages={args.max_pages} max_depth={max_depth}")
    results, visited = crawl(
        seeds, args.max_pages, max_depth, args.delay, args.headed, args.verbose
    )
    total = sum(len(v["candidates"]) for v in results.values())
    print(f"Visited {len(visited)} page(s); extracted {total} candidate limit(s) from {len(results)} page(s).")

    auto = render_auto_section(results, len(visited), run_date)
    if args.dry_run:
        print("\n--- DRY RUN: auto-generated section preview ---\n")
        print(auto)
        return 0

    write_reference(args.out, auto)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
