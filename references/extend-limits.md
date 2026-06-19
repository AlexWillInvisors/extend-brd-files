# Workday Extend — Platform Limits & Constraints

This is the extend-brd skill's source of truth for Workday Extend platform limits.
The skill consults it to (a) proactively flag, while authoring, any design element
that plausibly brushes a documented limit, and (b) run a full limits audit during a
BRD review. See `SKILL.md` ("Checking the design against Extend limits").

The file has three zones:

1. **Curated (verified)** — limits you have personally confirmed against the live
   Workday documentation, each with its source URL and verification date. Trusted;
   the skill may assert these in a BRD.
2. **Commonly cited (UNVERIFIED)** — constraints the skill references from prior
   project experience but that have **not** been confirmed against a current source.
   Treat these as prompts to check, not facts. In a BRD, flag anything resting on
   one of these as `Open:`/`TBD` until it's verified and promoted to zone 1.
3. **Auto-extracted candidates** — regenerated on each run of
   `scripts/scrape_extend_limits.py`, quoted verbatim from
   `developer.workday.com/documentation` with source URL and retrieval date.

> Maintenance: run `python scripts/scrape_extend_limits.py` (Playwright required —
> see the script header) to refresh zone 3. The crawler PRESERVES zones 1 and 2
> (everything above the auto-generated marker) and only rewrites zone 3.

Format each curated limit as:
- **<limit name>** — <value/threshold>. <scope / when it applies>. Source: <url> (verified <date>).

## 1. Curated limits (verified)

Pulled from Workday's canonical `Reference … Limits` pages by the crawler on
**2026-06-17**. These are quoted, not inferred — but spot-check the exact figure on
the live page before asserting it to a client, and re-run the crawler periodically
since Workday revises these. The design-relevant set:

