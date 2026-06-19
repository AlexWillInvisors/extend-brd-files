# Testing the `extend-brd` skill

How to test a build, judge the output, and fold feedback back into the skill. This
file and `tests/` are **dev artifacts** — they are not included in the distributed
package (`build_package.py` only ships `SKILL.md`, `assets/`, `references/`,
`scripts/`).

Testing is a loop: **install → exercise → judge → write down defects → fold back →
bump version → rebuild → reinstall.**

---

## 0. Where to test

Test in the runtime where the skill actually runs (Claude Code, or claude.ai with
skills) — **not** by running Python locally. The `.docx` generation needs an
unpack/pack/validate path; `brd_edit.py`'s editing core is self-sufficient (it merges
split runs itself), but you still need to unpack/repack the file. Confirm the `docx`
skill (or a plain unzip/zip) is available in that runtime before relying on it.

## 1. Install & confirm

1. Build: `python scripts/build_package.py` → `extend-brd-v1.zip`.
2. Install the zip. (Two install-blockers are guarded by the build: backslash paths
   and description > 1024 chars. If install still fails, that's new — capture it.)
3. Confirm it loaded (`/` menu shows `extend-brd`, or ask "what skills do you have?").
4. Force-invoke once with `/extend-brd` before testing auto-trigger.

## 2. Trigger tests (does it fire on its own?)

Paste each in a fresh session; note whether it engages **without** the slash command:

| Prompt | Should fire? |
|---|---|
| "Turn these scoping notes into a BRD." | yes |
| "Draft requirements for our new EER Extend app." | yes |
| "Poke holes in this requirements doc." | yes (Step 5 review) |
| "Build the RAID log for this." | yes |
| "Verify this BRD / check for hallucinations." | yes (Step 6 verification) |
| "Does this design breach any Extend limits?" | yes |
| "What's the WQL row cap?" | **no** — generic question, not a BRD (checks negative boundary) |

## 3. Exercise the workflows

Use `tests/sample-scoping-notes.md` as repeatable input. The reverse-doc path was
validated against a real app (Event Spend Form); the fixture covers the notes path.

| Scenario | Input / prompt | What to check |
|---|---|---|
| **New BRD from notes** | the fixture + "draft the BRD" | Asks the gap batch up front (problem/volume, VP-role + counts, retention, language); does **not** invent them. Defaults Language to **US English only**. |
| **Proactive limit flag** | same run | Flags the **bulk-close synchronous orchestration on a page iterating a variable list** against the **25 s** page-trigger limit; no false structural flag (3 BOs / 1 domain are within caps). |
| **New BRD from app files** | point at a `model/`+`orchestration/` bundle | BOs/integrations grounded in files; **no** "reverse-documented from…" meta-commentary; `.orchestration` intent recovered via `SendWorkdayApiRequest` / `CreateTextTemplate`. |
| **Revision round** | hand it an existing BRD `.docx`, ask for one change | **Tracked changes** authored "Claude," surgical. (Plain content is only for fresh fills — see the tracked-vs-plain rule.) |
| **Step 5 review (RAID)** | "review this BRD" | Two registers (blunt chat / measured in-doc); **single consolidated grid** by default; cites only **verified** limits; doesn't pad. |
| **Step 6 verification** | "verify this BRD / check for hallucinations" | Self-audits, then walks you through **only flagged items**; every concrete claim traces to the fixture or a gap answer; unsourced claims are flagged `Open:`/cut, never asserted. |

## 4. Judge the output

**Document integrity** (open the `.docx`): cover image, Lato font, TOC, footer typo
("Confidental") preserved; section heading reads **Features** (not "Processes");
validation passes (ignore any benign `intelligence2.xml` line; only `document.xml`
errors are real).

**Content quality** (against `references/filled-example.md`): problem + scale first,
"problems this bridges" bullets, **one paragraph per Flow-of-Events step**, one row
per item in tables, unknowns flagged `Open:`/`TBD`, nothing confabulated.

**Anti-hallucination** (the fixture is ground truth): did it invent a volume number,
retention period, or VP-role user count you never supplied? It shouldn't.

## 5. Capture feedback (be specific)

For each test note: *did it trigger? · right gap questions? · quality vs gold
standard? · `.docx` valid? · exact defect (section + what was wrong).* Concrete beats
vague — "Feature 2 Flow of Events was one run-on paragraph, not per-step" is fixable.

## 6. Fold feedback back in — where each fix lives

| Symptom | File to edit |
|---|---|
| Wrong/missing **triggering** | `SKILL.md` `description` (keep < 1024 chars — the build guards it) |
| **Confabulation / wrong gap questions** | `SKILL.md` step 1 + craft rules; verification = step 6 |
| **Section content** quality | `references/section-guide.md` |
| **docx mechanics / helper** bugs | `references/template-anatomy.md`, `assets/brd_edit.py` |
| **Wrong/missing limits** | `references/extend-limits.md` (verified zone) or re-run `scripts/scrape_extend_limits.py` |
| **RAID format** | `references/raid-example.md` |
| Tracked-vs-plain, validation | `SKILL.md` steps 4 / 7 |

Then: bump `version:` in `SKILL.md` → `python scripts/build_package.py` → reinstall →
re-test the specific scenario. Patch (x.x.+1) for fixes, minor (x.+1.0) for new
capability. The package name stays `extend-brd-v<major>.zip`.

## 7. Known limitations to keep in mind while testing

- **Limits zone 2** (referential-integrity-at-delete, deployment/release windows,
  exact REST/WQL per-page cap) is unverified — the skill should phrase these as
  confirmation questions, not assert them.
- The `docx`-skill dependency in the target runtime hasn't been formally confirmed on
  a live run — note any unpack/pack/validate friction.
