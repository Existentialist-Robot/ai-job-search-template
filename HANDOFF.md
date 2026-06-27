# HANDOFF — [YOUR_NAME] Job Search

**Last updated:** [DATE]
**Working directory:** `[PATH_TO_THIS_REPO]`
**Owner:** [YOUR_NAME] ([profile in CLAUDE.md](CLAUDE.md))

`job_search_tracker.csv` is the unified application index, and `working/exports/` is the canonical packet/PDF archive. This file is narrative handoff context, not the canonical application index. Start here, then read the current files in `working/active/`.

---

## Quick Start

When resuming:

1. Read this file end to end.
2. Read everything in [`working/active/`](working/active/).
3. Use [`CLAUDE.md`](CLAUDE.md) for candidate profile, Canva workflow, and verification rules.
4. Confirm with [YOUR_NAME] if anything in Current Sprint looks stale.

Before stopping:

1. Update this file's Current Sprint, Active Documents, and Pending Items.
2. Move stale active docs to [`working/archive/`](working/archive/).
3. Keep helper scripts in [`working/scripts/`](working/scripts/) and generated JSON in [`working/scripts/generated/`](working/scripts/generated/).
4. Update `job_search_tracker.csv` when applications are submitted or closed without submission.

---

## Current Sprint

**Window:** [START_DATE] to [END_DATE]

**Active effort:** [DESCRIPTION — e.g. "3 applications in progress from June sweep; pair 1 ported, pairs 2–3 pending."]

| Priority | Workstream | Artifact | Next action |
|----------|------------|----------|-------------|
| 1 | [e.g. Interview prep — Role at Org] | `working/active/interview_prep_role.md` | [e.g. Rehearse answer bank] |
| 2 | [e.g. Fresh apply-list search] | _pending_ | [e.g. Run /pipeline sweep] |

**Level reminder:** [YOUR acceptance target — e.g. Senior Manager / Director scope and roughly $100K+. Sub-level roles only worth pursuing when salary/scope clearly clears the bar.]

---

## Application Finals Archive (`working/exports/`)

**Every application — past and present — is filed under `working/exports/` as the single source of truth.** Structure:

```
working/exports/<YYYY-MM (Mon 'YY)>/<YY-MM-DD - Company - Role>/
    [YOUR_NAME]_Resume.pdf
    [YOUR_NAME]_Cover_Letter.pdf
    copy/
        packet_slug_date.md       # per-app draft/review record
        review_agents_date.md     # agent review findings
    <Interview Research>.md       # any per-app interview artifacts
```

- Month folders sort chronologically; app folders are date-first for autosort.
- Working/record docs and interview prep live WITH their application (not in generic archive) whenever they map 1:1 to one role. Only multi-app sprint notes and intermediate pair-reviews stay in `working/archive/`.

---

## Active Documents

`working/active/` is cleaned to live work only:

- _[List current active docs here — e.g. job sweep doc, current interview prep]_

---

## Repo Structure

```text
ai-job-search/
|-- HANDOFF.md                  # this file: state + workflow + rules
|-- CLAUDE.md                   # candidate profile, Canva workflow, verification checklist
|-- GETTING_STARTED.md          # setup guide + agent onboarding
|-- job_search_tracker.csv
|-- working/
|   |-- active/                 # live work only (current interview doc + fresh search)
|   |-- exports/                # FINALS ARCHIVE: every submitted app (PDFs + drafts), by month/date
|   |-- archive/                # superseded multi-app sprint notes + intermediate reviews
|   `-- scripts/                # Canva helper scripts + viz
|       `-- generated/          # generated operation/copy JSON
|-- cv/
|-- cover_letters/
`-- .claude/skills/
```

---

## Submitted This Calendar Quarter

Tracker file: [`job_search_tracker.csv`](job_search_tracker.csv)

_[Update this list as you submit applications. Example format:]_

- [Role] — [Org] — [Date]

---

## Hiring Probability Filter

Do not add a role to the apply list unless there is a minimum low-medium realistic chance you actually get hired. Skills match is not enough.

Passes:

- Generalist mandates: policy, strategy, program design, stakeholder engagement, ecosystem/innovation/economic development
- Manager, Senior Manager, or Director level where outsider perspective could plausibly be valued
- Roles aligned to your target sectors (see CLAUDE.md)

Fails despite skills match:

- Specialist domains where you lack the credential or track record
- Executive/VP-level without a strong identity-match reason
- Near-certain internal-only competitions

Your bridge into target sectors:

[DESCRIBE YOUR BRIDGE — e.g. grant relationships, awards, stakeholder recognition, relevant past roles]

---

## Job Search Infrastructure

### Search Execution

**HARD RULE — small direct sweeps only.** Run job searches as a handful of **foreground `WebSearch`/`WebFetch` calls the main agent makes itself**, then write one consolidated doc. **NEVER launch background or long-running multi-agent search jobs** — they burn tokens and silently fail. Keep each sweep to ~4–6 targeted queries against known employer portals; if more coverage is needed, run another small sweep, not a bigger agent. Fail-proof beats exhaustive.

**Sweep-doc format:** embed each posting link **inside the results table near the top** (hyperlink the role cell) — no separate "Links" section at the bottom.

### Job Boards to Search

See `.claude/skills/pipeline/boards.md` for the full registry of confirmed queryable boards.

Quick reference — highest-signal sources:
1. [Your government portal, e.g. jobpostings.alberta.ca]
2. [LinkedIn Jobs — saved search for your target roles + location]
3. [Your target org career pages]
4. CharityVillage (if non-profit sector)
5. GC Jobs / regional development agencies (if federal)

### Last Sweeps

| Source | Last checked | Notes |
|--------|--------------|-------|
| [Board name] | [Date] | [Notes] |

### Portals Requiring Manual Browser Check

| Portal | URL | Cadence |
|--------|-----|---------|
| [Org name] | [URL] | [e.g. Weekly] |

---

## Application Workflow

1. Evaluate fit first: skills, experience, behavior/culture, career alignment, and realistic hiring probability.
2. Do not draft for roles below the threshold.
3. Manual-open gate before Canva work: you must confirm live portal status before porting.
4. Draft edits as active docs only when they are current. Archive stale drafts promptly.
5. Use Canva design `[YOUR_CANVA_DESIGN_ID]` and the workflow in [`CLAUDE.md`](CLAUDE.md).
6. Run verification before presenting or porting.
7. Track submissions and non-submissions in `job_search_tracker.csv`.

---

## Hard Rules

- Never fabricate job postings.
- Salary floor: $[YOUR_FLOOR]. Real target: $[YOUR_TARGET_RANGE].
- No specialist-domain applications unless there is a clear, realistic bridge.
- Keep outputs direct and tight.

---

## Pending Items

_[List outstanding to-dos here. Example:]_

1. Verify open status on [Role A], [Role B] before porting.
2. Update `job_search_tracker.csv` with [recent submission].
3. Run next broad sweep after [Date].

---

## Reference

- Candidate profile, Canva workflow, verification checklist: [`CLAUDE.md`](CLAUDE.md)
- Setup guide: [`GETTING_STARTED.md`](GETTING_STARTED.md)
- Current active docs: [`working/active/`](working/active/)
- Archived prior work: [`working/archive/`](working/archive/)
- Canva helper scripts: [`working/scripts/`](working/scripts/)
