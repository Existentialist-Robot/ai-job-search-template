"""Extract full text of multi-run work-experience boxes from the Canva transaction JSON.

PURPOSE
-------
Before building a port, you need the exact current text of each work-experience box to use
as find-anchors in find_and_replace_text operations. This script extracts that text by
looking up each box by its element_id.

USAGE
-----
1. Set SNAP to your latest transaction snapshot file.
2. Set WORK_IDS to the element IDs of your 4 work-experience boxes
   (get these from parse_transaction.py — look for multi-run boxes with your role titles).
3. Run: python working/scripts/utils/read_work_boxes.py

OUTPUT
------
For each box: each text run, up to 10 runs (title run, bullets run, etc.).
The bullets run text is what you use as find_text in find_and_replace_text.
"""
import re, json

# ── SET THESE ─────────────────────────────────────────────────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap

# Map your box names to their element IDs from parse_transaction.py
WORK_IDS = [
    ('Role1',    'YOUR_ELEMENT_ID_FOR_ROLE_1'),   # e.g. your main/current role
    ('Role2',    'YOUR_ELEMENT_ID_FOR_ROLE_2'),
    ('Role3',    'YOUR_ELEMENT_ID_FOR_ROLE_3'),
    ('Role4',    'YOUR_ELEMENT_ID_FOR_ROLE_4'),
]
# ──────────────────────────────────────────────────────────────────────────────

with open(SNAP, 'r', encoding='utf-8') as f:
    raw = f.read()

outer = json.loads(raw)
inner_str = outer[0]['text']

for name, eid in WORK_IDS:
    idx = inner_str.find(eid)
    if idx == -1:
        print(f'NOT FOUND: {eid} ({name})')
        continue
    start = inner_str.rfind('{"page_index"', 0, idx)
    chunk = inner_str[start:start+3000]
    # Extract all "text": "..." values in this element
    texts = re.findall(r'"text":"((?:[^"\\]|\\.)*)"', chunk)
    print(f'=== {name} ({eid[:25]}...) ===')
    for i, t in enumerate(texts[:10]):
        t2 = t.replace('\\n', '\n').replace('\\"', '"')
        print(f'  run {i}: {repr(t2[:120])}')
    print()
