# Worked example — CER Mass EL Rollover BRD

This is a real, finished BRD (Forvis Mazars, CER Mass Engagement Letter Rollover)
extracted to markdown. It is the **gold standard** for voice, depth, and structure.
Read it to calibrate how a filled BRD reads — especially the problem-first Business
Requirements opening, the 'problems this bridges' bullets, the numbered bolded Flow
of Events steps, the Appendix rule tables, and the explicit Open:/TBD flags.

> **Naming note:** this example predates the **Processes → Features** rename. Where it
> says "Processes" / "Process #" / "Process Flow," the current template and skill use
> **Features** / **Feature #** / **Feature Flow**. The example also renders Flow of
> Events as a single run-on cell; the current default is **one paragraph per step**
> (the run-on form remains acceptable for very short flows). Calibrate on its voice and
> depth — not these two presentational details.

The rendered .docx (not this markdown) is what the client receives; this text shows
the *content shape*, not the styling (cover, Lato, TOC, footer come from the template).

---

##### CER — Mass Engagement Letter Rollover

Prepared for Forvis Mazars

June 2025

Contents

	Business Requirements	3

	Story/Process Flow	4

	Implementation & User Guides	6

	Reporting & Data Retention	6

	Flexible UI Integration	6

	Security Roles	6

	Language Translations	6

	Mobile App Compatibility	6

	Process Flows	7

	See attached	7

	Signoff/Approval page	8

	Version 1.0………………………………………………………………xx/xx/xxxx	8

	Appendix	9

	UI Mockups	9

	Data Transmission	9

	Model Components	10

	Business Objects	10

	Security Domains	10

# Business Requirements

The client manages Engagement Letter (EL) creation individually through the CER application. As the practice prepares for a mass Tax engagement rollover, processing ELs one at a time is not operationally feasible at the required scale of 70,000–90,000 letters.

This document defines the requirements for a Mass EL Rollover feature built as an extension of the existing CER Workday Extend application. The feature provides two rollover paths for CER users : a Bulk EL Rollover that selects many prior-year ELs at once via a single grid that displays EL rows and their associated project rows inline, and a Single EL Rollover that lets the user select one EL at a time from a grid of ELs eligible for rollover. In the Bulk path, a loop orchestration iterates the selected ELs and invokes an individual-EL-rollover orchestration for each; rolled ELs are created in Approved status and sent to CPQ and Amelio. In the Single path, the selected EL and its projects are rolled over, the rolled EL is created in Save for Later status, and the user is taken directly to the Edit EL page to complete and approve it; on approval it is sent to CPQ and Amelio. The Single EL Rollover grid is exposed on the Convert Proposal page as the most analogous location, but the EL being rolled does not need to originate from a proposal.

The Bulk EL Rollover path is delivered in two phases. **Phase 1** is required for the November Tax rollover go-live: filtered selection, the flat interleaved grid, configurable pagination and selection thresholds, terminated-executive detection with affected ELs rendered non-selectable, batch submit, and the transition-year mass upload. **Phase 2** is a post-go-live enhancement that makes affected ELs selectable and moves resolution after submission: a validation orchestration scans every role on each EL and its projects for terminated workers, diverts any EL with a terminated role to a Rollover Exception status, and routes it to a correction workspace where the user mass-replaces terminated workers across multiple ELs or projects. Corrected ELs are re-validated and then roll over; ELs with no exceptions flow through and roll untouched. The Single EL Rollover path reuses the same individual-EL-rollover orchestration the Bulk path invokes per EL, surfaced to the user as a grid of rollover-eligible ELs from which one EL is selected at a time. A single rolled EL is created in Save for Later status; terminated-role and closed-or-suspended-customer issues do not block the roll but must be corrected on the Edit EL page before the EL can be approved.

The problems this solution bridges:

- The current EL Draft functionality requires one-by-one creation, which is not feasible at a volume of 70,000–90,000 letters.

- CER users will have already generated pre-rollover engagements using the existing Mass Roll functionality; the feature must bridge the gap between rolled projects and the corresponding EL Requests.

- During the transition year, prior-year EL Drafts do not exist in CER, so a mass-upload mechanism is required to group projects into ELs.

- Data volumes of hundreds to 1,000+ ELs introduce memory and response-time constraints that require explicit pagination and batch-size controls.

- Terminated workers in EL or project roles cause downstream rollover failures and must be detected and resolved.

# Processes

