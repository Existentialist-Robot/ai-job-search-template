# -*- coding: utf-8 -*-
"""
EXAMPLE BUILDER SCRIPT — clone this for every new role you port.

HOW TO USE THIS FILE
--------------------
1. Do `start-editing-transaction` in Canva MCP → note the persisted snapshot path.
2. Copy this file to builders/build_<role>_pair<k>.py.
3. Update SNAP to the new snapshot path.
4. Update PAGE to the pair you're porting (1-indexed Canva page numbers).
5. Run parse_transaction.py to get fresh element IDs for this pair.
6. Update ID with those element IDs.
7. Update CURRENT_BULLETS with the actual current text of each work-experience box
   (use read_work_boxes.py or read_bullets_full.py to get the exact strings).
8. Update SINGLE and NEW_BULLETS with your role-targeted copy.
9. Run this script: python working/scripts/builders/build_<role>_pair<k>.py
   — check output for OVER! warnings and fix before proceeding.
10. perform-editing-operations using the generated JSON.
11. format_text {font_style: normal} on all work boxes to clear italic first bullet.
12. commit-editing-transaction.
13. height_audit.py to check for overflow.

PORTING RULES (do not skip)
----------------------------
- Single-run boxes (headline, tagline, profile, skill labels, skill descs, cover):
  use replace_text.
- Multi-run boxes (work experience — bold title + bullets):
  use find_and_replace_text on the BULLETS BLOCK ONLY (everything after the title line).
  Never whole-replace a multi-run box — it flattens the bold title and italicizes bullets.
- Length-match every box: new text must be <= the CAP. OVER! = must trim.
- Cover letter: aim 3,050–3,300 chars. Under 2,700 reads "light." Over 3,400 = overflow risk.
- After commit: run height_audit.py. Any work box taller than the shortest same-type box = overflow.
"""
import json, os

# ── STEP 1: SET SNAP TO YOUR LATEST TRANSACTION SNAPSHOT ─────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap

# ── STEP 2: SET PAGE NUMBER (1-indexed) ───────────────────────────────────────
RESUME_PAGE = 1   # e.g. 1 for pair 1, 3 for pair 2, etc.
COVER_PAGE  = 2   # always RESUME_PAGE + 1

# ── STEP 3: ELEMENT IDs (from parse_transaction.py) ──────────────────────────
# Run parse_transaction.py with SNAP set above, then copy the element_ids here.
# Element IDs regenerate every time you duplicate a pair — always refresh.
ID = {
    "head1":   "PASTE_RESUME_HEADLINE_ELEMENT_ID",
    "head2":   "PASTE_COVER_HEADLINE_ELEMENT_ID",
    "tagline": "PASTE_TAGLINE_ELEMENT_ID",
    "profile": "PASTE_PROFILE_ELEMENT_ID",
    "divider": "PASTE_DIVIDER_ELEMENT_ID",
    # Work experience boxes (multi-run — bold title + bullets)
    "ROLE1":   "PASTE_ROLE1_ELEMENT_ID",   # your main/most recent role
    "ROLE2":   "PASTE_ROLE2_ELEMENT_ID",
    "ROLE3":   "PASTE_ROLE3_ELEMENT_ID",
    "ROLE4":   "PASTE_ROLE4_ELEMENT_ID",
    # Skill labels (single-run)
    "sk1L":    "PASTE_SKILL_LABEL_1_ID",
    "sk2L":    "PASTE_SKILL_LABEL_2_ID",
    "sk3L":    "PASTE_SKILL_LABEL_3_ID",
    "sk4L":    "PASTE_SKILL_LABEL_4_ID",
    # Skill descriptions (single-run)
    "sk1D":    "PASTE_SKILL_DESC_1_ID",
    "sk2D":    "PASTE_SKILL_DESC_2_ID",
    "sk3D":    "PASTE_SKILL_DESC_3_ID",
    "sk4D":    "PASTE_SKILL_DESC_4_ID",
    # Cover letter (single large box on the cover page)
    "cover":   "PASTE_COVER_LETTER_ELEMENT_ID",
}

# ── STEP 4: CHARACTER CAPACITY PER BOX ────────────────────────────────────────
# Use your calibrated targets from CLAUDE.md.
# These are estimates until you've done 2 real ports and updated CLAUDE.md.
CAP = {
    "head1":   51,
    "head2":   51,
    "tagline": 40,
    "profile": 719,
    "divider": 31,
    "ROLE1":   967,   # 5 bullets
    "ROLE2":   386,   # 2 bullets
    "ROLE3":   403,   # 2 bullets
    "ROLE4":   480,   # 2 bullets
    "sk1L":    29,
    "sk2L":    21,
    "sk3L":    23,
    "sk4L":    20,
    "sk1D":    170,
    "sk2D":    175,
    "sk3D":    175,
    "sk4D":    210,
    "cover":   3387,  # aim 3050–3300 in practice
}

# ── STEP 5: CURRENT BULLETS (find-anchors for find_and_replace_text) ──────────
# Get these from read_work_boxes.py or read_bullets_full.py.
# Must be the EXACT current text of the bullets block (everything after the title line).
# Use read_bullets_unicode.py if you have em-dashes or other non-ASCII characters.
CURRENT = {
    "ROLE1": "Paste exact current bullet text for Role 1 here.\nSecond bullet here.\nThird bullet.\nFourth bullet.\nFifth bullet.",
    "ROLE2": "Paste exact current bullet text for Role 2 here.\nSecond bullet here.",
    "ROLE3": "Paste exact current bullet text for Role 3 here.\nSecond bullet here.",
    "ROLE4": "Paste exact current bullet text for Role 4 here.\nSecond bullet here.",
}

