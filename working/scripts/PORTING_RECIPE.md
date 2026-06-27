# Canva Porting Toolkit (reusable — don't re-derive)

The résumé/cover template is identical across every dup pair. **Element IDs regenerate per duplicated page** (the one thing that changes), so a quick parse is always needed — but the layout, mapping, and recipe below never change.

## Fast path (per pair)
1. `start-editing-transaction` → note the persisted snapshot file path + transaction_id.
2. Copy closest builder from `builders/` → `builders/build_<role>_pair<k>.py`. Change: `SNAP` path, page numbers, `ID` dict (from parse_transaction.py), `CURRENT` dict (from read_work_boxes.py / read_bullets_full.py), and role copy (`SINGLE` dict + `NEW_BULLETS` dict + `cover`).
3. Run it → prints per-box char counts + `CLEAN MAP: PASS` + writes `generated/<role>_ops.json`.
4. `perform-editing-operations` immediately after `start-editing-transaction` (transactions expire — don't let them sit).
5. `format_text {font_style: normal}` on each work-experience box — clears baked italic first bullet.
6. Check response: title runs intact (bold preserved), no obvious overflow.
7. `commit-editing-transaction` — **changes are lost if not committed**.

## Stable template layout (logical box → how to find it)
- **headline** (×2, resume+cover): your positioning title (top of page).
- **tagline**: short phrase below headline.
- **profile**: the wide summary paragraph.
- **divider**: the standalone section-break phrase.
- **work boxes** (Role1/Role2/Role3/Role4): match by title prefix (your exact title text). Each = bold title-run + date/org-run + **italic first-bullet run** + normal-rest run.
- **skill labels/descriptions**: 4 skill areas with label + description paragraph.
- **cover**: the big box on the even page.

## Rules (why it ports clean)
- Boxes are absolutely positioned → **overflow is the only failure**. Keep every box **≤ current length**; under is safe.
- **Single-run boxes** → whole-box `replace_text`.
- **Work boxes** → `find_and_replace_text` on the **bullets-block only** (everything after the first `\n\n`), preserving the bold title; then **`format_text {font_style: normal}`** to clear the baked italic first bullet (verify the title stays its own run).
- Never set italic. Length-match by character count; expect a 1-line trim pass.

## Overflow detection (MANDATORY — always run after commit)
Character count is an imprecise proxy because proportional fonts render wide words wider regardless of char count. The only reliable overflow check is **box height comparison**:

1. After committing, start a new transaction and run `working/scripts/utils/height_audit.py`.
2. Compare work box heights across pairs. The **shortest clean box height is the baseline**.
3. Any box taller than baseline by ≥ 5 units = overflow. Trim the longest bullets until heights match.
4. **Per-bullet rule:** matching the *box total* to ceiling is not sufficient — a single over-long bullet wraps to an extra line and overflows even when the box total is under. Match each bullet to its proven-good equivalent length (or shorter), not just the box total.
5. Wide-word text (long words like "government", "post-secondary", "institutional") renders wider than char count — aim 10–15 chars UNDER the limit when using wide-word-heavy text.
6. Skill descs: check `height` in the response — any skill desc taller than ~40 units is overflowing.

## Files

### Utilities (`utils/`) — general-purpose, reuse every port
| Script | Purpose |
|--------|---------|
| `parse_transaction.py` | Parse a truncated Canva transaction JSON. Extracts element IDs, positions, dimensions, run counts, and text for all pages or a target page range. Run this first after `start-editing-transaction` to build the element map. |
| `read_work_boxes.py` | Read current text from the multi-run work boxes using element_id lookup. Run before building a port to get the current text for find-anchors. |
| `read_bullets_full.py` | Get the full untruncated bullet block for a work box (when `read_work_boxes.py` truncates at ~120 chars). Pass a unique starting phrase; extracts the whole text value. |
| `read_bullets_unicode.py` | Get exact Unicode codepoints for bullet text — critical when bullets contain em-dashes (—) or other special chars that must match exactly in `find_text`. |
| `height_audit.py` | Compare box heights across pairs to detect overflow. Run after every commit. |

### Builders (`builders/`) — clone one, swap copy, run
| Script | Best for |
|--------|---------|
| `build_EXAMPLE_pair1.py` | **Start here.** Fully commented template — copy and fill in your role copy. |

**Cloning a new role:** copy the closest builder → change `SNAP` path (new transaction file) → update page numbers → run `parse_transaction.py` to refresh `ID` → run `read_work_boxes.py` to refresh `CURRENT` → swap `SINGLE` copy + `NEW_BULLETS` → run → check `CLEAN MAP: PASS` + bound warnings → apply ops.

### Generated (`generated/`)
Builder scripts write ops JSON here. Each file is named `<role_slug>_pair<k>_ops.json`. These are ephemeral — commit them if you want a record, but they're always rebuildable from the builder script.

### Viz (`viz/`)
- `build_job_viz.py` — generates `working/active/job_search_viz.html`: 3D job search pipeline visualization

## Export & filing convention

Export each application as **separate résumé + cover PDFs** (portals usually want them apart), **PRO** quality.

- **Export call:** `export-design` → `{type:"pdf", size:"letter", export_quality:"pro", pages:[N]}`, one page per call (résumé = first page of the pair, cover = second). The `pages` param exports a single page and skips hidden/stale pages. Each call returns a download URL; fetch with PowerShell `Invoke-WebRequest` (not Bash — spaces/parentheses in paths cause failures).
- **Re-export whenever Canva changes** — URLs reflect a point-in-time render.

**Folder structure** (under `working/exports/`):
```
working/exports/
└── <YYYY-MM (Mon 'YY)>/                      ← monthly only. e.g. "2025-06 (Jun '25)"
    └── <YY-MM-DD - Company - Role>/          ← per application; date-FIRST so it auto-sorts
          ├── [YOUR_NAME]_Resume.pdf
          ├── [YOUR_NAME]_Cover_Letter.pdf
          └── copy/
              ├── packet_<slug>_<date>.md      ← draft packet (written here at draft time)
              └── review_agents_<date>.md      ← reviewer agent findings
```
- Month folder: `YYYY-MM (Mon 'YY)`. App folder: `YY-MM-DD - <Company> - <Role>`. Date = export/submit date.
- **`working/exports/` is the finals archive — the source of truth for every submitted application.**
- **File working docs WITH the application.** A doc that maps 1:1 to one application (draft, interview prep) goes in that app's folder. Only **multi-app sprint notes and intermediate pair-reviews** stay in `working/archive/`.
- **`working/active/` holds live work only** — the current interview doc, plus (optionally) one current sweep doc. Everything else is filed.
