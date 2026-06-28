"""
Overflow audit for pages 1-6.
Checks each CEO bullet and skill desc against EU-proven per-line targets.
Flags anything that likely causes a 1-line overhang.
"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SNAP = r"C:\Users\exist\.claude\projects\c--Users-exist-Documents-GitHub-ai-job-search\c5447b84-53c5-48b0-84f6-5b999cf5a62e\tool-results\toolu_01Na8TPrMTvm8AeCuofztjxA.json"
s = json.load(open(SNAP, encoding="utf-8"))[0]["text"]
obj = re.compile(r'"page_index":(\d+),"regions":\[(.*?)\],"containerElement":\{.*?"element_id":"([^"]+)"', re.DOTALL)
tx  = re.compile(r'"text":"((?:[^"\\]|\\.)*)"')
cur = {}
for m in obj.finditer(s):
    pg = int(m.group(1))
    if pg not in range(1, 7): continue
    texts = []
    for t in tx.findall(m.group(2)):
        try: texts.append(json.loads('"'+t+'"'))
        except: texts.append(t)
    cur[m.group(3)] = (pg, "".join(texts))

# CEO box element IDs by page
CEO_IDS = {
    1: "PBNtB5GtVWGvt33P-LBVG0jg2Hl6yVXsG",   # Communitech
    3: "PBhHJgQYsZBbPJ8y-LBwSwMjjNjXF4FV1",   # Platform Calgary
    5: "PB6stmpxGmLcY25V-LBNj95pzvvcwsDtb",   # Service Alberta
}

# EU per-bullet targets (from CLAUDE.md — hard ceiling per bullet)
B_TARGETS = [232, 178, 165, 150, 123]

# Skill desc caps by position (sk1D..sk4D) — same across all pairs
SK_CAPS = [170, 180, 175, 210]

# Skill desc IDs by page — collect from dump
SK_D_KEYWORDS = [
    "Policy & Strategic Advice", "Policy Analysis", "Ecosystem Development",
    "Partnership Development", "Prepared strategic briefings",
    "Synthesizes qualitative", "Built Alberta",
    "Stakeholder Networks", "Member Relations", "Policy Consultation",
    "Stakeholder Relations",
    "Innovation Ecosystems", "Community Programming", "Decision Materials",
    "Policy Intelligence", "Partner Strategy", "Legislative Research",
]

OVERFLOWS = []

print("=== CEO BULLET OVERFLOW AUDIT ===\n")
for pg, eid in CEO_IDS.items():
    if eid not in cur: print(f"P{pg} CEO: NOT IN SNAP"); continue
    _, full = cur[eid]
    idx = full.find("\n\n")
    bullets_raw = full[idx+2:] if idx >= 0 else full
    bullets = bullets_raw.split("\n")
    pair_name = {1:"Communitech",3:"Platform Calgary",5:"Service Alberta"}[pg]
    print(f"--- P{pg} {pair_name} ({len(bullets)} bullets, {len(full)} total) ---")
    for i, b in enumerate(bullets):
        cap = B_TARGETS[i] if i < len(B_TARGETS) else 123
        status = "OK" if len(b) <= cap else f"OVER +{len(b)-cap}"
        flag = " ⚠️" if len(b) > cap else ""
        print(f"  b{i+1} [{len(b):3}/{cap}] {status}{flag}")
        print(f"       {repr(b[:80])}")
        if len(b) > cap:
            OVERFLOWS.append((f"P{pg} CEO b{i+1}", eid, b, cap))

print("\n=== SKILL DESC OVERFLOW AUDIT ===\n")
# Find skill desc elements by their content keywords
sk_hits = []
for eid, (pg, txt) in cur.items():
    if pg not in (1, 3, 5): continue
    if len(txt) < 100 or len(txt) > 215: continue
    # skip work boxes, covers, profile
    if "\n" in txt or len(txt) > 215: continue
    # find element by text content pattern
    for kw in SK_D_KEYWORDS:
        pass  # just log all relevant-length single-line elements
    # Check if this could be a skill desc (100-215 chars, no newline)
    if 100 <= len(txt) <= 215:
        sk_hits.append((pg, eid, txt))

sk_hits.sort(key=lambda x: (x[0], len(x[2])))
# Group by page and sort by position (approximate)
for pg in (1, 3, 5):
    items = [(e,t) for p,e,t in sk_hits if p==pg]
    pair_name = {1:"Communitech",3:"Platform Calgary",5:"Service Alberta"}[pg]
    if items:
        print(f"--- P{pg} {pair_name} skill descs ---")
        for i, (eid, txt) in enumerate(items):
            # Can't know exact sk position without position data, estimate from length
            print(f"  [{len(txt):3}] {repr(txt[:75])}")

print(f"\n\n=== OVERFLOW SUMMARY ===")
if OVERFLOWS:
    print(f"{len(OVERFLOWS)} bullet(s) over per-line target:\n")
    for name, eid, b, cap in OVERFLOWS:
        excess = len(b) - cap
        print(f"  {name}: {len(b)} chars (cap {cap}, over by {excess})")
        print(f"    Full: {repr(b)}")
        print()
else:
    print("No CEO bullet overflows detected.")
