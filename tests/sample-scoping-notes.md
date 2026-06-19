# Test fixture — discovery notes: "Employee Equipment Request" (EER) Extend app

> **This is a synthetic test fixture, not a real engagement.** Use it as repeatable
> input for the *notes → BRD* path (the complement to reverse-documenting from app
> files). Paste it (or point the skill at this file) and ask it to draft the BRD.
> It is engineered to exercise specific skill behaviors — see "What this fixture
> tests" at the bottom. Because it doubles as the ground truth for a verification-pass
> test, treat what's written here as the only sourced facts: anything the BRD asserts
> beyond this (or beyond what you answer to its gap questions) is a hallucination.

---

## Raw notes from the discovery call (messy on purpose)

App name the client uses: **Employee Equipment Request** (they abbreviate it "EER").
Built on Workday Extend. Net-new app, not an extension of an existing one.

**What it does (high level):** employees request work equipment (laptops, monitors,
peripherals). Goes for manager approval, then IT fulfillment. Replaces a SharePoint
form + email chain they use today. They hate the email chain.

**Processes we walked through:**
- *Submit a request.* Employee opens the EER task, picks one or more equipment items
  (each line = item type + estimated cost + justification), attaches a quote if they
  have one, submits. On submit it goes to their manager.
- *Manager review.* Manager approves or sends back. If the **total estimated cost of
  the request is over $2,500**, it also needs **VP approval** after the manager
  (second approval step). Under $2,500, manager approval is enough.
- *IT fulfillment.* After final approval, IT sees the approved request, marks each
  line item fulfilled, and records the asset tag for each delivered item.
- They also mentioned wanting to **bulk-close** old approved-but-never-fulfilled
  requests — select a bunch on a page and close them all at once. This runs off the
  fulfillment screen.

**Data / model (what they've built or plan):**
- An **Equipment Request** business object (header: requester, manager, total cost,
  status).
- A child **Request Line Item** object (item type, estimated cost, justification,
  asset tag, fulfilled flag) — one parent request has many line items.
- An **Attachments** object for the optional quote.
- Statuses on the request: Draft, Submitted, Manager Approved, VP Approved, Approved,
  Fulfilled, Closed, Denied, Sent Back.
- One security domain: **Equipment Request Domain**.

**Integrations / orchestration:**
- On submit, an orchestration looks up the requester's manager (WQL) and routes the
  business process.
- On final approval, an orchestration calls an **external procurement system** (they
  said it's REST, an endpoint called `POST /purchase-orders`) to create a PO, then
  patches the EER record with the returned PO number.
- The **bulk-close** action runs a **synchronous** orchestration from the fulfillment
  page that iterates the selected requests and sets each to Closed. They expect users
  might select "a lot" at once.

**Open things they couldn't answer on the call:**
- Didn't know expected request volume per month / per year.
- Didn't know who exactly owns the VP-approval security role, or how many users.
- Hadn't thought about data retention for closed requests.
- Weren't sure about languages — "just English for now? maybe?" (not confirmed).
- No mention of mobile.

---

## What this fixture tests (for the tester — don't feed this section to the skill)

- **Gap-questioning (step 1):** the notes deliberately omit the *why/scale* and a few
  decisions. A correct run asks a tight batch up front about: business problem +
  expected volume/scale, VP-approval role ownership + user counts, retention for
  closed requests, and language confirmation — and does NOT invent any of them.
- **Language default:** languages are unconfirmed → the BRD should default to **US
  English only**, not the three-language stock text.
- **Proactive limit flag (authoring):** the **bulk-close synchronous orchestration
  launched from a presentation page, iterating a variable/"a lot" of requests**, plausibly
  brushes the **verified 25-second synchronous-orchestration-triggered-by-a-presentation-page**
  limit. A correct run flags this inline (`Open:`) and names it bluntly in chat.
- **Grounded specifics:** the `$2,500` VP-approval threshold, the `POST /purchase-orders`
  REST call, the BO/field/status set, and the single security domain are all sourced
  *here* — the BRD may assert them. Model-component counts are tiny (3 BOs, 1 domain),
  comfortably within limits — so there should be **no** structural limit flag.
- **Verification pass (step 6):** run "verify this BRD / check for hallucinations" and
  confirm every concrete claim traces back to this fixture or to a gap answer; anything
  else should be flagged. Good adversarial check: see if it fabricates a retention
  period, a volume number, or a security-role user count that you never provided.
- **Feature-table fill + per-step Flow of Events + single-grid RAID** (if you also ask
  for a review) exercise the v1.1.0+ defaults.
