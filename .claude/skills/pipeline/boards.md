# Confirmed Queryable Job Boards

All boards below have been verified as returning plain HTML — no JS rendering, no headless browser required. Queryable via WebFetch directly.

Last verified: 2025

---

## Board Registry

| # | Board | Base URL | Search URL Pattern | Sector Focus | Notes |
|---|-------|----------|--------------------|--------------|-------|
| 1 | **GoA Alberta** | jobpostings.alberta.ca | `https://jobpostings.alberta.ca/search/?q={keywords}&l={location}&startrow=0` | Provincial government, APS | Edmonton-centric; full HTML pagination |
| 2 | **Charity Village** | charityvillage.com | `https://www.charityvillage.com/jobs/?q={keywords}&l={location}` | Nonprofit, charity, social sector | 1,400+ active jobs; structured data including salary + close dates |
| 3 | **Work In Nonprofits** | workinnonprofits.ca | `https://workinnonprofits.ca/jobs/list-by/region/{region_id}` | Regional nonprofit | Limited filtering but clean HTML |
| 4 | **MINJobs** | municipalinfonet.com | `https://municipalinfonet.com/jobs?q={keywords}&province={province}` | Municipal government | Sortable; good for regional director roles |
| 5 | **GoodWork** | goodwork.ca | `https://www.goodwork.ca/jobs.php?prov={prov}&q={keywords}&type=full` | Green economy, nonprofits, social enterprise | Mix of nonprofit + mission-driven private |
| 6 | **Search-first: Tech/Startup ATS** | Google → Greenhouse/Ashby/Lever | `WebSearch: "{keywords}" site:boards.greenhouse.io OR site:jobs.ashbyhq.com Alberta Canada {year}` → WebFetch individual results | Tech, startup, scaleup, industry | Individual ATS pages ARE fetchable (HTML); only aggregate hubs block. |
| 7 | **Search-first: Corporate/Industry** | Google → company career pages | `WebSearch: "director" OR "VP" partnerships strategy innovation {province} Canada {year} careers -site:linkedin.com -site:glassdoor.com` → WebFetch individual results | Corporate, mid-market, tech-adjacent industry | Surfaces company career pages not on ATS platforms. |
| 8 | **Eluta.ca** | eluta.ca | `https://www.eluta.ca/search?q={keywords}&l={location}` | Aggregator — government, post-secondary, corporate | Aggregates from employer sites; SPL links expire fast, use category pages |
| 9 | **BC Public Service** | bcpublicservice.hua.hrsmart.com | `https://bcpublicservice.hua.hrsmart.com/hr/ats/JobSearch/search` | BC provincial government | Relevant for remote-eligible or relocation roles |
| 10 | **ReachHire** | reachhire.ca | `https://reachhire.ca/jobs/?search={keywords}&location={location}` | Alberta nonprofit sector | Powered by Careerleaf |
| 11 | **GC Jobs — individual poster pages** | emploisfp-psjobs.cfp-psc.gc.ca | `https://emploisfp-psjobs.cfp-psc.gc.ca/psrs-srfp/applicant/page1800?poster={POSTER_ID}` | Federal government | Individual posting pages are plain HTML. **Cannot search directly** — search portal is JS-gated. Workflow: WebSearch to surface poster IDs, then WebFetch each page. |

---

## Search Keywords by Sector

### Government & Quasi-Governmental
```
director innovation, manager innovation partnerships, director economic development,
director post-secondary, director strategy, executive director programs,
senior advisor policy, manager ecosystem development, director industry relations
```

### Innovation Ecosystem
```
director entrepreneurship, program director innovation, ecosystem manager,
director partnerships, venture development, incubator director,
director community engagement innovation
```

### Non-Profit / Workforce
```
executive director programs, director community programs, manager innovation programs,
director workforce development, director industry engagement
```

### Post-Secondary
```
director industry liaison, director innovation partnerships, director technology transfer,
director enterprise, director research partnerships, director entrepreneurship
```

---

## Query Strategy

Run 2–3 keyword variations per board per sweep. Prioritize your highest-signal boards first. Per sweep: **4–6 WebFetch calls** (rule from CLAUDE.md / Search Execution). Don't fan out to all boards in one call — do 2 waves of 5 if doing a broad sweep.

---

## Secondary Sources (org-specific — check as supplemental only)

| Board | URL | Notes |
|-------|-----|-------|
| [Your target org 1] | `[career page URL]` | Check weekly |
| [Your target org 2] | `[career page URL]` | Check weekly |
| Alberta Innovates | `careers.albertainnovates.ca/go/Opportunities-at-Alberta-Innovates/2571817/` | Direct AI careers page |

---

## Free API Access — Register for These

| API | Register | Coverage | Free Tier | Best For |
|-----|----------|----------|-----------|---------|
| **Adzuna** | [developer.adzuna.com](https://developer.adzuna.com) | 26,000+ Canadian jobs; 12 countries | Free tier (~250 calls/day) | Best Canadian aggregator; salary data; searchable by city/province. MCP server: `github.com/folathecoder/adzuna-job-search-mcp` |
| **Jooble** | [jooble.org/api/about](https://jooble.org/api/about) | 70+ countries incl. Canada; aggregates Job Bank | Free key on request | Returns title, company, location, salary, description, posting date, source URL in JSON |

---

## WebSearch as a Discovery Layer

**Use WebSearch** — it's Google's indexed cache of JS-rendered pages that WebFetch cannot reach:

1. `WebSearch: site:boards.greenhouse.io "director" {province} {year}` → surfaces individual ATS pages
2. `WebSearch: site:emploisfp-psjobs.cfp-psc.gc.ca {city} "advisor" {year}` → surfaces current GC Jobs poster IDs
3. WebFetch the individual URL → full job details

**Cadence:** Government portals post in waves (often bi-weekly). Sweep every 5–7 days or roles close before you see them.

---

## Known Failures (do not retry without testing first)

| Board | Status | Reason |
|-------|--------|--------|
| jobbank.gc.ca search | ❌ JS-rendered | Returns 0 results; requires session-aware POST with ViewState tokens |
| ca.indeed.com search | ❌ 403 Blocked | Cloudflare protection on direct fetches |
| workopolis.com | ❌ 403 Forbidden | Bot protection |
| idealist.org | ❌ JS-rendered | No job data without JS |
| lever.co | ❌ 403 Forbidden | Blocks scraping |
