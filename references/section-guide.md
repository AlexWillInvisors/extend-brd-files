# Section guide

What each backbone section must contain, and the craft that makes it read like the
worked example (`filled-example.md`) rather than filled-in boilerplate. Sections
are in template order; do not reorder or rename them.

## 1. Business Requirements

The most important section — it frames everything. Structure:

1. **Problem + scale, first.** One or two sentences naming the current pain and
   its magnitude. Example: managing ELs one at a time is "not operationally
   feasible at the required scale of 70,000–90,000 letters." Lead with the number.
2. **What the document defines + the solution shape.** Name the feature, say it's
   built as an extension of (or net-new) Extend app, and describe the solution's
   major paths/phases in prose. Phase-1/Phase-2 splits and multi-path flows are
   described HERE, not as separate sections.
3. **"The problems this solution bridges:"** followed by a bullet list — each
   bullet a concrete gap the solution closes (volume infeasibility, transition-year
   data gaps, performance constraints, etc.).

Keep it client-readable: plain language, bottom-line-first. This is leadership-
facing prose.

## 2. Features

One use-case table per feature. This section is titled **Features** in the template
(renamed from the older "Processes"); the table's first row label is **Feature #**.
Fill each table with `brd_edit.fill_process_table` (it matches rows by label). The
fixed row set (don't add/remove rows):

| Row | Content |
|---|---|
| Feature # / title | `<N> — <active verb phrase>` (e.g. "1 — Bulk EL Rollover: select and roll over engagement letters (Phase 1)") |
| Goal | 1–2 sentences: scope and outcome. NOT the step-by-step flow. |
| Business Event/Trigger | What prompts the feature to run |
| Primary Actor(s) | Who initiates |
| Actor(s) | Secondary actors (incl. system actors like "Validation orchestration (system actor)") |
| Pre-conditions | What must be true to start |
| Post-conditions | What's true on success; alternative successful terminations |
| Flow of Events | **Numbered, bolded steps — one per paragraph (default).** A paragraph each: **1. Filter.** <what the actor does / how the system responds>, then a new paragraph **2. Review the grid.** …, etc. Pass this to `fill_process_table` as a list of run-lists (one per step), each typically a bold step label + a plain body run. A single run-on paragraph (**1. … 2. … 3. …**) is an acceptable alternative for very short flows. Reference the Appendix for detailed rule sets rather than inlining them. |

A multi-phase feature gets one table per phase/path (the example has three:
Phase 1 bulk, Phase 2 validate/resolve, single-EL); use `add_process_table` to add
tables beyond the three stubs. Replace each `[[Insert Feature Flow Diagram]]` with
the real diagram or leave as an explicit pending placeholder.

## 3. Integrations

Lead sentence + a three-column table: **Integration Name | External System /
Mechanism | Description.** Include Workday-internal orchestrations and EIBs, not
just external systems — the example lists "EL/project grid data assembly
(Workday WQL/orchestration)," "Rollover submission (O4I)," EIB mass-uploads, etc.
Add a **Note:** line for scope boundaries ("No changes are required to the
Integration Hub process"). Ground this in the app's actual orchestration files
when available.

## 4. Reporting Requirements

Two-column table: **Report Name | Description.** If reporting is thin, one row is
fine (the example has one: O4I run status). Flag undesigned presentation as such
("The user-facing presentation of these results is to be designed").

## 5. Data Retention Requirements

Prose. State whether the feature introduces new long-term storage, what statuses
records are created in, and any retention policy considerations. Flag unconfirmed
retention questions as **Open:**. **Replace the template's payment-data example
entirely** — it's from a different engagement.

## 6. Security Requirements

Role table (**Security Role | # of Users | Description**) when known, or `TBD.`
when not. The example honestly states `TBD` and notes roles will be defined as
security is finalized — do that rather than invent roles.

## 7. Language Translations

**Default to US English only** when the language set isn't explicitly defined. The
template ships a stock three-language sentence (US English / US Spanish /
French-Canadian) — do **not** keep it by default; replace it with an English-only
statement (e.g. "The Extend app will be available in US English."). Only list
additional languages when the engagement explicitly confirms them — in that case
name exactly those languages and note the app respects the user's Workday language
preference. Never carry the stock multi-language list forward unconfirmed.

## 8. Mobile App Compatibility

Usually the stock "Extend app functionality is not needed on the Workday Mobile
App." Confirm it's true for this app before keeping.

## 9. Signoff/Approval page

Version table (**Version # | Approver | Date**). Seed with the current version
row (e.g. "1.0"); leave approver/date blank for the client.

## 10. Appendix

**These four subsections ALREADY ship in the template as `Heading2` headings** — UI
Mockups, Model Components, Business Objects, Security Domains. **Edit the existing
headings; do not add new ones.** (Adding a second "Model Components" heading is an
easy mistake — it's already there between UI Mockups and Business Objects.) Only
**project-specific** subsections are *inserted* (as new `Heading2`), after these four.

- **UI Mockups**: `[Insert images]` — insert mockups or leave as explicit pending
  placeholder.
- **Model Components**: the stock definition paragraph is fine; add a sentence on
  whether new components are introduced.
- **Business Objects**: table (**Name | Description**) of this app's BOs, grounded
  in `.businessobject` files when available. "No new business objects are
  introduced" is a strong, valid entry when true — don't pad.
- **Security Domains**: table (**Name | Description**), or note security is TBD.
- **Project-specific subsections** (added under the Appendix): detailed rules
  that would clutter the Process tables — eligibility rules, field-mapping rules,
  data-model/grid shapes. The example adds "Eligibility rules," "Rollover field
  rules," "Flat interleaved grid data model," and "Pagination and selection." Use
  tables where the content is a rule set.

## Open Questions & Risks (review output — opt-in only)

Produced only when the user asks for a review (SKILL.md step 5), never on a plain
authoring run. Lives as an Appendix subsection (`Heading2`), not a top-level
section. The **client-facing name stays "Open Questions & Risks"** — deliberately
gentler than "RAID log" so it reads as constructive open items, not internal
hedging — but it stores a full **RAID model plus Open Questions**: five buckets.

The five buckets:

- **Open Questions** — ambiguous, undecided, or assumed-without-confirmation items.
  Each: the question and why it matters (and, in chat, who should answer it).
- **Risks** — things that *could* derail delivery or production (future/potential).
  Each: the risk, its impact, and any mitigation.
- **Actions** — concrete follow-ups to resolve the open items. Each: the action, its
  owner, and status/target.
- **Issues** — problems *already* present (current, not potential): a contradiction
  between sections, a design that already exceeds a confirmed limit, a missing piece.
- **Decisions** — decisions already made that the BRD relies on (with rationale and
  date), plus decisions still owed before signoff.

(Risks are potential; issues are realized. Keep them in separate buckets.)

Two registers, same substance:

- **In-doc (client-facing, measured) — single consolidated grid (default):** one
  table with columns **Type · Item / Description · Owner · Target / Date**, one row per
  item, the Type cell naming the bucket (Open Question / Risk / Action / Issue /
  Decision) and rationale/impact folded into the Description. This reads better than
  several tiny tables when buckets have only a few rows each.
  - *Alternative (long RAID):* one small table per **non-empty** bucket — Open
    Questions (**Item | Why it matters**), Risks (**Risk | Impact | Mitigation**),
    Actions (**Action | Owner | Target/status**), Issues (**Item | Resolution
    needed**), Decisions (**Decision | Rationale | Date**). Omit empty buckets.
  - **Label with a bold run, not `Heading3`** — whether it's the grid's column
    headers or per-bucket table headers, this template's `Heading3` is only faintly
    differentiated from body text, so use a bold run for the labels.
  - Framed as items to resolve before signoff. E.g. "Confirm the rollover batch
    processing approach given expected data volumes" — not "this will blow the
    synchronous-orchestration cap."
- **Chat (internal-facing, blunt):** same items grouped by the five buckets, naming
  platform constraints and delivery risk directly. The chat version is where "this
  iterates a variable-sized dataset synchronously and will hit the documented
  sync-orchestration cap (see `extend-limits.md`)" belongs.

Don't pad. A short honest list beats a long speculative one. Draw on real Extend
platform constraints **from `references/extend-limits.md`** when the BRD's plan
plausibly brushes them — but only flag a constraint the design actually risks, not a
generic checklist. Assert a specific limit value only if it's in that file's
**verified** zone; otherwise frame it as a question to confirm.

Note: this format is not in `filled-example.md` (that BRD predates the review
feature). Instead, see **`references/raid-example.md`** for a worked example of both
registers — the blunt internal chat summary and the measured in-doc tables — grounded
in the same CER Mass EL Rollover engagement and the verified limits in
`extend-limits.md`. It's illustrative, not a real deliverable's review; defer to any
RAID/open-items format the team standardizes on if one exists.

## Cross-cutting craft

- Flag every unknown as bold **Open:** or **TBD** inline — never silently omit,
  never confabulate.
- Cut unverified claims (numbers, retention periods, behaviors) or flag them
  `Open:` — don't assert them.
- Reference the Appendix from the Features section instead of inlining detailed
  rule sets in the Flow of Events.
- **One row per item in every table.** Each business object, security domain,
  integration, report, and role gets its own row — never collapse a set into a
  single cell (e.g. "Full / Simple / Reports / Setup" in one row is wrong; that's
  four rows). The Name/first column holds one item; the Description column
  describes that one item. This holds even when the items share a one-line summary
  you'd otherwise be tempted to write once.
- Plain, client-readable language throughout; the BRD is leadership-facing.
