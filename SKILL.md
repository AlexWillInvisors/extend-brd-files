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
  this skill to REVIEW an existing Extend BRD for holes, gaps, open questions, or
  risks ("review this BRD," "what are we missing," "any risks or open items").
  Do NOT use for internal design docs, ROM/scoping estimates (that's the scoping
  playbook), or non-Extend Word documents.
license: Proprietary
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

If the user handed over app files, read them to ground the Appendix
(business objects, security domains) and the Integrations section in what's
actually built — don't describe a data model from memory when the
`.businessobject` files are right there.

### 2. Confirm the backbone and any added sections

The template has a **fixed section backbone** (do not reorder or rename):

1. **Business Requirements** — the problem, its scale, and what the solution bridges
2. **Processes** — one use-case table per process
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
prose and the Process tables — they are not new top-level sections.

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
title block (appears twice), the three process tables (whose Goal cells are NOT
uniform — tables 2 and 3 carry pre-filled goals from a prior engagement), and the
empty-cell or prior-engagement-seeded tables (Integrations, Reporting, Signoff,
Appendix BOs, Security Domains) — a small uniqueness-checked Python pass over
`document.xml` is the right tool, not a naive single-string Edit. In short:

- Title block: `[Extend/BoW App Name]` → app name; `Prepared for [CLIENT]` →
  client; `DD-Month-Year` → the date.
- Business Requirements: replace the one-line "Summary of our understanding…"
  placeholder with the real problem/scale/bridge prose.
- Processes: the template ships **three** stub use-case tables with boilerplate
  cell text ("Use an active verb phrase…", "Describe in one or two sentences…").
  Fill one table per real process; delete extra stubs or add more by cloning the
  table structure. Replace each `[[Insert Process Flow Diagram]]` with the real
  diagram, or leave it as an explicit placeholder if the diagram is pending.
- Remaining sections: replace the example/boilerplate prose and empty table rows
  with real content, or the section's stock text where it genuinely applies (the
  Language Translations and Mobile App Compatibility stock sentences are often
  correct as-is — confirm, don't assume).
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

### 5. Review for holes and risks (only when explicitly asked)

This step is **opt-in**. Run it only when the user asks for a review — phrases
like "review this BRD," "what are the holes/gaps," "any risks or open items,"
"poke holes in this." Do NOT run it on a normal authoring or fill request; a
plain "draft the BRD" should not append a risks section.

When asked, interrogate the whole BRD actively — don't just collect the `Open:` /
`TBD` flags already in the text. Read each section against the others and against
what a Workday Extend engagement actually needs, and surface:

- **Open Questions** — anything ambiguous, undecided, or assumed-without-
  confirmation: unspecified volumes or thresholds, undefined security roles,
  unconfirmed retention periods, integration error-handling not described,
  process flows missing a failure path, a stated behavior that contradicts another
  section, app-platform constraints the design may trip (BO/field/SI+MI caps, the
  25s synchronous-orchestration limit, WQL LIMIT/paging, deployment freeze
  windows) when the BRD's plan plausibly brushes them.
- **Risks** — things that could derail delivery or go wrong in production:
  performance/scale exposure, dependencies on client-side work or external
  systems, sequencing/timeline risk, scope ambiguity that could expand, data-
  migration or transition-year gaps.

Deliver the findings in **two places**:

1. **A chat summary** — internal-facing, blunt. Group as Open Questions and Risks.
   For each item: what's unclear/risky, why it matters, and (for open questions)
   the specific question to put to the client or team. This is for the consultant,
   so it can name platform constraints and delivery risk directly.
2. **An "Open Questions & Risks" Appendix subsection in the BRD** — client-facing,
   measured. Same substance, but framed as constructive open items and
   considerations to resolve before signoff, not as internal hedging. Style its
   header `Heading2` to match the other Appendix subsections. Two tables (Open
   Questions; Risks) or two bulleted lists. If the review is part of a revision
   round on an existing doc, insert this section as **tracked changes** like any
   other edit.

Keep the two registers distinct: the chat version can say "this will blow the 25s
synchronous orchestration cap"; the in-doc version says "Confirm the rollover
batch processing approach given expected data volumes." Never invent a risk to
pad the list — an honest short list beats a padded one. See
`references/section-guide.md` ("Open Questions & Risks") for format detail.

### 6. Validate and deliver

Pack with validation on, then present the `.docx`. If validation fails, unpack,
fix the XML, repack — don't paper over it.

## Craft rules (what separates a real BRD from filled boilerplate)

These are distilled from the worked example. Apply them throughout:

- **Business Requirements leads with the problem and its scale, then the
  solution.** The example opens with "the client manages ELs one at a time … not
  feasible at 70,000–90,000 letters" *before* describing the feature. State the
  pain and the number first.
- **Close Business Requirements with a "problems this solution bridges" bullet
  list** — each bullet a concrete gap the solution closes.
- **Process tables use the fixed row set** (Process # / Goal / Business
  Event/Trigger / Primary Actor(s) / Actor(s) / Pre-conditions / Post-conditions /
  Flow of Events). In **Flow of Events**, write numbered, bolded steps
  (**1. Filter.** … **2. Review.** …), describing what the actor does and how the
  system responds — not a vague paragraph.
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