| **Process** | **1 — Bulk EL Rollover: select and roll over engagement letters (Phase 1)** |
| --- | --- |
| **Goal** | Enable a CER user to filter, select, and submit batches of prior-year ELs for automated rollover. A loop orchestration iterates the selected ELs and invokes the individual-EL-rollover orchestration for each, creating rolled ELs in Approved status and sending them to CPQ and Amelio, with eligibility gating that excludes ELs carrying a terminated executive or a closed or suspended customer. |
| **Business Event/Trigger** | The annual mass Tax engagement rollover requires large volumes of prior-year ELs to be rolled forward to the new period. |
| **Primary Actor(s)** | CER user |
| **Actor(s)** | Primary EL Executive and Requestor (downstream visibility on the Manage EL Requests dashboard) |
| **Pre-conditions** | The user is a CER user. Prior-year ELs exist in CER (created natively or via the transition-year EIB mass upload). Projects to be rolled are in Initialized rollover status. |
| **Post-conditions** | Selected ELs are submitted; eligible, initialized, not-yet-rolled projects are rolled into Approved ELs and sent to CPQ and Amelio. Rolled ELs are visible on the Manage EL Requests dashboard, subject to existing visibility rules. |
| **Flow of Events** | **1. Filter. **The user opens the rollover task and applies filters. Every search requires the EL Period window (Period Start → Period End) plus at least one of EL Market, Primary EL Executive, or Primary EL Customer. Full-market single-run processing is not supported. **2. Review the grid. **Results render as a flat interleaved grid: each EL header row is followed by its project rows. An EL with a mix of already-rolled and not-yet-rolled projects is split into two groups — a non-selectable Already Rolled group and a selectable group. Eligibility (selectable vs. not) is shown via Status / Status Reason. See Appendix for the eligibility rules and grid data model. **3. Select. **The user selects eligible EL groups, with selections persisting across pages. Pagination and the selection batch limit are configured by project count. ELs with a terminated executive are non-selectable in Phase 1 and are rolled via the existing one-at-a-time process. **4. Confirm and submit. **A summary screen shows totals (ELs to create, projects included, exclusions and reasons). On confirmation, the batch is submitted to an Orchestrate for Integrations (O4I) loop orchestration that iterates the selected ELs and invokes the individual-EL-rollover orchestration for each; that orchestration applies the rollover field rules, creates the rolled EL in Approved status, and sends it to CPQ and Amelio. See Appendix for field rules. **5. Track. **O4I emits Integration Messages recording progress and per-EL success/failure for monitoring. |
| **Process** | **2 — Bulk EL Rollover: validate and resolve terminated roles (Phase 2)** |
| **Goal** | After submission, validate every role on each EL and its projects for terminated workers, divert affected ELs to a Rollover Exception status, and let the user mass-replace terminated workers in a correction workspace so corrected ELs re-validate and roll. |
| **Business Event/Trigger** | An EL batch is submitted for rollover in Phase 2, where all ELs are selectable regardless of terminated-role status. |
| **Primary Actor(s)** | CER user |
| **Actor(s)** | Validation orchestration (system actor) |
| **Pre-conditions** | Phase 2 is live (eligibility gating from Phase 1 is removed; all ELs are selectable). An EL batch has been submitted for rollover. |
| **Post-conditions** | ELs with no terminated roles roll over untouched in the same submission. ELs with one or more terminated roles are held in Rollover Exception status until corrected, then re-validated and rolled. |
| **Flow of Events** | **1. Validate. **On submission, a validation orchestration scans every role on each EL and its projects for workers terminated as of the rollover date. The check covers all roles, not just executives. **2. Branch. **An EL with zero terminated roles rolls over immediately. An EL with any terminated role is set to Rollover Exception status (per-EL) and withheld. **3. Correct. **Excepted ELs surface in a net-new correction workspace. The user selects multiple ELs and/or projects and mass-replaces a terminated worker in a role with an active worker. **4. Re-validate and roll. **On save, corrected ELs are automatically re-run through the same validation orchestration; those that clear validation roll over, and any still carrying a terminated role remain in Rollover Exception status for further correction. |
| **Process** | **3 — Single EL Rollover: select and roll over one engagement letter** |
| **Goal** | Enable a CER user to select a single rollover-eligible EL from a grid, roll over that EL and its projects, create the rolled EL in Save for Later status, and take the user straight to the Edit EL page to complete and approve it. The grid is exposed on the Convert Proposal page as the most analogous location, but the EL does not need to originate from a proposal. |
| **Business Event/Trigger** | A user needs to roll a single prior-year EL forward to the new period without going through the bulk selection grid. |
| **Primary Actor(s)** | CER user |
| **Pre-conditions** | The user is a CER user. At least one prior-year EL is eligible for rollover. The associated project is in Initialized rollover status. |
| **Post-conditions** | The rolled EL is created in Save for Later status and the user lands on its Edit EL page. The EL cannot be approved while it carries a terminated role or a closed or suspended customer; once those are corrected and the EL is approved, it is sent to CPQ and Amelio. |
| **Flow of Events** | **1. Select. **From a grid of rollover-eligible ELs (exposed on the Convert Proposal page), the user selects one EL to roll over. **2. Roll. **The individual-EL-rollover orchestration applies the rollover field rules and rolls over the selected EL and its projects, creating the rolled EL in Save for Later status. The roll proceeds regardless of terminated-role or closed-or-suspended-customer issues. **3. Edit. **The user is taken directly to the Edit EL page for the rolled EL to review and complete it, including correcting any terminated roles or closed or suspended customers. **4. Approve and send. **Approval is blocked until all such issues are corrected. On approval, the EL is sent to CPQ and Amelio. |

