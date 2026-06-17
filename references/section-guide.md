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

## 2. Processes

One use-case table per process. The fixed row set (don't add/remove rows):

| Row | Content |
|---|---|
| Process # / title | `<N> — <active verb phrase>` (e.g. "1 — Bulk EL Rollover: select and roll over engagement letters (Phase 1)") |
| Goal | 1–2 sentences: scope and outcome. NOT the step-by-step flow. |
| Business Event/Trigger | What prompts the process to run |
| Primary Actor(s) | Who initiates |
| Actor(s) | Secondary actors (incl. system actors like "Validation orchestration (system actor)") |
| Pre-conditions | What must be true to start |
| Post-conditions | What's true on success; alternative successful terminations |
| Flow of Events | **Numbered, bolded steps**: **1. Filter.** … **2. Review the grid.** … Each step says what the actor does and how the system responds. Reference the Appendix for detailed rules ("See Appendix for the eligibility rules") rather than inlining everything. |

A multi-phase feature gets one table per phase/path (the example has three:
Phase 1 bulk, Phase 2 validate/resolve, single-EL). Replace each
`[[Insert Process Flow Diagram]]` with the real diagram or leave as an explicit
pending placeholder.

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

Stock sentence about US English / US Spanish / French-Canadian and using the
user's Workday language preference. **Confirm the actual language set** — only
keep the stock languages if they're correct for this engagement.

## 8. Mobile App Compatibility

Usually the stock "Extend app functionality is not needed on the Workday Mobile
App." Confirm it's true for this app before keeping.

## 9. Signoff/Approval page

Version table (**Version # | Approver | Date**). Seed with the current version
row (e.g. "1.0"); leave approver/date blank for the client.

## 10. Appendix

Fixed subsections (`Heading2`): **UI Mockups, Model Components, Business Objects,
Security Domains.** Plus any project-specific subsections added here.

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
section. Lighter than full RAID — two categories only:

- **Open Questions** — ambiguous, undecided, or assumed-without-confirmation
  items. Each: the question, why it matters, and (in the chat version) who should
  answer it.
- **Risks** — things that could derail delivery or production. Each: the risk and
  its impact.

Two registers, same substance:

- **In-doc (client-facing, measured):** two tables. Open Questions
  (**Item | Why it matters**) and Risks (**Risk | Impact / consideration**).
  Framed as items to resolve before signoff, not internal hedging. E.g. "Confirm
  the rollover batch processing approach given expected data volumes" — not
  "this will blow the 25s synchronous orchestration cap."
- **Chat (internal-facing, blunt):** same items, but name platform constraints
  and delivery risk directly. The chat version is where "this iterates a
  variable-sized dataset synchronously and will hit the 25s cap" belongs.

Don't pad. A short honest list beats a long speculative one. Draw on real Extend
platform constraints when the BRD's plan plausibly brushes them (BO/field/SI+MI
caps, 25s synchronous-orchestration limit, WQL LIMIT/paging and the 100-row REST
cap, deployment freeze windows, referential-integrity-at-delete), but only flag a
constraint the design actually risks — not a generic checklist.

Note: this format has no gold-standard example in `filled-example.md` (that BRD
predates the review feature), so it's the one part of the skill not modeled on a
real Invisors deliverable. Defer to any RAID/open-items format the team
standardizes on if one exists.

## Cross-cutting craft

- Flag every unknown as bold **Open:** or **TBD** inline — never silently omit,
  never confabulate.
- Cut unverified claims (numbers, retention periods, behaviors) or flag them
  `Open:` — don't assert them.
- Reference the Appendix from the Processes section instead of inlining detailed
  rule sets in the Flow of Events.
- **One row per item in every table.** Each business object, security domain,
  integration, report, and role gets its own row — never collapse a set into a
  single cell (e.g. "Full / Simple / Reports / Setup" in one row is wrong; that's
  four rows). The Name/first column holds one item; the Description column
  describes that one item. This holds even when the items share a one-line summary
  you'd otherwise be tempted to write once.
- Plain, client-readable language throughout; the BRD is leadership-facing.
