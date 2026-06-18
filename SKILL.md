---
name: extend-brd
description: >-
  Author or revise a Business Requirements Document (BRD) for a Workday Extend
  (or Built on Workday) engagement, using the standard Invisors BRD template.
  Use this skill WHENEVER the user wants to produce, draft, fill in, update, or
  revise a BRD, requirements doc, or "the BRD" for an Extend / BoW app — including
  when they hand over a scoping document, meeting notes, or existing app files to
  turn into requirements, or ask to document an app's processes, integrations,
  business objects, or security model in the client-facing BRD format. Trigger
  even if the user says "requirements document," "the Forvis doc," "the CER BRD,"
  or names a specific client/app rather than saying "BRD" explicitly. Also use
  this skill to REVIEW an existing Extend BRD or its design for holes, gaps, open
  questions, risks, or RAID items, and to check whether the design would breach
  Workday Extend platform limits ("review this BRD," "what are we missing," "any
  risks or open items," "build the RAID log," "does this design breach any Extend
  limits").
  Do NOT use for internal design docs, ROM/scoping estimates (that's the scoping
  playbook), or non-Extend Word documents.
license: Proprietary
version: 1.1.0
---

# Extend BRD authoring

Produce a client-facing Business Requirements Document for a Workday Extend / BoW
engagement, filled into the standard Invisors template (`Extend Deploy - BRD`).
The deliverable is a `.docx` that preserves the template's cover image, Lato
styling, table of contents, and Invisors footer exactly — only the content
changes.

## The cardinal rule: edit the template, never rebuild it

The template carries a topographic cover image, a teal title card, Lato fonts, a
generated table of contents, and the "Elevating Perspective + Transforming
Results / Invisors Proprietary and Confidential" footer. **None of that can be
faithfully regenerated from scratch** with docx-js, and attempts to do so always
drift. So the workflow is always: **copy `assets/brd-template.docx`, then
find-and-replace the placeholder content with filled content** using the `docx`
skill's unpack → edit XML → pack flow. Read `/mnt/skills/public/docx/SKILL.md`
for those mechanics before touching the file — this skill does not duplicate them.

Never start a BRD with docx-js. Never hand-build the cover or TOC. Start from the
asset.

### Dependencies & runtime

- **`brd_edit.py` requires `lxml`** (`pip install lxml`). It is the required tool for
  all content insertion and tracked-change edits (see `references/template-anatomy.md`).
- **Unpack / pack / validate** the `.docx` with the `docx` skill's scripts when they're
  available (`/mnt/skills/public/docx/` in Anthropic's skill runtime). Read
  `/mnt/skills/public/docx/SKILL.md` for those mechanics — this skill doesn't duplicate
  them. If that skill isn't present, a plain unzip → edit → re-zip works too; a `.docx`
  is just a zip.
- **Self-sufficient editing core.** `brd_edit.py` now merges split runs itself
  (`merge_runs()`, called lazily), so its text anchors resolve **with or without** the
  docx skill's `unpack.py` run-merging step. You still need *some* way to unpack/repack
  the file — but the editing logic no longer depends on `unpack.py` having run.
- **`scripts/scrape_extend_limits.py`** (the limits crawler) is a separate, human-run
  maintenance tool needing `playwright`; it is never invoked during a BRD session.

## Workflow

### 1. Assess inputs before writing anything

A BRD request arrives with one of (or a mix of): a filled scoping questionnaire or
notes, a live conversation to work it out together, or existing app files
(`model/`, `presentation/`, `orchestration/`) to reverse-document. Your first job
is to judge **whether you have enough to write each section** — not to start
typing.

Walk the fixed backbone (below) and, for each section, mark what the inputs cover
and what they don't. Then **ask targeted gap questions for the genuinely missing
pieces only** — don't re-ask what the inputs already answer, and don't stall on a
complete scoping doc. The user is close to the technical and business detail and
will catch a confabulated requirement instantly, so the failure mode to avoid is
inventing content to fill a section. When you don't have it, that's an `Open:` /
`TBD` flag in the doc (see craft rules), not a guess.

**On a pure reverse-doc run, the gaps are predictable — batch them up front.** App
files carry the *how* (Features, Integrations, model, security domains) but never the
*why* or the *scale*. So a reverse-doc run almost always gaps on exactly three
things: **Business Requirements framing (the problem + volume/scale), Data Retention,
and the language set** — and almost never on Features/Integrations/Appendix. Ask
those few leadership-level questions in one batch at the start, rather than
discovering them section by section.

**Reading `.orchestration` files fast.** They're dense single-line JSON ASTs. Don't
read the whole tree — grep for `SendWorkdayApiRequest` (the `path`/`method` nodes
give you the integration calls, e.g. a SOAP `Submit_Project_Request`) and
`CreateTextTemplate` (request bodies, where threshold/branch logic like a `$50k`
hierarchy split lives). That recovers the integration intent in a fraction of the
time.

If the user handed over app files, read them to ground the Appendix
(business objects, security domains) and the Integrations section in what's
actually built — don't describe a data model from memory when the
`.businessobject` files are right there.

### 2. Confirm the backbone and any added sections

The template has a **fixed section backbone** (do not reorder or rename):

1. **Business Requirements** — the problem, its scale, and what the solution bridges
2. **Features** — one use-case table per feature (the template heading is "Features")
3. **Integrations** — table of cross-system data flows
4. **Reporting Requirements** — table
5. **Data Retention Requirements** — prose
6. **Security Requirements** — table (or `TBD`)
7. **Language Translations** — prose
8. **Mobile App Compatibility** — prose
9. **Signoff/Approval page** — version table
10. **Appendix** — UI Mockups, Model Components, Business Objects, Security Domains

**Project-specific sections are added UNDER the Appendix**, not by altering the
backbone. The worked example adds Appendix subsections like "Eligibility rules,"
"Rollover field rules," and "grid data model." Phase-1/Phase-2 splits, multi-path
flows, and similar feature structure live **inside** the Business Requirements
prose and the Feature tables — they are not new top-level sections.

The **Open Questions & Risks** section produced by a review (step 5) is likewise
an Appendix subsection, never a new top-level section — it must not disturb the
backbone numbering or TOC.

See `references/section-guide.md` for what each section must contain and the
craft that makes each one read like the example rather than like filled-in
boilerplate.

### 3. Fill the template (new BRD)

Copy `assets/brd-template.docx`, unpack it, and replace each placeholder. The
exact placeholder tokens, the style IDs, and the find-and-replace mechanics are in
`references/template-anatomy.md` — read it before editing, especially the
"Table-filling patterns" section. Use the Edit tool directly for the **unique
prose placeholders** (title, Business Requirements, Data Retention, Security
intro, Language, Mobile). For the **repeated/duplicated structures** — the
title block (appears twice), the three feature tables (whose Goal cells are NOT
uniform — tables 2 and 3 carry pre-filled goals from a prior engagement), and the
empty-cell or prior-engagement-seeded tables (Integrations, Reporting, Signoff,
Appendix BOs, Security Domains) — a small uniqueness-checked Python pass over
`document.xml` is the right tool, not a naive single-string Edit. In short:

- Title block: `[Extend/BoW App Name]` → app name; `Prepared for [CLIENT]` →
  client; `DD-Month-Year` → the date.
- Business Requirements: replace the one-line "Summary of our understanding…"
  placeholder with the real problem/scale/bridge prose.
- Features: the template ships **three** stub use-case tables (vertical label/value,
  not header+data-row). Fill one table per real feature with
  `brd_edit.fill_process_table` (matches rows by label; pass Flow of Events as a list
  of run-lists, one paragraph per step). Delete extra stubs, or add more with
  `add_process_table` (clones a table with valid fresh ids — don't hand-clone and
  hand-number `w14:paraId`s). Replace each `[[Insert Feature Flow Diagram]]` with the
  real diagram, or leave it as an explicit placeholder if the diagram is pending.
- Remaining sections: replace the example/boilerplate prose and empty table rows
  with real content, or the section's stock text where it genuinely applies. Mobile
  App Compatibility's stock "not needed" sentence is often correct as-is — confirm,
  don't assume. **Language Translations defaults to US English only**: replace the
  template's three-language stock sentence with an English-only statement unless a
  specific language set is explicitly confirmed for the engagement.
- After packing, the TOC page numbers won't auto-update (Word recalculates on
  open). That's expected; don't try to hand-fix them.

Model the **voice, depth, and structure** on `references/filled-example.md` — it's
the gold standard for what a finished BRD reads like.

### 4. Revise an existing BRD (revision round) — use tracked changes

When the user hands you an existing BRD to edit (not a fresh fill), make the
edits as **Word tracked changes** authored as "Claude," so the user can review
and accept/reject. The `docx` skill's XML reference has the `<w:ins>` / `<w:del>`
patterns. Make minimal, surgical edits — mark only what changes, preserve the
surrounding `<w:rPr>` formatting. Edit **in place** in the same document across
rounds; don't spin up a parallel "v2" unless asked. Content-accuracy corrections
take priority over stylistic ones.

**Tracked changes vs. plain edits — get this right or pack fails.** Tracked changes
are ONLY for revising a BRD the **user supplied as an existing file** (where the
baseline genuinely is that file). On a **fresh authoring run** — including a
single-pass *draft + review* (see step 5) — write everything as **plain content**,
not tracked changes. Why: `pack.py` validates by stripping Claude's tracked changes
and checking the result matches the **original template**; if the rest of the doc has
plain fills, the stripped text won't match and pack fails with "Document text doesn't
match after removing Claude's tracked changes." Never mix plain fills with tracked-
change insertions in the same fresh document.

### 5. Review for holes and risks (only when explicitly asked)

This step is **opt-in**. Run it only when the user asks for a review — phrases
like "review this BRD," "what are the holes/gaps," "any risks or open items,"
"poke holes in this." Do NOT run it on a normal authoring or fill request; a
plain "draft the BRD" should not append a risks section.

When asked, interrogate the whole BRD actively — don't just collect the `Open:` /
`TBD` flags already in the text. Read each section against the others, against what a
Workday Extend engagement actually needs, and **against the documented platform
limits** in `references/extend-limits.md` (run the full limits audit here — see
"Checking the design against Extend limits"). The internal model is a full **RAID
log plus Open Questions** — five buckets:

- **Open Questions** — anything ambiguous, undecided, or assumed-without-
  confirmation: unspecified volumes or thresholds, undefined security roles,
  unconfirmed retention periods, integration error-handling not described,
  process flows missing a failure path, a stated behavior that contradicts another
  section.
- **Risks** — things that could derail delivery or go wrong in production:
  performance/scale exposure (especially where the design plausibly brushes a limit
  in `extend-limits.md`), dependencies on client-side work or external systems,
  sequencing/timeline risk, scope ambiguity that could expand, data-migration or
  transition-year gaps.
- **Actions** — concrete follow-ups needed to resolve the open items: who needs to
  decide, confirm, build, or provide data, and (where known) by when.
- **Issues** — problems *already* present in the BRD or the plan: contradictions
  between sections, a design that already exceeds a confirmed limit, a missing
  section, a requirement that can't be met as written. (Risks are future; issues are
  current.)