# ── STEP 6: NEW COPY — ROLE TARGETED ─────────────────────────────────────────
# Replace with your role-targeted content. Length-match to CAP before running.

SINGLE = {
    "head1":   "Your Role-Targeted Headline Here",           # <= CAP["head1"]
    "head2":   "Your Role-Targeted Headline Here",           # same as head1
    "tagline": "Your Tagline Here",                          # <= CAP["tagline"]
    "divider": "Your Divider Phrase",                        # <= CAP["divider"]

    "profile": (
        "Your role-targeted profile paragraph goes here. This should be 3–5 sentences "
        "that connect your strongest experience to the target role's key requirements. "
        "Be specific and use concrete numbers. Aim for ~700 characters. "
        "This is the first thing a screener reads — make it count."
    ),  # <= CAP["profile"]

    "sk1L":  "Skill Label 1",   # e.g. "Program Design"
    "sk2L":  "Skill Label 2",   # e.g. "Stakeholder Engagement"
    "sk3L":  "Skill Label 3",   # e.g. "Technical Leadership"
    "sk4L":  "Skill Label 4",   # e.g. "Data & Analytics"

    "sk1D":  "2–3 sentence description of your first skill area.",    # <= CAP["sk1D"]
    "sk2D":  "2–3 sentence description of your second skill area.",   # <= CAP["sk2D"]
    "sk3D":  "2–3 sentence description of your third skill area.",    # <= CAP["sk3D"]
    "sk4D":  "2–3 sentence description of your fourth skill area.",   # <= CAP["sk4D"]

    "cover": (
        "Dear [Hiring Manager Name / Hiring Committee],\n\n"
        "[Opening paragraph — why you're applying and what you bring. 2–3 sentences.]\n\n"
        "[Body paragraph 1 — your most relevant experience, with specific examples and metrics.]\n\n"
        "[Body paragraph 2 — a second proof point; how you'd approach this role.]\n\n"
        "[Closing paragraph — genuine enthusiasm for this org/role, call to action.]\n\n"
        "Sincerely,\n[YOUR_NAME]"
    ),  # aim 3050–3300 chars total
}

NEW_BULLETS = {
    "ROLE1": [
        "First bullet for Role 1 — lead with the most impressive achievement.",
        "Second bullet — program or project delivery proof point.",
        "Third bullet — stakeholder/partnership achievement.",
        "Fourth bullet — quantified metric or scale.",
        "Fifth bullet — complementary capability relevant to target role.",
    ],
    "ROLE2": [
        "First bullet for Role 2.",
        "Second bullet for Role 2.",
    ],
    "ROLE3": [
        "First bullet for Role 3.",
        "Second bullet for Role 3.",
    ],
    "ROLE4": [
        "First bullet for Role 4.",
        "Second bullet for Role 4.",
    ],
}

# ── BUILD OPS ─────────────────────────────────────────────────────────────────
ops = []
all_ids_found = True

print(f"\n{'BOX':10} {'cap':>5} {'new':>5}  status")
print("-" * 40)

# Single-run boxes → replace_text
for k in ("head1", "head2", "tagline", "profile", "divider",
          "sk1L", "sk2L", "sk3L", "sk4L",
          "sk1D", "sk2D", "sk3D", "sk4D",
          "cover"):
    if not ID.get(k) or "PASTE_" in ID.get(k, ""):
        print(f"{k:10} {'':>5} {'':>5}  SKIPPED (no ID)")
        all_ids_found = False
        continue
    t = SINGLE[k]
    over = " OVER!" if len(t) > CAP[k] else ""
    print(f"{k:10} {CAP[k]:>5} {len(t):>5}  {'OK' if not over else 'OVER!'}")
    ops.append({"type": "replace_text", "element_id": ID[k], "text": t})

# Multi-run boxes → find_and_replace_text on bullets block only
for k in ("ROLE1", "ROLE2", "ROLE3", "ROLE4"):
    if not ID.get(k) or "PASTE_" in ID.get(k, ""):
        print(f"{k:10} {'':>5} {'':>5}  SKIPPED (no ID)")
        all_ids_found = False
        continue
    nb = "\n".join(NEW_BULLETS[k])
    over = " OVER!" if len(nb) > CAP[k] else ""
    print(f"{k:10} {CAP[k]:>5} {len(nb):>5}  {'OK' if not over else 'OVER!'}")
    ops.append({
        "type": "find_and_replace_text",
        "element_id": ID[k],
        "find_text": CURRENT[k],
        "replace_text": nb,
    })

print()
if all_ids_found:
    print("CLEAN-MAP CHECK: PASS")
else:
    print("CLEAN-MAP CHECK: FAIL — fix missing IDs before porting")

# Write ops JSON
slug = "example_role"  # change this to your role slug
out_dir = os.path.join(os.path.dirname(__file__), "..", "generated")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, f"{slug}_pair{RESUME_PAGE//2 + 1}_ops.json")
json.dump(ops, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nWrote {len(ops)} ops to {out_path}")
print("Next: perform-editing-operations → format_text (italic fix) → commit-editing-transaction → height_audit.py")
