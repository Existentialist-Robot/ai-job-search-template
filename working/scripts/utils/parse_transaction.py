"""Parse the truncated Canva transaction JSON to extract element map for pages in scope.

USAGE
-----
1. After `start-editing-transaction`, note the persisted snapshot file path Claude reports.
2. Set SNAP below to that path.
3. Run: python working/scripts/utils/parse_transaction.py
4. The output table shows: page, top, left, width, height, run_count, element_id, text preview.
   Use this to build your ID dict in the builder script.

NOTES
-----
- The transaction JSON is large and may be truncated near ~100 KB in the persisted file.
- This parser is tolerant of truncation — it uses regex per-element, not a full JSON parse.
- Run this FIRST after every start-editing-transaction to refresh your element IDs.
  Element IDs regenerate per duplicated page — never reuse IDs from a previous transaction.
"""
import re, json, sys

# ── SET THIS TO YOUR LATEST TRANSACTION SNAPSHOT FILE ──────────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap
# ────────────────────────────────────────────────────────────────────────────────

# ── optional: filter to specific pages (0-indexed in Canva API) ────────────────
TARGET_PAGES = None   # None = all pages; or set e.g. {0, 1} for pages 1-2

with open(SNAP, 'r', encoding='utf-8') as f:
    raw = f.read()

# Outer structure is [{type: text, text: "<escaped inner json>"}]
# Step 1: parse outer array (the outer JSON is complete even if inner is truncated)
try:
    outer = json.loads(raw)
    inner_str = outer[0]['text']
except Exception:
    # File truncated - extract text field manually
    m = re.search(r'"text":\s*"(.*)', raw, re.DOTALL)
    if not m:
        print("ERROR: can't find text field")
        sys.exit(1)
    escaped = m.group(1)
    inner_str = escaped.replace('\\"', '"')

# Step 2: extract transaction_id
tid_m = re.search(r'"transaction_id"\s*:\s*"([^"]+)"', inner_str)
print("transaction_id:", tid_m.group(1) if tid_m else "NOT FOUND")

# Step 3: find all richtext elements via regex (tolerant of truncation)
elem_pat = re.compile(
    r'\{"page_index":(\d+),"regions":\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\],'
    r'"containerElement":\{"type":"TEXT","position":\{"top":([\d.]+),"left":([\d.]+)\},'
    r'"dimension":\{"width":([\d.]+),"height":([\d.]+)\}\},"element_id":"([^"]+)"\}'
)

elements = []
for m in elem_pat.finditer(inner_str):
    page_idx = int(m.group(1))
    if TARGET_PAGES is not None and page_idx not in TARGET_PAGES:
        continue
    regions_raw = m.group(2)
    top = float(m.group(3))
    left = float(m.group(4))
    w = float(m.group(5))
    h = float(m.group(6))
    eid = m.group(7)
    texts = re.findall(r'"text":"((?:[^"\\]|\\.)*)"', regions_raw)
    run_count = len(texts)
    joined = ' | '.join(t[:40] for t in texts[:3])
    elements.append((page_idx, top, left, w, h, run_count, eid, joined))

print(f"\nTotal elements parsed: {len(elements)}\n")

print(f"{'P':2} {'top':5} {'left':5} {'w':5} {'h':5} {'runs':4}  {'element_id':45}  text")
print("-" * 120)
for (pid, top, left, w, h, run_count, eid, txt) in sorted(elements, key=lambda x: (x[0], x[1])):
    # Page index is 0-based in the API; display as 1-based (Canva page number)
    print(f"P{pid+1} {top:5.0f} {left:5.0f} {w:5.0f} {h:5.0f} {run_count:4d}  {eid:45}  {repr(txt)[:60]}")