- **Decisions** — decisions already made that the BRD depends on (with their
  rationale), and decisions still owed before signoff.

The client-facing in-doc section keeps the gentler name **"Open Questions &
Risks"** (it stores all five buckets, but the label avoids alarming the client).
See `references/section-guide.md` for the in-doc table layout per bucket.

Deliver the findings in **two places**:

1. **A chat summary** — internal-facing, blunt. Group by the five buckets (Open
   Questions, Risks, Actions, Issues, Decisions); omit any bucket that's empty
   rather than padding it. For each item: what it is, why it matters, and (for open
   questions/actions) who should answer or own it. This is for the consultant, so it
   can name platform constraints and delivery risk directly — e.g. "this iterates a
   variable-sized dataset synchronously and will hit the documented sync-orchestration
   cap (see `extend-limits.md`)."
2. **An "Open Questions & Risks" Appendix subsection in the BRD** — client-facing,
   measured. Same substance, but framed as constructive open items, considerations,
   actions, and recorded decisions to resolve before signoff — not as internal
   hedging. Style its header `Heading2` to match the other Appendix subsections.
   Default to a **single consolidated grid** (Type · Item/Description · Owner ·
   Target/Date); per-bucket tables are an acceptable alternative for a long RAID. Use
   **bold runs**, not `Heading3`, for the labels (see `references/section-guide.md` and
   `references/raid-example.md`). **Tracked vs. plain (critical — see step 4):** if
   this review is a **single-pass draft + review** of a fresh BRD, insert the section
   as **plain content**. Use **tracked changes** ONLY when reviewing a BRD the user
   supplied as an existing file. Mixing plain fills with tracked insertions in one
   fresh document makes `pack.py` fail validation.

