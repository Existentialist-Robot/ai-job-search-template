"""Get full (untruncated) bullet text from work-experience boxes.

PURPOSE
-------
read_work_boxes.py truncates text at ~120 chars per run. If a bullet block is longer
than that, use this script to get the full untruncated text via a starting-phrase anchor.
This is critical when building find_and_replace_text find_text anchors — the find_text
must match the full current text exactly (including any em-dashes, newlines, etc.).

USAGE
-----
1. Set SNAP to your latest transaction snapshot file.
2. Set START_PHRASES to a unique opening phrase for each box's bullet block.
   Each phrase should be unique enough to identify the box unambiguously.
3. Run: python working/scripts/utils/read_bullets_full.py

OUTPUT
------
For each box: full text of the bullet block, char count, and a JSON repr for copy-paste
into your find_text parameter.
"""
import re, json

# ── SET THESE ─────────────────────────────────────────────────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap

# Map box names to a unique starting phrase in their bullet text
# Choose a phrase that appears only in that one box
START_PHRASES = {
    'Role1-b1': "First few words of your first bullet in role 1",
    'Role2-b1': "First few words of your first bullet in role 2",
    'Role3-b1': "First few words of your first bullet in role 3",
    'Role4-b1': "First few words of your first bullet in role 4",
}
# ──────────────────────────────────────────────────────────────────────────────

with open(SNAP, 'r', encoding='utf-8') as f:
    raw = f.read()

outer = json.loads(raw)
inner_str = outer[0]['text']

for label, start_phrase in START_PHRASES.items():
    idx = inner_str.find(start_phrase)
    if idx == -1:
        print(f'NOT FOUND: {label}')
        continue
    # Go back to find the opening "text":"
    q_start = inner_str.rfind('"text":"', 0, idx)
    # Extract from after "text":"
    text_start = q_start + 8  # len('"text":"') = 8
    # Find end: unescaped "
    end = text_start
    while end < len(inner_str):
        c = inner_str[end]
        if c == '"':
            backslashes = 0
            i = end - 1
            while i >= text_start and inner_str[i] == '\\':
                backslashes += 1
                i -= 1
            if backslashes % 2 == 0:
                break
        end += 1
    full_text = inner_str[text_start:end].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
    print(f'=== {label} ===')
    print(repr(full_text[:900]))
    print(f'  CHARS: {len(full_text)}')
    print()
