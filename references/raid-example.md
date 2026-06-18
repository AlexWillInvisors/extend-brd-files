# Worked example — Open Questions & Risks (RAID) output

This is the gold-standard for the **review output** (SKILL.md step 5): the internal
model is a full RAID log plus Open Questions (**R**isks, **A**ctions, **I**ssues,
**D**ecisions, + Open Questions), surfaced in two registers. It is grounded in the
same engagement as `filled-example.md` (CER Mass EL Rollover) so you can see how real
design facts and the verified limits in `extend-limits.md` turn into RAID items.

Two things to notice:
- **The chat register names platform limits bluntly and cites `extend-limits.md`.**
  The in-doc register says the same thing as a measured open item, no scary numbers.
- **Every item traces to something concrete** — a stated volume, a TBD section, a
  page-triggered orchestration, a verified cap. Nothing is padded. Buckets with no
  items are simply omitted.

---

## Register 1 — Chat summary (internal, blunt)

Grouped by the five buckets. This is for the consultant; it can name caps and
delivery risk directly.

**Open Questions**
- **Grid/batch volumes.** The BRD cites 70,000–90,000 letters overall and "hundreds
  to 1,000+ ELs" per run, but the per-page and per-batch project counts are "to be
  confirmed after performance testing." We need expected peak rows per filtered grid
  query and per submit to size against the limits below.
- **Tenant Extend SKU + current instance count.** Extend instances are capped per
  tenant and **shared across all Extend BOs + attachment objects**: 10M (Essential/
  Legacy) vs 100M (Professional) — see `extend-limits.md`. Transition-year EIB uploads
  plus 70–90k rolled ELs and their projects consume against that shared pool. Pull the
  *Extend Object Instance Count* report to confirm headroom.
- **Single-roll orchestration mode.** The individual-EL-rollover orchestration is
  invoked from the Convert Proposal page. If it runs synchronously off the page it's
  under the **25-second presentation-page sync cap** (`extend-limits.md`). Confirm
  sync vs async and that one roll completes within 25s.
- **Audit-trail retention.** Already flagged Open in the BRD: must O4I Integration
  Message history be retained beyond Workday's default, and for how long?
- **Security model.** Security Requirements is TBD — which roles own the rollover
  task, the Phase 2 correction workspace, and admin of the pagination/batch attributes?

**Risks**
- **Grid assembly may blow the 25s page-trigger cap.** The grid data-assembly
  orchestration is page-triggered and flattens each EL's projects into an interleaved
  grid. For large filtered sets this is the most likely place to hit the **25-second
  synchronous-orchestration-triggered-by-a-presentation-page** limit → grid timeout.
  WQL itself caps at 1M rows (fine here), but the 25s wall is the real exposure.
- **Instance-cap headroom.** If the tenant is on Essential/Legacy (10M shared cap) and
  already loaded, the transition-year uploads + rollover volume could approach it.
- **Threshold tuning vs. timeline.** Pagination/batch values are unset pending perf
  testing; if testing slips, Nov go-live is at risk, and values set too high reintroduce
  the timeout/volume risks above.
- **Phase 2 scope.** The correction workspace + cross-EL mass-replace is net-new UI +
  orchestration; effort/scope risk if pulled toward the Nov date.
- **Client data dependency.** Go-live depends on clean transition-year EIB data (EL
  Request, Project Draft, CPQ Quote) delivered on schedule; inbound EIB processing also
  has its own runtime limit (`extend-limits.md`).

**Actions**
- Run performance testing to set max-projects-per-page and batch limit before go-live — *delivery team*.
- Define rollover/correction/admin security roles + domains; feeds the Security section — *client security + Invisors*.
- Confirm Extend SKU and pull current instance count via the Extend Object Instance Count report — *client admin*.
- Confirm sync/async mode of grid-assembly and single-roll orchestrations; measure against 25s — *dev*.

**Issues** (already realized, not just potential)
- Security Requirements is currently **TBD** — a required section is unresolved and blocks signoff.
- Initial pagination/selection threshold values are undefined in the BRD; downstream design depends on numbers not yet known.