**Orchestration runtime** (Source: <https://developer.workday.com/documentation/GUID-412c9e62-1ba2-4975-a36b-b794d2b559be/ReferenceOrchestrationRuntimeLimits>):
- **Synchronous orchestration triggered by a presentation page** — **25 seconds**.
  Takes precedence over any timeout configured on the orchestration itself. If total
  processing may exceed 25s, Workday recommends an asynchronous orchestration. *(This
  is the real "25-second" limit — it is NOT the general synchronous cap.)*
- **Synchronous orchestration runtime (Extend apps)** — **5 minutes** total processing.
- **Asynchronous orchestration runtime (Extend apps)** — **48 hours**.
- **Workday Home Card orchestration runtime** — **5 minutes**.
- **Individual process** — **60 minutes (production)** / **45 minutes (non-production)**.
- **Concurrent data on disk** — **2 GB** (file-backed structures; freed when out of scope).
- **Launch message size** — **20 MB**. **Response message size** — **500 MB**.

**Synchronous API ceiling** (Source: <https://developer.workday.com/documentation/GUID-616ce8c7-f1a8-42f0-b090-67c527286638/ConceptWorkdayCloudPlatformAPIGateway>):
- Synchronous Workday API calls through the WCP API Gateway **can't exceed 5 minutes**, except Graph API.

**WQL** (Source: <https://developer.workday.com/documentation/GUID-98ecf957-d369-4439-b541-ae8be7844401/ReferenceWQLResultLimits>):
- WQL queries return a **maximum of 1,000,000 rows**; timeouts of 30 minutes / 5 minutes apply (confirm which applies to your call type on the page).

**Graph API** (Source: <https://developer.workday.com/documentation/GUID-2c1bf9a6-e073-4a5c-a631-6467554546d1/ReferenceLimitsonGraphAPI>):
- **Response page limit** — default 20, **maximum 100**. **Request timeout** — **3 minutes**.
- **Related business object instances** — **maximum 500** returned per multi-instance query. **File attachment** — **30 MB** max.

**Presentation components & scripting** (Source: <https://developer.workday.com/documentation/GUID-54854abf-9a2e-4788-8aa3-9a92ddf1e71e/ReferenceLimitsonPresentationComponents>):
- **PMD request timeout** — **60 seconds**. **Endpoint timeout** — **24 seconds**. **Inbound endpoint timeout on a Card** — **5 seconds**. **Card load timeout on Home Page** — **15 seconds**.
- **editWizard widgets per app** — **15** (combined with flow definitions). **flow definitions per app** — **15** (combined with editWizard widgets).
- **Script CPU time** — **5 seconds** per execution. **Call frames / stack depth** — **25**. **Nested script modules** — **2 levels**. **Script size** — within the **100 KB** max PMD file size. **richText text limit** — **5 MB**. **fileUploader file size** — **10 MB** default (override via `maxFileSize`).

**Model components — per app** (Source: <https://developer.workday.com/documentation/GUID-7d78b63a-766a-449c-839c-f7080e7e67aa/ReferenceLimitsonModelComponents>):
- **Business objects** — **20 per app**. **Security domains** — **10 per app**. **Business processes** — **5 per app**. **Tasks** — **20 per app**. **Reports** — **10 per app**. **Attachments** — **5 per app**. **Model profile groups** — **10 per app**.
- **TEXT fields enabled for search in prompts** — **3 per app**. **SINGLE_INSTANCE + MULTI_INSTANCE fields targeting a Workday-delivered BO** — **25 per app**. **SINGLE_INSTANCE fields with `enableReportingFromTarget=true`** — **5 per app**.

**Model components — per business object** (same source):
- **Fields** — **50 per business object**. **Derived fields** — **40 per business object**. **SINGLE_INSTANCE + MULTI_INSTANCE fields** — **10 per business object**. **Indexable fields** — **5 per business object** (plus auto-indexed SINGLE_INSTANCE fields; derived and MULTI_INSTANCE fields can't be indexed).
- Field text lengths: **name 100 chars**, **label 150 chars**, **description 500 chars**. Numeric: **up to 10 decimal places**, **up to 99 digits**. **Expression length** — **1000 characters**.

**Model components — instances per tenant** (same source):
- **10 million instances** (Extend Essential & Legacy SKUs) / **100 million instances** (Extend Professional SKU), excluding deleted instances. **Shared across all Extend business objects and attachment objects in the tenant.** (Check usage via the *Extend Object Instance Count* report.)
- **Attachment maximum size** — **30 MB**.

**Integrations & web services** (Source: <https://developer.workday.com/documentation/dan1370797408285/ReferenceIntegrationsandWebServiceLimits>):
- **Long-running integrations** — **30-hour** processing limit. **Standard integrations** — **4 hours** (**2 hours** for IMPL tenants). **Concurrent integrations** — up to **5**. **Data-source-step HTTP processing (WWS/RaaS)** — **6 hours**.

**External data** (Source: <https://developer.workday.com/documentation/nja1529966316312/ReferenceExternalDataLimits>):
- **Single file** — **256 MB** compressed. **Concurrent uploads (any method)** — **10**. **Fields per table / per published dataset** — **1,000**.
- Per **24-hour rolling period**: **24,000** buckets created/edited, **24,000** data-change activities/bucket completions, **50,000** files across all containers/buckets, **125 GB** compressed total.

**Web services** (Source: <https://developer.workday.com/documentation/dan1370797408285/ReferenceIntegrationsandWebServiceLimits>):
- **WWS response size** — **max 1,000,000 instances** per response (narrow with request criteria / filters / date ranges). **Rich-text string** — **1,048,576 chars (1 MB)**. Request rate limits vary by tenant worker count (e.g. <3,500 workers: 75,000/24h, 15,000/60-min) — see the page table.

**Configuration packages** (Source: <https://developer.workday.com/documentation/GUID-7f13485a-37bb-4863-9133-b9547602cf03/CreateConfigurationPackagesforApps>):
- A configuration package can contain **up to 300 instances**, including dependencies.

> See zone 3 for the full verbatim extract (including External Data 24-hour bucket/file caps and SOAP numeric-precision limits) and any limits not promoted here.

## 2. Commonly cited constraints (UNVERIFIED — confirm before relying on these)

These are constraints the skill reasons about that the 2026-06-17 crawl did **not**
authoritatively resolve. Each still needs confirmation against the live documentation.
**Do not assert any of these in a client BRD without verifying first** — flag the
affected requirement as `Open:`/`TBD` instead.

- **Referential integrity at delete** — instances referenced by other instances
  cannot be deleted while referenced; affects data-cleanup and retention design.
  Not found on the public developer site via search (2026-06-18) — likely documented
  only in gated Community/model docs. _Needs a `developer.workday.com` source URL to
  promote._ Source: TODO.
- **WQL/REST per-page row caps for paged reads** — zone 1 has the 1M-row WQL ceiling;
  the per-*page* size for paged reads is the open question. **Almost certainly mirrors
  the verified Graph API paging — default 20, maximum 100 per page** (standard Workday
  REST uses a `limit` param, max 100). Treat as ~100/page pending a `developer.workday.com`
  REST/WQL paging page to confirm. Source: TODO (cross-ref Graph API limits in zone 1).
- **Deployment / release windows** (delivery-timeline consideration, not a platform
  governor limit) — Workday ships **feature releases in the second week of March and
  September**, each preceded by a **~5-week preview/test window**; **weekly service
  updates** (bug fixes / off-cycle enhancements) land in a **weekend maintenance
  window**. Relevant to BRD sequencing/timeline RAID, not to design caps. Source:
  Workday release-management guidance (workday.com) — confirm the current schedule for
  the engagement; this is cadence guidance, not a `developer.workday.com` limit.

<!-- ===== AUTO-GENERATED BELOW THIS LINE — regenerated on every crawl; do not hand-edit ===== -->

## Auto-extracted limit candidates

> Crawled 50 page(s) under developer.workday.com; found 242 candidate limit statement(s) on 14 page(s).
> Retrieved: **2026-06-17** via `scripts/scrape_extend_limits.py`.
> Each line is quoted verbatim from the source page. These are *candidates* — confirm the value and context against the live doc before relying on it in a client BRD, then promote the trusted ones into the curated section above.

### Reference: Limits on Graph API - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-2c1bf9a6-e073-4a5c-a631-6467554546d1/ReferenceLimitsonGraphAPI>

- Response page limit — Default is 20. Maximum is 100.
- Graph API request timeout — 3 minutes If the processing time exceeds the limit, the query or mutation will return an error, and the response will include only the processed fields.
- Rate limiting — We rate limit requests when we determine that the number or complexity of queries and mutations start to impact the overall tenant health. A Graph API request returns an HTTP response code of 429 Too Many Requests when other requests overload the resources on your tenant. If you encounter this response code, we recommend that you implement: An exponential back-off retry mechanism for the process that generates the API requests. Caching.
- Related business objects — When you query a multi-instance field as a related business object, a limit of 500 related business object instances will be returned. The request will return an error if there are more than 500 instances in the related business object.
- File attachment size — 30 MB maximum per file attachment. Graph API supports the file types that have been configured on the tenant. See the System Setup section in Administrator Guide: Reference: Edit Tenant Setup - System. Note: If you use Graph API with the fileUploader widget in an Extend app, the limits imposed by the fileUploader overrides the Graph API limits. See the fileUploader limits. See the fileUploader limits in Reference: Limits on Presentation Components.
- Maximum is 100.
- When you query a multi-instance field as a related business object, a limit of 500 related business object instances will be returned.
- 30 MB maximum per file attachment.

### Concept: Orchestration Processes - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-3274e8db-46ed-4c0b-bedc-e36948e26613/ConceptOrchestrationProcesses>

- Can execute for up to 60 minutes in an app that's been promoted to production or 45 minutes in an app not yet promoted to production.
- The 60/45 minute timeout resets.
- Always bear in mind that the maximum time allowed for any single process to complete is 60 minutes on a production tenant or 45 minutes on a nonproduction tenant, while the entire orchestration is subject to its own separate timeout:

### Reference: Orchestration Runtime Limits - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-412c9e62-1ba2-4975-a36b-b794d2b559be/ReferenceOrchestrationRuntimeLimits>

- Workday Home Card orchestration runtime duration — 5 minutes — The total processing time allowed for a Home Card orchestration
- Synchronous orchestration runtime duration (Extend apps only) — 5 minutes — The total processing time allowed for a synchronous orchestration.
- Asynchronous orchestration runtime duration (Extend apps only) — 48 hours — The total processing time allowed for an asynchronous orchestration.
- Workday Integration System orchestration runtime duration — 48 hours — The total processing time allowed for an Integration System orchestration.
- Workday Business Process orchestration runtime callback period — 90 days — The period during which a Business Process triggered by an orchestration must complete.
- Individual process (Prod) — 60 minutes — The maximum time allowed for any process in an app that's been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Individual process (Nonprod) — 45 minutes — The maximum time allowed for any process in an app that hasn't been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Concurrent data in memory — 200 MB — The maximum amount of data an orchestration can have in memory at the same time. The figure includes the data held by all in-scope values in memory as well as any temporary values created while evaluating expressions. It doesn't include the heap space taken up by an orchestration. Note that Workday manages large data items on disk in file-backed data structures. This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.
- Concurrent data on disk — 2 GB — The maximum amount of data an orchestration can have on disk in file-backed data structures at the same time. Note that once values go out of scope, they're cleaned up by the runtime. Any associated data on disk no longer counts towards this limit.
- Launch message size — 20 MB — The maximum size of the request message used to launch an orchestration.
- Response message size — 500 MB — The maximum size of an individual HTTP message response returned from an HTTP API call.
- Synchronous orchestration triggered by a presentation page — 25 seconds — The total processing time allowed for a synchronous orchestration triggered by a presentation page. Takes precedence over any timeouts you configured on the orchestration itself. If you anticipate a total processing time of longer than 25 seconds, Workday recommends that you use an asynchronous orchestration.
- Orchestrations and suborchestrations in an app — 150 — The total number of orchestrations and suborchestrations allowed in a single app. Extend warns you when the total reaches 125.
- Steps in an orchestration — 300 — The total number of steps allowed in an individual orchestration. Extend warns you when the total reaches 200.
- This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.

### Reference: Limits on Presentation Components - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-54854abf-9a2e-4788-8aa3-9a92ddf1e71e/ReferenceLimitsonPresentationComponents>

- Number of pages per app. — 75
- Endpoint timeout. — 24 seconds
- fileUploader attachment file size. To override the default maximum file size, set the maxFileSize attribute of fileUploader to the maximum number of bytes. — 10 MB
- Number of inbound endpoints. — 30 non-deferred inbound endpoints in PMDs and Pods.
- Number of outbound endpoints. — 30
- PMD request timeout. A request can include initial page loads, page submissions, and remote validations. A single request can call multiple endpoints. — 60 seconds
- richText text limit. — 5 MB
- Size of presentation files (.pmd, .amd, .smd, .pod, .script files). — 100 KB
- Size of response payload from an endpoint. — 25 MB
- Number of characters on the text widget and the label attribute on all widgets. — 255
- Number of editWizard widgets per app. — 15 (combined limit with flow definitions).
- Number of flow definitions per app. — 15 (combined limit with editWizard widgets).
- Call frames — The number of levels in a program stack execution, such as recursive function calls, has a maximum of 25.
- CPU time — The CPU time consumed for each script execution has a maximum of 5 seconds. This limit doesn't include endpoint invocation and widget API calls because these calls are executed in separate threads.
- Levels of nested script modules — The maximum number of levels of nested script modules is 2. Example of 2 levels of nested scripts: script1 that includes script 2 that includes script 3. If script 3 includes another script, it exceeds the limit, and receives a validation error.
- Script size — The script size limit within the maximum PMD file size, which is 100 KB.
- Number of Card components per app. — 3
- Number of Card Tenant Settings components per app. — 3
- Number of non-deferred inbound endpoints per Card component. — 2
- Inbound endpoint timeout on a Card. — 5 seconds
- Card load timeout on the Workday Home Page. Note: If the Card load reaches the timeout limit, the Home Page doesn't display the card. — 15 seconds
- Extend Cards on Home Page across the tenant (regardless of Security group). — 4
- Extend Cards per Hub. — 4
- Extend Card per Custom Search Result. — 1
- Extend Card per Journey Step. — 1
- 15 (combined limit with flow definitions).
- 15 (combined limit with editWizard widgets).
- The number of levels in a program stack execution, such as recursive function calls, has a maximum of 25.
- The CPU time consumed for each script execution has a maximum of 5 seconds.
- The maximum number of levels of nested script modules is 2.
- If script 3 includes another script, it exceeds the limit, and receives a validation error.
- The script size limit within the maximum PMD file size, which is 100 KB.

### Concept: Workday Cloud Platform API Gateway - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-616ce8c7-f1a8-42f0-b090-67c527286638/ConceptWorkdayCloudPlatformAPIGateway>

- In general, synchronous Workday API calls that go through WCP API Gateway can’t exceed 5 minutes, except for Graph API.

### Reference: Limits on Model Components - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-7d78b63a-766a-449c-839c-f7080e7e67aa/ReferenceLimitsonModelComponents>

- Number of business objects. — 20 per app.
- Number of security domains. — 10 per app.
- Number of business processes. — 5 per app.
- Number of attachments. — 5 per app.
- Number of tasks. — 20 per app.
- Number of reports. — 10 per app.
- Number of TEXT fields that are enabled for search in prompts. — 3 per app.
- Number of SINGLE_INSTANCE and MULTI_INSTANCE fields where the target is a Workday-delivered business object. — 25 per app.
- Number of SINGLE_INSTANCE fields where enableReportingFromTarget is set to true. — 5 per app.
- name — 100 characters.
- id — Zero to Short.MAX_VALUE (32767).
- label — 150 characters.
- Number of instances (Extend Essential and Legacy SKUs). — 10 million instances per tenant, excluding deleted instances. This limit is shared across all Extend business objects and attachment objects in the tenant. To display the instance count for Extend business objects and attachments in a tenant, access the Extend Object Instance Count report, secured by the Manage: App Manager domain in the System functional area.
- Number of instances (Extend Professional SKU). — 100 million instances per tenant, excluding deleted instances. This limit is shared across all Extend business objects and attachment objects in the tenant. To display the instance count for Extend business objects and attachments in a tenant, access the Extend Object Instance Count report, secured by the Manage: App Manager domain in the System functional area.
- Number of fields. — 50 per business object.
- Number of derived fields. — 40 per business object.
- Number of fields you can index. — 5 per business object, in addition to SINGLE_INSTANCE fields that Extend indexes automatically. You can't index derived fields or MULTI_INSTANCE fields.
- Number of SINGLE_INSTANCE and MULTI_INSTANCE fields. — 10 per business object.
- description — 500 characters.
- Number of fields you can index. — 5 per attachment object, in addition to SINGLE_INSTANCE fields that Extend indexes automatically. You can't index derived fields or MULTI_INSTANCE fields.
- Maximum size of attachment. — 30 MB
- Number of model profile groups. — An app can have up to 10 model profile groups.
- Number of decimal places. — 10
- Number of digits. — 99 (positive or negative).
- Length of expression. — 1000 characters.

### Create Configuration Packages for Apps - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-7f13485a-37bb-4863-9133-b9547602cf03/CreateConfigurationPackagesforApps>

- Configuration packages can contain up to 300 instances, including their dependencies.

### Reference: WQL Result Limits - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-98ecf957-d369-4439-b541-ae8be7844401/ReferenceWQLResultLimits>

- >1 million — None — Query fails.
- >1 million — <=1 million — Query succeeds and returns a maximum of 1 million rows. You can view 10,000 rows at a time.
- <=1 million — None or <=1 million — Query succeeds and returns all rows. You can view 10,000 rows at a time.
- WQL queries return a maximum of 1 million rows.
- 30-minute timeout.
- 5-minute timeout.
- Query succeeds and returns a maximum of 1 million rows.

### Reference: Orchestration Runtime Limits - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-b341f6f0-cd6f-4930-8bcb-723a03f64805/ReferenceOrchestrationRuntimeLimits>

- Workday Home Card orchestration runtime duration — 5 minutes — The total processing time allowed for a Home Card orchestration
- Synchronous orchestration runtime duration (Extend apps only) — 5 minutes — The total processing time allowed for a synchronous orchestration.
- Asynchronous orchestration runtime duration (Extend apps only) — 48 hours — The total processing time allowed for an asynchronous orchestration.
- Workday Integration System orchestration runtime duration — 48 hours — The total processing time allowed for an Integration System orchestration.
- Workday Business Process orchestration runtime callback period — 90 days — The period during which a Business Process triggered by an orchestration must complete.
- Individual process (Prod) — 60 minutes — The maximum time allowed for any process in an app that's been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Individual process (Nonprod) — 45 minutes — The maximum time allowed for any process in an app that hasn't been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Concurrent data in memory — 200 MB — The maximum amount of data an orchestration can have in memory at the same time. The figure includes the data held by all in-scope values in memory as well as any temporary values created while evaluating expressions. It doesn't include the heap space taken up by an orchestration. Note that Workday manages large data items on disk in file-backed data structures. This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.
- Concurrent data on disk — 2 GB — The maximum amount of data an orchestration can have on disk in file-backed data structures at the same time. Note that once values go out of scope, they're cleaned up by the runtime. Any associated data on disk no longer counts towards this limit.
- Launch message size — 20 MB — The maximum size of the request message used to launch an orchestration.
- Response message size — 500 MB — The maximum size of an individual HTTP message response returned from an HTTP API call.
- Synchronous orchestration triggered by a presentation page — 25 seconds — The total processing time allowed for a synchronous orchestration triggered by a presentation page. Takes precedence over any timeouts you configured on the orchestration itself. If you anticipate a total processing time of longer than 25 seconds, Workday recommends that you use an asynchronous orchestration.
- Orchestrations and suborchestrations in an app — 150 — The total number of orchestrations and suborchestrations allowed in a single app. Extend warns you when the total reaches 125.
- Steps in an orchestration — 300 — The total number of steps allowed in an individual orchestration. Extend warns you when the total reaches 200.
- This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.

### Reference: Limits on Extend App Components - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-c58fce8e-198e-402e-9846-e1be8a429bad/ReferenceLimitsonExtendAppComponents>

- Number of business objects. — 20 per app.
- Number of security domains. — 10 per app.
- Number of business processes. — 5 per app.
- Number of attachments. — 5 per app.
- Number of tasks. — 20 per app.
- Number of reports. — 10 per app.
- Number of TEXT fields that are enabled for search in prompts. — 3 per app.
- Number of SINGLE_INSTANCE and MULTI_INSTANCE fields where the target is a Workday-delivered business object. — 25 per app.
- Number of SINGLE_INSTANCE fields where enableReportingFromTarget is set to true. — 5 per app.
- name — 100 characters.
- id — Zero to Short.MAX_VALUE (32767).
- label — 150 characters.
- Number of instances (Extend Essential and Legacy SKUs). — 10 million instances per tenant, excluding deleted instances. This limit is shared across all Extend business objects and attachment objects in the tenant. To display the instance count for Extend business objects and attachments in a tenant, access the Extend Object Instance Count report, secured by the Manage: App Manager domain in the System functional area.
- Number of instances (Extend Professional SKU). — 100 million instances per tenant, excluding deleted instances. This limit is shared across all Extend business objects and attachment objects in the tenant. To display the instance count for Extend business objects and attachments in a tenant, access the Extend Object Instance Count report, secured by the Manage: App Manager domain in the System functional area.
- Number of fields. — 50 per business object.
- Number of derived fields. — 40 per business object.
- Number of fields you can index. — 5 per business object, in addition to SINGLE_INSTANCE fields that Extend indexes automatically. You can't index derived fields or MULTI_INSTANCE fields.
- Number of SINGLE_INSTANCE and MULTI_INSTANCE fields. — 10 per business object.
- description — 500 characters.
- Number of fields you can index. — 5 per attachment object, in addition to SINGLE_INSTANCE fields that Extend indexes automatically. You can't index derived fields or MULTI_INSTANCE fields.
- Maximum size of attachment. — 30 MB
- Number of decimal places. — 10
- Number of digits. — 99 (positive or negative).
- Length of expression. — 1000 characters.
- Number of pages per app. — 75
- Endpoint timeout. — 24 seconds
- fileUploader attachment file size. To override the default maximum file size, set the maxFileSize attribute of fileUploader to the maximum number of bytes. — 10 MB
- Number of inbound endpoints. — 30 non-deferred inbound endpoints in PMDs and Pods.
- Number of outbound endpoints. — 30
- PMD request timeout. A request can include initial page loads, page submissions, and remote validations. A single request can call multiple endpoints. — 60 seconds
- richText text limit. — 5 MB
- Size of presentation files (.pmd, .amd, .smd, .pod, .script files). — 100 KB
- Size of response payload from an endpoint. — 25 MB
- Number of characters on the text widget and the label attribute on all widgets. — 255
- Number of editWizard widgets per app. — 15 (combined limit with flow definitions).
- Number of flow definitions per app. — 15 (combined limit with editWizard widgets).
- Call frames — The number of levels in a program stack execution, such as recursive function calls, has a maximum of 25.
- CPU time — The CPU time consumed for each script execution has a maximum of 5 seconds. This limit doesn't include endpoint invocation and widget API calls because these calls are executed in separate threads.
- Levels of nested script modules — The maximum number of levels of nested script modules is 2. Example of 2 levels of nested scripts: script1 that includes script 2 that includes script 3. If script 3 includes another script, it exceeds the limit, and receives a validation error.
- Script size — The script size limit within the maximum PMD file size, which is 100 KB.
- Number of Card components per app. — 3
- Number of Card Tenant Settings components per app. — 3
- Number of non-deferred inbound endpoints per Card component. — 2
- Inbound endpoint timeout on a Card. — 5 seconds
- Card load timeout on the Workday Home Page. Note: If the Card load reaches the timeout limit, the Home Page doesn't display the card. — 15 seconds
- Extend Cards on Home Page across the tenant (regardless of Security group). — 4
- Extend Cards per Hub. — 4
- Extend Card per Custom Search Result. — 1
- Extend Card per Journey Step. — 1
- Response page limit — Default is 20. Maximum is 100.
- Graph API request timeout — 3 minutes If the processing time exceeds the limit, the query or mutation will return an error, and the response will include only the processed fields.
- Rate limiting — We rate limit requests when we determine that the number or complexity of queries and mutations start to impact the overall tenant health. A Graph API request returns an HTTP response code of 429 Too Many Requests when other requests overload the resources on your tenant. If you encounter this response code, we recommend that you implement: An exponential back-off retry mechanism for the process that generates the API requests. Caching.
- Related business objects — When you query a multi-instance field as a related business object, a limit of 500 related business object instances will be returned. The request will return an error if there are more than 500 instances in the related business object.
- File attachment size — 30 MB maximum per file attachment. Graph API supports the file types that have been configured on the tenant. See the System Setup section in Administrator Guide: Reference: Edit Tenant Setup - System. Note: If you use Graph API with the fileUploader widget in an Extend app, the limits imposed by the fileUploader overrides the Graph API limits. See the fileUploader limits. See the fileUploader limits in Reference: Limits on Presentation Components.
- Workday Home Card orchestration runtime duration — 5 minutes — The total processing time allowed for a Home Card orchestration
- Synchronous orchestration runtime duration (Extend apps only) — 5 minutes — The total processing time allowed for a synchronous orchestration.
- Asynchronous orchestration runtime duration (Extend apps only) — 48 hours — The total processing time allowed for an asynchronous orchestration.
- Workday Integration System orchestration runtime duration — 48 hours — The total processing time allowed for an Integration System orchestration.
- Workday Business Process orchestration runtime callback period — 90 days — The period during which a Business Process triggered by an orchestration must complete.
- Individual process (Prod) — 60 minutes — The maximum time allowed for any process in an app that's been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Individual process (Nonprod) — 45 minutes — The maximum time allowed for any process in an app that hasn't been promoted to a production tenant. For more information, see: Concept: Orchestration Processes.
- Concurrent data in memory — 200 MB — The maximum amount of data an orchestration can have in memory at the same time. The figure includes the data held by all in-scope values in memory as well as any temporary values created while evaluating expressions. It doesn't include the heap space taken up by an orchestration. Note that Workday manages large data items on disk in file-backed data structures. This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.
- Concurrent data on disk — 2 GB — The maximum amount of data an orchestration can have on disk in file-backed data structures at the same time. Note that once values go out of scope, they're cleaned up by the runtime. Any associated data on disk no longer counts towards this limit.
- Launch message size — 20 MB — The maximum size of the request message used to launch an orchestration.
- Response message size — 500 MB — The maximum size of an individual HTTP message response returned from an HTTP API call.
- Synchronous orchestration triggered by a presentation page — 25 seconds — The total processing time allowed for a synchronous orchestration triggered by a presentation page. Takes precedence over any timeouts you configured on the orchestration itself. If you anticipate a total processing time of longer than 25 seconds, Workday recommends that you use an asynchronous orchestration.
- Orchestrations and suborchestrations in an app — 150 — The total number of orchestrations and suborchestrations allowed in a single app. Extend warns you when the total reaches 125.
- Steps in an orchestration — 300 — The total number of steps allowed in an individual orchestration. Extend warns you when the total reaches 200.
- Access token on Graph API Explorer, REST API Explorer, SOAP API Explorer — 60 minutes
- >1 million — None — Query fails.
- >1 million — <=1 million — Query succeeds and returns a maximum of 1 million rows. You can view 10,000 rows at a time.
- <=1 million — None or <=1 million — Query succeeds and returns all rows. You can view 10,000 rows at a time.
- 15 (combined limit with flow definitions).
- 15 (combined limit with editWizard widgets).
- The number of levels in a program stack execution, such as recursive function calls, has a maximum of 25.
- The CPU time consumed for each script execution has a maximum of 5 seconds.
- The maximum number of levels of nested script modules is 2.
- If script 3 includes another script, it exceeds the limit, and receives a validation error.
- The script size limit within the maximum PMD file size, which is 100 KB.
- Maximum is 100.
- When you query a multi-instance field as a related business object, a limit of 500 related business object instances will be returned.
- 30 MB maximum per file attachment.
- This feature means that an orchestration can have many values that are larger than the 20 MB limit in scope concurrently because they're not held in memory.
- In general, synchronous Workday API calls that go through WCP API Gateway can’t exceed 5 minutes, except for Graph API.
- WQL queries return a maximum of 1 million rows.
- 30-minute timeout.
- 5-minute timeout.
- Query succeeds and returns a maximum of 1 million rows.

### Define HTTP Retry Policies - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-d04cc763-a044-423f-b39e-1348dfd76a87/DefineHTTPRetryPolicies>

- Maximum Total Retries — Specify the maximum number of HTTP retries that Orchestration Builder can attempt. You can't specify more than 60 retries.

### Define HTTP Polling Configurations - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/GUID-f6359618-dbbf-4116-b354-b4a6653f9ee2/DefineHTTPPollingConfigurations>

- Total Polling Duration (Minutes) — Specify how long polling should last in total. The maximum value allowed is 2880 minutes (48 hours).
- The maximum value allowed is 2880 minutes (48 hours).
- The minimum value allowed is 1 minute and the maximum is 60 minutes.
- Orchestrate employs exponential backoff, meaning it conserves resources by doubling the interval between retries after each failed attempt up to the interval maximum of 60 minutes.
- The orchestration initiates the file processing and then, using the HTTP polling configuration, checks the external job status endpoint after 2 minutes, then after another 4 minutes, then again after 8 minutes, and so on up to the 60 minute interval limit, until both stop conditions are met or until the total polling time of 120 minutes has elapsed.

### Reference: Integrations and Web Service Limits - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/dan1370797408285/ReferenceIntegrationsandWebServiceLimits>

- Customer Size — Maximum Requests per 24-hour Period — Maximum Requests in a single 60-minute Period
- DocuSign Integration API Requests — Hourly API call limits: 3000 by default. Burst API call limits: 500 calls per 30 seconds. Note: These numbers are currently accurate. For more information, refer to DocuSign API Rate Call Limits or contact DocuSign directly.
- EIBs: Runtime — Processing time for: Outbound EIBs retrieving custom report or web service data: 30 hours. Any pause in processing doesn't count toward the 30-hour limit. Inbound EIBs loading Workday Web Service or Custom Object data: 5 hours. Inbound EIBs creating the Failure Report, Errors & Warnings spreadsheet, and Add Errors to Attachment spreadsheet: 2 hours.
- Integration Event Maximum Processing Time — 7 days. Exception: ADP Payroll CSV integrations.
- Studio Integrations: Put Integration Message Sub-Assembly — 500 times in an integration event. This limit doesn't include: Messages with attachments and targets. Messages that change the integration event status.
- Studio Integrations: Runtime — Total of all files generated during the integration run: 3 GB (compressed). Single file generated during the integration run: 1 GB (compressed). Memory used during processing: 12 GB. Integrations can use several times the amount of memory that the output files require. Time limitation: 2 hours.
- Studio Integrations: File-Backed Managed Data (FBMD) Limit — The maximum document size that a Studio integration can handle: 16 GB.
- Workday Web Services: Attachments — For SOAP and REST: Maximum Attachment Size: 30MB Maximum Image Size: 30MB
- Workday Web Services: Currency — Decimal (total_digits, fraction_digits) Example: decimal (18, 6) implies that the given SOAP API has a limit of a maximum of 18 digits with 6 of them being decimal digits. It's a dynamic value specified in the Workday Web Services (WWS) Directory on Community under the Type/Value column.
- Workday Web Services: Response Size Limit — Maximum number of instances in a web service response: 1 million. You can reduce the number of instances returned by using request criteria, response filters, or date ranges. Workday doesn't log web service responses. You can specify external integration HTTP headers with your requests to enable tracking in server logs.
- Workday Web Services: Rich Text String Size Limit — Maximum number of characters: 1,048,576 or 1MB.
- Less than 3,500 workers (ME) — 75,000 — 15,000
- Less than 10,000 workers (LE) — 100,000 — 30,000
- Less than 100,000 workers (LE) — 250,000 — 75,000
- More than 100,000 workers — 350,000 — 100,000
- For Paged API requests, avoid setting a strict HTTP timeout for page 1 requests to ensure that Workday has enough time to build a cache for subsequent calls.
- Maximum Requests per 24-hour Period
- Maximum Requests in a single 60-minute Period
- The processing limit for long running integrations is 30 hours.
- The processing limit for standard integrations is 4 hours (2 hours for IMPL tenants).
- On the delivery step, Workday applies the 30-hour limit.
- On the data source step, Workday applies a 6-hour HTTP processing request limit for Workday Web Services and Reports-as-a-Service (RaaS).
- up to 5 concurrent integrations if resources are available at that time.
- Up to 4 hours.
- Workday allows some connectors to run for up to 30 hours.
- Any pause in processing doesn't count toward the 30-hour limit.
- decimal (18, 6) implies that the given SOAP API has a limit of a maximum of 18 digits with 6 of them being decimal digits.
- decimal (4, 0)>0 implies that the given SOAP API has a limit of 4 digits, no fractions, and no negative numbers.
- decimal (2, 1) implies that the given SOAP API has a limit of 2 digits, 1 fraction, and negative numbers.

### Reference: External Data Limits - Documentation | Workday Developers
Source: <https://developer.workday.com/documentation/nja1529966316312/ReferenceExternalDataLimits>

- Maximum size of a single file — 256 MB compressed
- Maximum number of buckets that can be created or edited in a 24-hour rolling period — 24,000
- Maximum number of data change activities and bucket completions that can be run in a 24-hour rolling period — 24,000
- Maximum number of concurrent uploads using any method — 10
- Maximum number of files in all file containers and buckets in a 24-hour rolling period — 50,000
- Maximum size of all files in all file containers and buckets in a 24-hour rolling period — 125 GB compressed
- Maximum number of fields in a table. — 1,000
- Maximum number of fields in a dataset, including Prism calculated fields, when you publish. — 1,000
- Maximum number of buckets that can be created or edited in a 24-hour rolling period
- Maximum number of data change activities and bucket completions that can be run in a 24-hour rolling period
- Maximum number of files in all file containers and buckets in a 24-hour rolling period
- Maximum size of all files in all file containers and buckets in a 24-hour rolling period