# Integrations

The following integrations are required to transmit data between Workday and external systems, and to drive the rollover and validation pipeline.

| **Integration Name** | **External System / Mechanism** | **Description** |
| --- | --- | --- |
| EL/project grid data assembly | Workday (WQL/orchestration) | Orchestration that gathers and formats the EL and project data — grouping each EL’s projects by rollover state and flattening into the interleaved EL/project rows with eligibility status — to populate the selection grid. |
| Rollover submission (O4I) | Orchestrate for Integrations | Asynchronous loop orchestration that iterates the submitted EL list and invokes the individual-EL-rollover orchestration for each, applying the rollover field rules, creating each rolled EL in Approved status, and sending it to CPQ and Amelio. Emits Integration Messages for status tracking and per-EL success/failure. |
| Terminated-role validation | Workday (worker status) via orchestration | Per-EL orchestration that checks all roles on the EL and its projects against worker termination status; returns a clean/exception verdict. Reused for initial validation and re-validation after correction (Phase 2). |
| Prior-year EL mass upload | EIB | Transition-year load that groups prior-year projects into EL Requests so the rollover feature has source ELs. |
| Prior-year Project Draft mass upload | EIB | Separate EIB load (distinct from the EL Request upload) for prior-year project draft data. |
| Prior-year CPQ Quote load | EIB | Separate EIB load (distinct from the EL Request upload) for prior-year CPQ Quote data. |
| Single EL rollover (individual-EL-rollover orchestration) | Workday (orchestration) | The individual-EL-rollover orchestration invoked once per EL. Called directly from the Convert Proposal page for Single EL Rollover (creating the EL in Save for Later status) and invoked per EL by the Bulk loop orchestration (creating the EL in Approved status). |

**Note: **No changes are required to the Integration Hub process.

# Reporting Requirements

| **Report Name** | **Description** |
| --- | --- |
| Rollover run status (O4I) | Per-EL success/failure and run progress are surfaced through O4I Integration Messages. The user-facing presentation of these results is to be designed. |

# Data Retention Requirements

Rolled ELs follow the existing CER data model and retention behavior; this feature introduces no new long-term storage beyond the EL and project records it creates. Bulk-path ELs are created in Approved status; Single-path ELs are created in Save for Later status. A Rollover Exception status (or equivalent) is represented on the EL record to support the Bulk-path Phase 2 validation pipeline.

**Open: **Confirm whether any rollover-run audit trail (e.g. O4I Integration Message history) must be retained beyond Workday’s default, and for how long.

# Security Requirements

TBD.

# Signoff/Approval page

| **Version #** | **Approver** | **Date** |
| --- | --- | --- |
| 1.0 |  |  |
|  |  |  |
|  |  |  |

# Appendix

## Eligibility rules

The eligibility rules below govern selection in the Bulk EL Rollover grid. Eligibility is evaluated per EL group, so a split EL can have one non-selectable group and one selectable group at the same time. A group is non-selectable if its primary EL customer is closed or suspended, or if a customer on one of its projects is closed or suspended. In Phase 1, a group whose EL has a terminated executive in any required role is also non-selectable; in Phase 2 this terminated-role gating is removed and terminated roles are handled by the validation orchestration after submission. In the Single EL Rollover path these conditions do not block the roll — the EL rolls into Save for Later status — but they block approval until corrected on the Edit EL page.

