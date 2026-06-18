# Template anatomy — `assets/brd-template.docx`

Everything in this file was verified against the actual template (`Extend Deploy -
BRD v6.1.26`). When in doubt, re-inspect the file rather than trusting this
document — if they ever disagree, the file wins.

## What the template carries (and why you must not rebuild it)

- **Cover image**: `word/media/image2.jpeg` (~1.1 MB topographic cover) plus
  `image1.png` / `image2.png` (logos). Regenerating these is impossible.
- **Font**: **Lato** (set in `styles.xml`). Not Calibri, not Arial. Leave the
  template's styles alone — new content inherits them automatically.
- **Brand teal**: appears as `005865` and `007788` in styles. Don't hand-apply
  colors; the styles already do it.
- **Table of contents**: a real Word TOC field. After you pack, page numbers
  show stale until the user opens the doc and Word recalculates. This is normal —
  do not try to fix TOC page numbers by hand.
- **Footer**: "Elevating Perspective + Transforming Results" and "Invisors
  Proprietary and Confidental" [sic — the typo is in the template; do not
  "correct" it unless asked]. Preserved automatically by editing in place.

## Heading / title style IDs (already defined — reference, don't redefine)

| Element | Style ID |
|---|---|
| App-name title (top of cover) | `Heading5` |
| "Prepared for [CLIENT]" | `Subtitle` |
| Section headers (Business Requirements, Features, …) | `Heading1` |
| Appendix subsections (UI Mockups, Business Objects, …) | `Heading2` |
| TOC entries | `TOC1` / `TOC2` |

New section content should reuse these existing styles. When adding a
project-specific Appendix subsection, style its header `Heading2` to match UI
Mockups / Model Components / Business Objects / Security Domains.

## Placeholder tokens to find-and-replace (new BRD)

Title block:

| Token | Replace with |
|---|---|
| `[Extend/BoW App Name]` | The app name (e.g. "CER — Mass Engagement Letter Rollover") |
| `Prepared for [CLIENT]` | "Prepared for <Client>" |
| `DD-Month-Year` | The date (e.g. "June 2025") |

Body placeholders:

