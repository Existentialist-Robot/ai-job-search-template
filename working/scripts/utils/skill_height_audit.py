"""
Skill desc height audit for pages 1, 3, 5.
Skill desc boxes are in the right column (left≈542) and should each be a single line (~34-36 units).
If a skill desc box is taller (~50+ units), it's wrapping to 2 lines and will crowd the layout.
"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SNAP = r"C:\Users\exist\.claude\projects\c--Users-exist-Documents-GitHub-ai-job-search\c5447b84-53c5-48b0-84f6-5b999cf5a62e\tool-results\toolu_01QnsEzZfiLcn1zjb4eWtkBZ.json"
s = json.load(open(SNAP, encoding="utf-8"))[0]["text"]

obj = re.compile(
    r'"page_index":(\d+),"regions":\[(.*?)\],"containerElement":\{"type":"[^"]+","position":\{"top":([\d.]+),"left":([\d.]+)\},"dimension":\{"width":([\d.]+),"height":([\d.]+)\}\},"element_id":"([^"]+)"',
    re.DOTALL
)
tx  = re.compile(r'"text":"((?:[^"\\]|\\.)*)"')

BASELINE_H = None  # will auto-detect from shortest single-line sk desc

rows = []
for m in obj.finditer(s):
    pg  = int(m.group(1))
    top = float(m.group(3))
    left= float(m.group(4))
    w   = float(m.group(5))
    h   = float(m.group(6))
    eid = m.group(7)
    if pg not in (1, 3, 5): continue
    texts = []
    for t in tx.findall(m.group(2)):
        try: texts.append(json.loads('"'+t+'"'))
        except: texts.append(t)
    joined = "".join(texts)
    # Skill descs: right column (left≈542), single-run (no \n), 100-210 chars, width≈200-250
    if left > 500 and w > 150 and 80 <= len(joined) <= 215 and "\n" not in joined:
        rows.append((pg, top, left, w, h, eid, joined))

if not rows:
    print("No skill desc elements found — check position filter")
    sys.exit()

# Detect baseline from shortest boxes
heights = [r[4] for r in rows]
baseline = min(heights)
print(f"Skill desc baseline height (clean 1-line): {baseline:.2f}")
print(f"Overflow threshold: >{baseline + 5:.2f}\n")

print(f"{'pg':>3} {'top':>7} {'h':>7} {'chars':>6}  {'status'}")
overflows = []
for pg, top, left, w, h, eid, txt in sorted(rows, key=lambda x: (x[0], x[2])):
    overflow = h > baseline + 5
    status = f"⚠️ OVERFLOW h={h:.1f}" if overflow else "OK"
    print(f"{pg:>3} {top:>7.1f} {h:>7.2f} {len(txt):>6}  {status}")
    print(f"     {eid[:55]:55}")
    print(f"     {repr(txt[:80])}")
    if overflow:
        overflows.append((pg, eid, h, len(txt), txt))

print(f"\n=== SUMMARY ===")
if overflows:
    print(f"{len(overflows)} skill desc(s) overflowing:\n")
    for pg, eid, h, n, txt in overflows:
        excess = h - baseline
        print(f"  P{pg} eid={eid}")
        print(f"  h={h:.2f} (+{excess:.1f}), {n} chars")
        print(f"  Text: {repr(txt[:90])}")
        # Suggest trim target
        # One line ≈ baseline height. If overflowing by ~15 units = 1 extra line
        # Estimate chars per line from non-overflowing elements
        ok_rows = [(r[5], r[4]) for r in rows if r[4] <= baseline + 2]
        if ok_rows:
            avg_chars = sum(len(r[6]) for r in rows if r[4] <= baseline + 2) / max(1, len(ok_rows))
            print(f"  Suggest trimming to ≈{int(avg_chars)} chars")
        print()
else:
    print("All skill descs fit in single line. ✅")