| **Condition** | **Selectable (P1)** | **Status / Reason** | **Display ****behavior** |
| --- | --- | --- | --- |
| Project Initialized, not yet rolled | n/a (project row) | — | Normal project row; included when its group is selected |
| Project Not-Initialized | n/a (project row) | — | Dimmed; may be picked up on a later run once initialized |
| Project already rolled | n/a (project row) | — | Appears in the Already Rolled group; excluded from re-roll |
| Closed Primary EL Customer | Not selectable | Not eligible / Closed primary EL customer | EL visible but non-selectable |
| EL group, all projects rolled | Not selectable | Not eligible / Already Rolled | Single non-selectable group; context only |
| Already-rolled group (split EL) | Not selectable | Not eligible / Already Rolled | Context group; its sibling unrolled group is selectable |
| Not-yet-rolled group (split EL) | Selectable | Eligible | Rolls its initialized projects on submit |
| Suspended Customer | Not selectable | Not eligible / Suspended customer | Suspended badge; EL visible but non-selectable |
| Closed Customer on Project | Not selectable | Not eligible / Closed customer on project | Status shown on project row; group non-selectable |
| Terminated exec (any required role) | Not selectable | Not eligible / Terminated executive | P1: checkbox disabled, roll one-at-a-time. P2: handled post-submit |

## Rollover field rules

| **Field** | **Rollover rule** | **Notes** |
| --- | --- | --- |
| EL Name | Year incremented by 1; next EL number sequence generated | Follows the existing naming convention |
| EL Period End Date | Incremented by 1 year from prior-year value |  |
| Primary EL Executive | Carried forward (P1); replaced via correction workspace if terminated (P2) | P1: EL non-selectable if terminated. P2: Rollover Exception until corrected |
| Engagement Executive | Carried forward per project (P1); replaced via correction workspace if terminated (P2) | P1: EL non-selectable if terminated. P2: Rollover Exception until corrected |
| All other roles (EL & project) | Carried forward; any terminated role triggers a Rollover Exception in P2 | P1: not validated beyond executives. P2: full role validation |
| Services CPQ Quote | Copied from prior-year EL in Draft status where available | Copy only where a quote exists |
| Approval status | Bulk path: created in Approved status and sent to CPQ and Amelio. Single path: created in Save for Later status, approved manually on the Edit EL page, then sent to CPQ and Amelio. |  |
| Projects included | Initialized, not-yet-rolled projects in the selected group only | Already-rolled and not-initialized projects excluded; supports partial rollover and multiple runs per EL |

## Flat interleaved grid data model

The selection grid binds to a single flat list where EL header records and project records are interleaved, assembled server-side before render. A mixed EL (some projects rolled, some not) is emitted as two ‘el’ records sharing the same EL id but differing by a groupState field (rolled vs. unrolled). Selection operates on the unrolled group; a submit-time guard ensures a project never rolls twice.

| **rowType** | **Key fields** | **Rendering** |
| --- | --- | --- |
| el | id, groupState (rolled/unrolled), name, customer, customerStatus, exec, periodEnd, status, statusReason | Checkbox (unrolled group only), bold EL name, customer, status badge, exec, period end, status / reason |
| project | elId, groupState, name, market, rolloverStatus, rolled (bool), engExec, yearEnd | Indent indicator, project name, market, rollover status badge, eng exec, year end |

## Pagination and selection

- Pagination is configured by project count, not EL count: a configurable maximum number of projects per page, with EL groups kept intact so an EL’s projects are not split across a page boundary.

- The selection batch limit is configured by project count: a configurable maximum number of projects per rollover batch. Selecting an EL group counts all its initialized, not-yet-rolled projects toward the limit.

- Both thresholds are stored as app-level attributes and adjustable by an administrator without a code deployment. Initial values to be confirmed after performance testing.

## Model Components

No new model components are required. The Mass EL Rollover feature is built as an extension of the existing CER Workday Extend application and reuses its delivered business objects, the single-project rollover orchestration, and the existing security framework; it assumes no structural changes to those components.

## Business Objects

No new business objects are introduced. The feature uses the existing CER Engagement Letter and Project business objects. The Phase 2 Rollover Exception state is represented on the existing EL record (status or equivalent field) rather than as a new business object.

## Security Domains

No new security domains are defined at this time; security is TBD (see Security Requirements). Any roles or domain policies for the Mass EL Rollover feature and the Phase 2 correction workspace will be defined as security is finalized.

Elevating Perspective + Transforming Results

Elevating Perspective + Transforming Results

2  |  Invisors Proprietary and Confidental