**Decisions**
- **Bulk path uses an asynchronous O4I loop orchestration** (not synchronous) —
  deliberately, so large batches run under the 48h async window rather than the 5min/25s
  sync caps. (Made.)
- **No new business objects / model components** — the feature extends the existing CER
  app, so the per-app BO cap (20) and per-BO field cap (50) are not engaged. (Checked, clear.)
- **Pagination + batch thresholds stored as app-level attributes**, admin-adjustable
  without a code deployment. (Made.)
- **Phase 1 vs Phase 2 phasing** — Phase 1 only for Nov go-live; confirm Phase 2 timing. (Owed.)

---

## Register 2 — In-doc subsection (client-facing, measured)

Goes in the BRD as an Appendix subsection titled **"Open Questions & Risks"**
(`Heading2`). **Default: a single consolidated grid** — one table, one row per item,
the **Type** column naming the bucket (Open Question / Risk / Action / Issue /
Decision) and rationale/impact folded into the Description. Label with **bold runs**,
not `Heading3` (this template's Heading3 is too faint). Same substance as the chat
register, framed as constructive items to resolve before signoff — note the softened
wording (e.g. "confirm expected volumes," not "this will blow the 25s cap").

| Type | Item / Description | Owner | Target / Date |
| --- | --- | --- | --- |
| Open Question | Confirm expected peak ELs/projects per filtered grid view and per rollover batch — sizes the pagination/batch thresholds and validates grid responsiveness at scale. | Invisors + client | Before build |
| Open Question | Confirm the tenant's Workday Extend edition and current Extend object instance usage — rollover and transition-year uploads draw on the shared instance allowance. | Client admin | Open |
| Open Question | Confirm whether Single EL Rollover (Convert Proposal page) runs interactively or in the background. | Development | Open |
| Open Question | Confirm any required retention period for rollover-run history (O4I Integration Messages). | Invisors + client | Before signoff |
| Risk | Assembling the selection grid for very large filtered sets may affect interactive responsiveness (slow/timed-out load at peak). Mitigation: right-size pagination by project count; performance-test before go-live. | Delivery team | Before go-live |
| Risk | Rollover + transition-year volumes consume the tenant's shared Extend instance allowance, reducing headroom for other apps. Mitigation: confirm edition + current usage; plan against headroom. | Client admin | Open |
| Risk | Pagination/batch thresholds are set only after performance testing — tuning sits on the path to the November go-live. Mitigation: schedule testing early; thresholds are admin-adjustable. | Delivery team | Before go-live |
| Risk | The Phase 2 correction workspace is net-new functionality (additional build effort). Mitigation: keep Phase 2 post-go-live; confirm phasing. | Invisors | Phase 2 |
| Issue | Security Requirements is currently TBD — a required section is unresolved and blocks signoff. | Client security + Invisors | Before signoff |
| Action | Define rollover, correction-workspace, and admin security roles/domains. | Client security + Invisors | Before signoff |
| Decision | Bulk rollover runs as an asynchronous (background) orchestration — supports large batches without interactive time limits. | — | Jun 2025 |
| Decision | No new business objects introduced; the feature extends the existing CER app (stays within app component limits). | — | Jun 2025 |
| Decision | Pagination/batch thresholds are configurable app settings, adjustable without a deployment. | — | Jun 2025 |

**Alternative (long RAID): one small table per non-empty bucket.** When several
buckets each carry many items, per-bucket tables can read better than one long grid.
Same content, split by bucket — Open Questions (**Item | Why it matters**), Risks
(**Risk | Impact | Mitigation**), Actions (**Action | Owner | Target/status**),
Issues (**Item | Resolution needed**), Decisions (**Decision | Rationale | Date**) —
each label a **bold run**, not `Heading3`.

> Note: this is illustrative, not a transcription of the real Forvis deliverable's
> review (that BRD predates the review feature). Use it for shape and register, and
> defer to any RAID/open-items format the team standardizes on.