| Location | Placeholder text to replace |
|---|---|
| Business Requirements | `Summary of our understanding of the business problems we are solving for and what the solution will bridge the gap for.` |
| Feature table — header cell | `Use an active verb phrase to describe this feature` → `<N> — <active verb phrase>` (the table's first row label is **Feature #** / **Feature**) |
| Feature table — Goal | `Describe in one or two sentences the scope and content of the use case. Do not describe the flow of events, business or data validation rules.` |
| Feature table — Business Event/Trigger | `These are triggers that simulate activity within the business. …` |
| Feature table — Primary Actor(s) | `Identify the actor initiating the use case` |
| Feature table — Actor(s) | `Identify the secondary actor` |
| Feature table — Pre-conditions | `Identify pre-conditions that must be met …` |
| Feature table — Post-conditions | `Describe how the use case is successfully complete. …` |
| Feature table — Flow of Events | `Describe what the actor does and how the system responds` |
| Feature flow diagram slot | `[[Insert Feature Flow Diagram]]` |
| Integrations | `The following integrations are required to transmit data between Workday and external systems.` (keep/adapt the lead sentence; fill the empty table rows) |
| Data Retention | `Store key payment data (status, method, …)` — example text from a different engagement; **replace entirely** |
| Security Requirements | `Security roles to facilitate the application's processes will be created/managed include. [[Client]] will own creation …` (fill the empty role table, or set `TBD`) |
| Language Translations | `The Extend app will be available in US English, US Spanish, and French-Canadian. …` — **stock text; do NOT keep by default.** Replace with an **English-only** statement ("The Extend app will be available in US English.") unless a specific multi-language set is explicitly confirmed for the engagement |
| Mobile App Compatibility | `Extend app functionality is not needed on the Workday Mobile App.` — stock; confirm |
| Appendix → UI Mockups | `[Insert images]` |
| Appendix → Business Objects / Security Domains | The example rows are from a different engagement (Promotion Nomination…); **replace with this app's objects**, or state "No new business objects are introduced" when true |

**The Features section ships THREE stub use-case tables.** These are vertical
label/value tables (`Feature #`, Goal, Business Event/Trigger, Primary Actor(s),
Actor(s), Pre-conditions, Post-conditions, Flow of Events) — **not** header+data-row
tables, so `fill_table_rows` does NOT fit them. Use **`fill_process_table(tbl,
fields)`** to fill one (it matches each row by label and supports multi-paragraph
Flow of Events). Fill one table per real feature. To add more, use
**`add_process_table()`** (clones a table with valid fresh ids) — do NOT hand-clone a
`<w:tbl>` and hand-generate `w14:paraId`s; random ids can land ≥ `0x80000000`, which
pack-time validation rejects. To remove a stub, delete its `<w:tbl>` and the
following `[[Insert Feature Flow Diagram]]` paragraph.

## Mechanics

### New BRD — find-and-replace flow

```bash
cp assets/brd-template.docx working.docx
python /mnt/skills/public/docx/scripts/office/unpack.py working.docx unpacked/
# edit unpacked/word/document.xml — prefer brd_edit.py (set_run_text, fill_table_rows,
#   fill_process_table / add_process_table) over raw string edits
python /mnt/skills/public/docx/scripts/office/pack.py unpacked/ output.docx --original working.docx
```

**`pack.py` writes NO output file when validation fails** — so a later `validate.py`
on the expected path reports "file does not exist," which is confusing. If pack
reports a validation failure, fix the XML and repack; don't chase the missing file.

- Use the **Edit tool for string replacement**, not a Python script (per the docx
  skill). The unpack step pretty-prints and merges runs, so placeholder text is
  usually contiguous in one `<w:t>`.
- **Split-run placeholders.** A few placeholders are NOT contiguous in the raw XML —
  Word splits them across runs (the title `[Extend/BoW App Name]` is `[`+`Extend`+`/`
  +`BoW`+` App Name]` with `<w:proofErr>` spell markers interleaved; the Business
  Requirements "Summary of our understanding…" sentence is split too). A plain Edit on
  the raw file then finds nothing. `brd_edit.py` handles this automatically: its
  text-anchor methods call `merge_runs()` (which merges adjacent same-property runs —
  comparing `rPr` by exclusive C14N so namespace noise doesn't block it — and drops
  `proofErr` markers) the first time an anchor isn't found, so anchors resolve **with
  or without** the docx skill's `unpack.py`. If you hand-edit instead of using the
  helper, run `unpack.py` first or these anchors won't match.
- **Smart quotes**: when adding apostrophes/quotes, use XML entities
  (`&#x2019;` for ’, `&#x201C;`/`&#x201D;` for “ ”) so they render as professional
  typography. The example uses smart quotes throughout (user's, "el" records).
- **Tables**: when cloning a process table or filling Integration/Reporting rows,
  preserve the existing cell structure and shading — copy an existing
  `<w:tr>` and edit its text rather than authoring a row from scratch.

### Revision round — tracked changes

When editing an existing BRD the user supplies (not a fresh template fill), make
**tracked changes** so the user can review:

- Author every change as **"Claude"** (`w:author="Claude"`).
- Replace the whole `<w:r>…</w:r>` with `<w:del>…</w:del>` + `<w:ins>…</w:ins>`
  siblings; copy the original `<w:rPr>` into both so formatting is preserved.
- Mark only what changes — minimal, surgical edits.
- When deleting an entire paragraph, also mark the paragraph mark deleted
  (`<w:del/>` inside `<w:pPr><w:rPr>`) so accepting doesn't leave an empty para.
- Full patterns: the Tracked Changes section of `/mnt/skills/public/docx/SKILL.md`.

### Validation

```bash
python /mnt/skills/public/docx/scripts/office/validate.py output.docx
```

If it fails: unpack, fix the XML, repack. Don't deliver an unvalidated file.

## Use the `brd_edit.py` helper — don't hand-splice XML

The bundled helper `assets/brd_edit.py` is the **required** tool for all content
insertion and tracked-change edits. It operates on a parsed lxml tree, so every
edit is well-formed and schema-legal by construction — eliminating the orphaned
closing tags and run-in-run nesting that hand-splicing `</w:r></w:p><w:p>…`
repeatedly produces (those only surface at pack-time and cost real debugging time).

Copy it next to the unpacked doc and use it from a fill script:

```python
from brd_edit import BRD
doc = BRD("unpacked/word/document.xml")

doc.set_run_text("Summary of our understanding", "Real BR opening prose…")
doc.add_paragraphs_after("The problems this solution bridges:", [
    {"style": "ListParagraph", "num": 5, "runs": [("Bullet one.", False)]},
    {"style": "ListParagraph", "num": 5, "runs": [("Bullet two.", False)]},
])
doc.fill_table_rows("The following integrations", rows=[
    [[("Name A", False)], [("System X", False)], [("Desc.", False)]],   # one row
    # …one row per item — never collapse a set into one cell
])
doc.tracked_replace("old phrase", "new phrase")            # del+ins, author=Claude
doc.tracked_insert_paragraphs_after("anchor text", [
    {"runs": [("A whole new paragraph, marked as a tracked insertion.", False)]},
])
doc.save()   # calls lint() first; raises on any illegal run/paragraph placement
```

Operations:
- `set_run_text(needle, new_text)` — replace the text of the run containing
  `needle` (single match). For one-run prose placeholders.
- `replace_paragraph_runs(needle, runs)` — replace ALL runs in a paragraph,
  preserving its `<w:pPr>`. `runs` is a list of `(text, bold)`.
- `add_paragraphs_after(needle, paras)` — insert sibling paragraphs after the
  paragraph containing `needle`. Each para: `{runs, style?, num?}`.
- `fill_table_rows(anchor, rows)` — clone the table's first data row once per entry
  in `rows`, fill each cell. The anchor can be header-cell text OR the intro
  sentence before the table. **One row per item.**
- `fill_empty_cell(para_id, runs)` — fill a specific empty cell by its `w14:paraId`.
- `find_process_tables()` — return the use-case (Feature) tables, identified
  structurally (they have a Goal row and a Flow of Events row).
- `fill_process_table(tbl, fields)` — fill a use-case table's value cells by row
  label. `fields` maps labels (the title row `Feature #`/`Feature`, Goal, Business
  Event/Trigger, Primary Actor(s), Actor(s), Pre-conditions, Post-conditions, Flow of
  Events) to values. A value may be a string, a list of strings (one paragraph each),
  a list of `(text, bold)` runs (one paragraph), or a list of run-lists (one paragraph
  per step — this is how Flow of Events gets one bolded step per paragraph).
- `add_process_table(after=None, template=None)` — clone a use-case table with VALID
  fresh `w14` ids and insert it; returns the new table to `fill_process_table()`. Add
  a `[[Insert Feature Flow Diagram]]` paragraph after it yourself if needed.
- `clone_block_with_fresh_ids(el)` — deep-copy any block and regenerate every
  `w14:paraId`/`w14:textId` in the valid range (`< 0x80000000`). Use this for any
  hand cloning so pack-time validation doesn't reject out-of-range ids.
- `tracked_replace(old, new)` — tracked-change replace: `old` → `<w:del>`, `new` →
  `<w:ins>`, authored as Claude, surrounding text preserved.
- `tracked_insert_paragraphs_after(needle, paras)` — insert whole new paragraphs as
  tracked insertions (paragraph mark marked inserted too).
- `merge_runs()` — consolidates adjacent runs that share run properties and drops
  `proofErr` markers, making split-run placeholders contiguous. Called automatically
  (lazily) by the text-anchor methods when an anchor isn't found, so you rarely call
  it directly; it's idempotent and semantically invisible (no rendered-text change).
- `lint()` — asserts every `<w:r>` and `<w:p>` sits in a legal parent. `save()`
  calls it automatically; call it yourself mid-edit to fail fast.

**The benign validator quirk (environment-dependent):** on some validator versions,
after packing, the strict OOXML validator reports one error on
`word/intelligence2.xml` ("intelligence: No matching global declaration"). This is a
Microsoft extension namespace present in the **original template**, not caused by your
edits — it's harmless and Word opens the file fine. (On other validator versions it
doesn't appear at all.) Either way, only treat `word/document.xml` errors as real:
confirm document.xml is clean and ignore any intelligence2.xml line.

## Table-filling patterns (handled by the helper; gotchas if you hand-edit)

The `brd_edit.py` helper above handles all of these for you. This section documents
the underlying template quirks so you understand what the helper is doing — and so
you have the gotcha list if you ever must hand-edit XML directly (not recommended).

- **Duplicated title blocks (×2).** The cover title box is rendered twice —
  `mc:Choice` (modern) and `mc:Fallback` (legacy `v:textbox`). `[Extend/BoW App
  Name]`, `Prepared for [CLIENT]`, and `DD-Month-Year` each appear **twice**.
  Replace both, identically. A uniqueness-checked scripted replace (assert count
  == 2) is safer than two manual edits that can drift.

- **Three Feature stub tables, NOT identical** (handled for you by
  `fill_process_table`; this matters only if you hand-edit). The template ships three
  use-case tables. The row *labels* (Goal, Business Event/Trigger, etc.) and most cell
  boilerplate repeat ×3 — but the **Goal cell differs per table**: table 1 has the
  generic "Describe in one or two sentences…" boilerplate, while tables 2 and 3
  carry **pre-filled goals from a prior engagement** ("Payment Submission via
  API…", "Void and Stop-Payment Actions…"). So a single find-target for "Goal"
  finds only one of three. Fill Goal with three distinct find-targets (one per
  table); fill the genuinely-uniform rows positionally (replace the i-th
  occurrence with process i). Grep the actual occurrence counts before assuming
  uniformity — don't trust that all three stubs match.

- **Positional fill for repeated boilerplate.** For a string that legitimately
  appears once per table (e.g. the trigger boilerplate, ×3), collect all match
  offsets and replace from **last to first** so earlier offsets stay valid. Wrap
  replacement text in proper runs (`<w:r><w:rPr><w:sz w:val="20"/>…</w:rPr><w:t
  xml:space="preserve">…</w:t></w:r>`); for a Flow-of-Events cell with bolded step
  labels, split the content on `<b>…</b>` and emit a `<w:b/>` run for each bold
  segment.

- **Empty-cell tables (Integrations, Reporting, Security roles, Signoff).** These
  ship with empty rows whose cells are self-closing `<w:p …/>` or empty
  `<w:p …></w:p>` paragraphs. To fill: clone one data row as a template and inject
  runs into each cell's paragraph (expand `<w:p …/>` → `<w:p …>RUNS</w:p>`). When
  a cell template has multiple paragraphs (some pre-filled cells do), keep only the
  first and drop the rest so you don't inherit stale prior-engagement text.

- **Appendix BO / Security-Domain tables carry prior-engagement rows.** The
  Business Objects table ships with "Promotion Nomination Budget/Worker" and "Job
  Description Attachments"; Security Domains ships with "Promotion Nomination
  Security Domain." These are **example rows from a different app** — replace them
  wholesale with this app's objects/domains (or "No new business objects are
  introduced" when true). Some of these cells span multiple paragraphs; collapse
  to one when replacing.

- **`?` smart chars & arrows as entities.** Use `&#x2192;` for the
  "Engagement Letter &#x2192; Engagement Executive &#x2192; Region" arrows,
  `&#x2014;` for em-dashes, and `&#x2019;`/`&#x201C;`/`&#x201D;` for smart quotes —
  matches the example BRD's typography and survives JSON/XML round-tripping.

- **After any scripted pass, re-grep for leftovers** (`Promotion Nomination`,
  `Payment Submission`, `Use an active verb`, `[CLIENT]`, `DD-Month-Year`, etc.)
  and **render the cover to an image** to confirm the cover image, title card, and
  footer survived. Then pack with validation on.
