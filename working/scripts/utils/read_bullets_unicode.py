"""Get exact Unicode codepoints for bullet text.

PURPOSE
-------
Critical when bullets contain em-dashes (—, U+2014), curly quotes, or other non-ASCII
characters that must match exactly in find_text. If your find_and_replace_text op is
silently failing (no error but box not updated), it's usually because the find_text
contains a character that looks identical on screen but has a different codepoint in
the actual Canva data. This script shows you the exact bytes.

USAGE
-----
1. Set SNAP to your latest transaction snapshot file.
2. Set BOXES with starting phrases for each box you want to inspect.
3. Run: python working/scripts/utils/read_bullets_unicode.py

OUTPUT
------
Per box: each line's char count, repr, and any non-ASCII characters with their codepoints.
Also outputs the full JSON repr suitable for copy-paste into find_text.
"""
import re, json

# ── SET THESE ─────────────────────────────────────────────────────────────────
SNAP = r"path/to/your/transaction/snap.json"  # set this to your latest transaction snap

BOXES = [
    ('Role1', "First few words of your first bullet in role 1"),
    ('Role2', "First few words of your first bullet in role 2"),
    ('Role3', "First few words of your first bullet in role 3"),
    ('Role4', "First few words of your first bullet in role 4"),
]
# ──────────────────────────────────────────────────────────────────────────────

with open(SNAP, 'r', encoding='utf-8') as f:
    raw = f.read()

outer = json.loads(raw)
inner_str = outer[0]['text']

for name, start_phrase in BOXES:
    idx = inner_str.find(start_phrase)
    if idx == -1:
        print(f'NOT FOUND: {name}')
        continue
    q_start = inner_str.rfind('"text":"', 0, idx)
    text_start = q_start + 8
    end = text_start
    while end < len(inner_str):
        c = inner_str[end]
        if c == '"':
            bs = 0
            i = end - 1
            while i >= text_start and inner_str[i] == '\\':
                bs += 1
                i -= 1
            if bs % 2 == 0:
                break
        end += 1

    escaped = inner_str[text_start:end]
    try:
        decoded = json.loads('"' + escaped + '"')
    except Exception:
        decoded = escaped.replace('\\n', '\n').replace('\\"', '"')

    print(f'=== {name} ===')
    lines = decoded.split('\n')
    for i, line in enumerate(lines):
        non_ascii = [(j, c, hex(ord(c))) for j, c in enumerate(line) if ord(c) > 127]
        print(f'  b{i+1} ({len(line)} chars): {repr(line[:120])}')
        if non_ascii:
            print(f'       non-ASCII: {non_ascii[:5]}')
    print(f'  TOTAL: {len(decoded)} chars')
    print(f'  JSON repr: {json.dumps(decoded)[:200]}')
    print()
