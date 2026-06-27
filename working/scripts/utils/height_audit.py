"""Height-based overflow detector.

PURPOSE
-------
Character count is an imprecise proxy for box overflow because proportional fonts
render wide words wider regardless of char count. The reliable overflow check is
comparing actual rendered box heights across pairs of the same design.

A work-experience box that is taller than the minimum across all pairs with the same
bullet count = overflow (wrapping to an extra line somewhere).

Also audits skill description boxes (single-run short boxes in the right column).

USAGE
-----
1. After committing a new port, start a NEW transaction (to get updated heights).
2. Set SNAP to the new transaction snapshot file.
3. Set WORK_LABELS to match the title prefix of each work-experience box in your template.
4. Run: python working/scripts/utils/height_audit.py

OUTPUT
------
- Per work box: page, height, bullet count, chars, height-per-bullet.
- Reference section: min/max height per box type per bullet count — delta > 8 = suspected overflow.
- Skill desc audit: any short single-run box taller than ~40 units.

CALIBRATION
-----------
After your first few ports, you'll know the baseline height for each box type at
each bullet count. Update the comparison threshold in the "OVERFLOW SUSPECTED"
check below if your template differs from the 8-unit delta default.
"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── SET THESE ─────────────────────────────────────────────────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap

# Map box type names to the title prefix that identifies each type
# These must match the exact start of the text in each work-experience box
WORK_LABELS = {
    "Role1": "Your exact title for role 1",   # e.g. "CEO & Executive Director"
    "Role2": "Your exact title for role 2",   # e.g. "Chief Technology Officer"
    "Role3": "Your exact title for role 3",   # e.g. "Program Creator"
    "Role4": "Your exact title for role 4",   # e.g. "Research Scientist"
}

# How many pages to audit (0-indexed; set to cover all your dup pairs)
MAX_PAGE = 20  # adjust up if you have more pairs
# ──────────────────────────────────────────────────────────────────────────────

s = json.load(open(SNAP, encoding="utf-8"))[0]["text"]

obj = re.compile(
    r'"page_index":(\d+),"regions":\[(.*?)\],"containerElement":\{"type":"[^"]+","position":\{"top":([\d.]+),"left":([\d.]+)\},"dimension":\{"width":([\d.]+),"height":([\d.]+)\}\},"element_id":"([^"]+)"',
    re.DOTALL
)
tx = re.compile(r'"text":"((?:[^"\\]|\\.)*)"')

elements = []
for m in obj.finditer(s):
    pg   = int(m.group(1))
    top  = float(m.group(3))
    left = float(m.group(4))
    w    = float(m.group(5))
    h    = float(m.group(6))
    eid  = m.group(7)
    texts = []
    for t in tx.findall(m.group(2)):
        try: texts.append(json.loads('"' + t + '"'))
        except: texts.append(t)
    joined = "".join(texts)
    elements.append((pg, eid, top, left, w, h, joined))

print("=== WORK BOX HEIGHT AUDIT ===\n")
print(f"{'pg':>3} {'box':6} {'eid':50} {'h':>7} {'bullets':>7} {'chars':>6} {'h/bullet':>9}")

ref_heights = {}

for pg, eid, top, left, w, h, txt in sorted(elements, key=lambda x: (x[0], x[2])):
    if pg > MAX_PAGE: continue
    for bname, sig in WORK_LABELS.items():
        if txt.startswith(sig):
            idx = txt.find("\n\n")
            bullets_raw = txt[idx+2:] if idx >= 0 else txt
            bullets = [b for b in bullets_raw.split("\n") if b.strip()]
            n = len(bullets)
            h_per = h/n if n else h
            key = (bname, n)
            ref_heights.setdefault(key, []).append(h)
            print(f"{pg+1:>3} {bname:6} {eid[:50]:50} {h:>7.2f} {n:>7} {len(bullets_raw):>6} {h_per:>9.2f}")

print("\n=== REFERENCE HEIGHTS (same box type, same bullet count) ===")
for (bname, n), heights in sorted(ref_heights.items()):
    mn, mx = min(heights), max(heights)
    delta = mx - mn
    flag = "  <-- OVERFLOW SUSPECTED" if delta > 8 else ""
    print(f"  {bname} {n}b: min={mn:.1f} max={mx:.1f} delta={delta:.1f}{flag}")

print("\n=== SKILL DESC HEIGHT AUDIT ===")
print(f"{'pg':>3} {'eid':50} {'h':>7} {'chars':>6} {'note'}")
# Skill descs: single-run elements, ~100-215 chars, no newlines
# Adjust the left/width filters if your template layout differs
for pg, eid, top, left, w, h, txt in sorted(elements, key=lambda x: (x[0], x[2])):
    if pg > MAX_PAGE or pg % 2 == 1: continue  # cover pages only (even pages in 0-indexed)
    if 100 <= len(txt) <= 215 and "\n" not in txt and w > 150:
        note = "OK" if h <= 40 else f"OVERFLOW? h={h:.1f}"
        print(f"{pg+1:>3} {eid[:50]:50} {h:>7.2f} {len(txt):>6} {note}")