Keep the two registers distinct: the chat version can say "this will blow the
documented synchronous-orchestration cap"; the in-doc version says "Confirm the
rollover batch processing approach given expected data volumes." Never invent a risk
to pad the list — an honest short list beats a padded one. Cite a specific limit only
when it's in the **verified** zone of `extend-limits.md`; if it's only a commonly-
cited (unverified) constraint, frame it as a question to confirm, not a stated fact.
See `references/section-guide.md` ("Open Questions & Risks") for format detail.

### 6. Validate and deliver

Pack with validation on, then present the `.docx`. If validation fails, unpack,
fix the XML, repack — don't paper over it.

## Checking the design against Extend limits

A Workday Extend app can be designed in a way that quietly breaches a platform limit
(business-object/field counts, the synchronous-orchestration runtime window, WQL/REST
paging and row caps, payload sizes, deployment windows, referential integrity at
delete). Catching that in the BRD — before build — is one of this skill's jobs.

The source of truth is `references/extend-limits.md`. It has a **verified** zone
(human-confirmed limits, safe to assert), a **commonly-cited (unverified)** zone
(prompts to check, never assert without confirming), and an **auto-extracted** zone
regenerated by the crawler. Read it before flagging anything, and respect which zone
a limit comes from.

Two modes, by the timing decision for this skill:

- **Proactive (every authoring/revision run) — light flags.** As you draft the
  Features, Integrations, Data Retention, and Appendix data-model content, watch for
  designs that plausibly brush a limit in `extend-limits.md`: a process that iterates
  a variable, client-stated volume synchronously; a read that could exceed a paging
  cap; a data model approaching BO/field counts. When you spot one, add a brief
  inline `Open:` flag in the relevant section (client-facing wording) **and** mention
  it once in chat (blunt wording). Do **not** append a full risks section on a plain
  authoring run — that's review-only. Keep it to genuine, design-specific hits; don't
  run a generic checklist against every BRD.
- **Full audit (on review, step 5).** Walk every documented limit in
  `extend-limits.md` against the design systematically and route findings into the
  RAID buckets (usually Risks and Open Questions). This is the exhaustive pass.

In both modes: assert a specific number only if it's in the **verified** zone. For an
unverified constraint, phrase it as a confirmation ("Confirm expected row volumes per
rollover run against Extend's paging limits"), never as a stated cap. If a limit
matters to a BRD and isn't verified yet, that's a cue to run the crawler / verify it
and promote it.

**Refreshing the limits reference.** `references/extend-limits.md` is maintained by
`scripts/scrape_extend_limits.py`, an offline Playwright crawler over
`developer.workday.com/documentation` (seed + discover). It's a human-run maintenance
step, not part of a BRD session — see the script header for setup and usage. The
crawler only rewrites the auto-extracted zone; the verified and commonly-cited zones
are preserved.

## Craft rules (what separates a real BRD from filled boilerplate)

These are distilled from the worked example. Apply them throughout:

- **Business Requirements leads with the problem and its scale, then the
  solution.** The example opens with "the client manages ELs one at a time … not
  feasible at 70,000–90,000 letters" *before* describing the feature. State the
  pain and the number first.
- **Close Business Requirements with a "problems this solution bridges" bullet
  list** — each bullet a concrete gap the solution closes.
- **Feature tables use the fixed row set** (Feature # / Goal / Business
  Event/Trigger / Primary Actor(s) / Actor(s) / Pre-conditions / Post-conditions /
  Flow of Events). In **Flow of Events**, write numbered, bolded steps **one per
  paragraph** (default): **1. Filter.** <…> as one paragraph, **2. Review.** <…> as
  the next, each describing what the actor does and how the system responds — not a
  vague paragraph, and not a single run-on (the run-on form is an acceptable
  alternative only for very short flows).
- **Flag unknowns explicitly as `Open:` or `TBD`, inline, in bold.** The example
  writes "**Open:** Confirm whether any rollover-run audit trail…" and "Security
  Requirements: TBD." Never silently omit a section you lack info for, and never
  invent content to fill it. An honest `TBD` is correct; a confabulated
  requirement is a defect.
- **Remove unverified claims rather than leave them unsourced.** If a number,
  retention period, or behavior isn't confirmed, either flag it `Open:` or cut it
  — don't assert it.
- **Integrations and Appendix describe what's actually built or planned**, grounded
  in app files when available. "No new business objects are introduced" is a valid,
  strong Appendix entry when true — don't pad.
- **The BRD always reads as a forward statement of requirements, regardless of
  input mode.** Whether the input was a scoping doc, a conversation, or existing
  app files to reverse-document, the *output* must never narrate how it was made.
  Do not write "reverse-documented from the deployed model," "the sources
  reviewed," "read from the app files," "this inventory is from the deployed
  model," or similar. Ground the content in the files, but state each requirement
  as a requirement. The one exception is the honest `Open:`/`TBD` flag for a
  genuinely undecided *requirement* (retention period, language set) — that's a
  real gap a normal BRD flags, not authoring meta-commentary. When reverse-
  documenting, phrase residual uncertainty as a client-facing confirmation
  ("Confirm the submit-time orchestration sequence"), never as a reference to
  source files ("...from the orchestration sources").

## Reference files

- `references/template-anatomy.md` — exact placeholder tokens, style IDs,
  find-and-replace and tracked-changes mechanics for THIS template. Read before
  editing.
- `references/section-guide.md` — per-section content guide + craft, section by
  section.
- `references/filled-example.md` — the CER Mass EL Rollover BRD, the gold-standard
  worked example. Read it to calibrate voice and depth.
- `references/raid-example.md` — worked example of the review output (Open Questions
  & Risks / full RAID), both the internal chat register and the in-doc tables, grounded
  in the same engagement. Read it before producing a review.
- `references/extend-limits.md` — the source of truth for Workday Extend platform
  limits (verified / commonly-cited / auto-extracted zones). Consult before flagging
  any limit. Maintained by the crawler below.
- `scripts/scrape_extend_limits.py` — offline Playwright crawler that refreshes the
  auto-extracted zone of `extend-limits.md` from `developer.workday.com`. Human-run
  maintenance tool; not invoked during a BRD session. See its header for setup.
