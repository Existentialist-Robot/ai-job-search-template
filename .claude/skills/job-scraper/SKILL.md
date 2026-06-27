# Job Search

**name:** job-search
**description:** Searches Canadian job sources for new positions matching the candidate's profile. Uses WebSearch + WebFetch. Triggers on: job search, find jobs, search jobs, new jobs, any new positions, /search, /scrape
**allowed-tools:** Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Agent, TodoWrite

---

## How It Works

Searches target job boards and Canadian ecosystem orgs using WebSearch and WebFetch. Deduplicates against previously seen jobs. Applies a **minimum low-medium hiring probability filter** before presenting results — skills match alone is not enough to list a role.

## Invocation

- "Find new jobs" / "Any new positions?" / "Run a job search"
- "/search" or "/scrape"
- Optional focus: "/search government" or "/search ecosystem" or "/search broad"

---

## CLI Tool Status

Most job board CLI tools are broken or blocked. Fall back directly to WebSearch + WebFetch.

| Tool | Status | Reason |
|------|--------|--------|
| Canada Job Bank search | ❌ Broken | Uses JSF/AJAX — GET requests return 0 results. Needs headless browser. |
| ca.indeed.com direct | ❌ Blocked | Cloudflare bot protection. |

---

## Execution Steps

### Step 0: Load State

1. Read `job_scraper/seen_jobs.json` (create if missing — start with `{"seen": {}}`)
2. Read `job_search_tracker.csv` to extract already-applied companies+roles
3. Read `.claude/skills/pipeline/boards.md` for query strategy

### Step 1: Search

Run WebSearch queries targeting sources from `boards.md`. Default: top 3 priority categories. "broad" = all categories.

**Primary sources (confirmed working via WebFetch):**
- Target government career portal (from CLAUDE.md / boards.md)
- Target quasi-gov or ecosystem org career pages
- Sector-specific boards (CharityVillage, MINJobs, etc. as relevant)

**Secondary sources (use WebSearch first, then WebFetch individual postings):**
- Google → ATS pages (Greenhouse, Ashby, Lever)
- Government job portals (need WebSearch to surface poster IDs)

### Step 2: Fetch & Verify

For each promising result from Step 1:
- Use WebFetch to retrieve the full job posting
- Extract: **title**, **ministry/org**, **salary**, **posting date**, **closing date**, **location**, **brief description (2 sentences)**
- **Verify it is still open** — check for "application period has closed" message. Discard if closed.
- Skip if already in `seen_jobs.json` or `job_search_tracker.csv`

Run fetches in parallel where possible (up to 7 at a time).

### Step 3: Hiring Probability Assessment

For each verified-open job, assess **realistic hiring probability** — not just skills match.

**Minimum threshold to list a role: Low-Medium probability.**

A role is Low-Medium or higher if:
- The mandate is generalist (policy, strategy, stakeholder engagement, program design) rather than domain specialist
- The candidate's transferable experience plausibly satisfies the core competencies
- The classification level is reachable (Manager or Director, not executive without relevant track record)
- The candidate has credible bridges into the sector (grants, awards, relationships)

A role is Low (do NOT list) if:
- It requires specialist domain knowledge the candidate lacks
- It's an Executive Director/C-suite in a specialist domain with no ecosystem connection
- Internal competition is near-certain and there's no obvious differentiator

**Fit labels reflect hiring probability, not skills match:**
- **High** = Strong realistic chance (clear pathway, skills map directly, domain fits)
- **Medium** = Plausible hire (skills transfer, some domain gap, but defensible application)
- **Low-Medium** = Worth applying but a stretch (one meaningful gap; requires strong framing)

### Step 4: Deduplicate & Store

Add all fetched jobs to `seen_jobs.json`:
```json
{
  "seen": {
    "<url_or_company_title_key>": {
      "title": "...",
      "company": "...",
      "url": "...",
      "first_seen": "YYYY-MM-DD",
      "fit": "high/medium/low-medium",
      "status": "new/skipped/evaluated"
    }
  }
}
```

### Step 5: Draft sweep to disk, THEN present

**MANDATORY — write the sweep to `working/active/job_sweep_{YYYY-MM-DD}.md` FIRST, before presenting in chat.** A chat-only shortlist is lost when the session ends. Write the doc, then summarize from it.

Doc structure:

```markdown
## New Job Matches — YYYY-MM-DD

Found X verified-open positions (Y high, Z medium, W low-medium).

| # | Fit | Title | Organization | Salary | Posted | Closes | URL |
|---|-----|-------|-------------|--------|--------|--------|-----|

### Highlights
For each High or Medium role, add 2-3 bullets:
- Why it matches the candidate's profile
- The bridge (grant relationships, ecosystem work, relevant experience)
- Any watch-out or gap to address in application
```

**Markdown table rule:** escape any literal pipe inside a header/cell — `P(hire|int)` → `P(hire\|int)` — or the column breaks.

After presenting, ask:
> "Want me to evaluate any of these in detail? Just give me the number(s)."

### Step 6: Update Tracker

If user decides to apply, add a row to `job_search_tracker.csv`.

---

## Important Rules

1. **Never fabricate postings.** Only present jobs found and verified via WebSearch/WebFetch.
2. **Verify open status.** Fetch every posting before including it. Discard anything showing "application period has closed."
3. **Minimum low-medium probability.** Do not list roles where there is no realistic path to hire.
4. **Parallel fetches.** Run up to 7 WebFetch calls simultaneously to stay efficient.
5. **Only open positions.** Skip expired deadlines. Flag roles closing within 48 hours as urgent.
6. **Respect deduplication.** Always check seen_jobs.json AND job_search_tracker.csv.
