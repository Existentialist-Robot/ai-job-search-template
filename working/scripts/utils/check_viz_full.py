"""
Full viz structural check — run after any changes to job_search_viz.html or build_job_viz.py.
Covers JS syntax, trace count, CSS architecture rules, slider wiring, and overflow guards.
This script is persistent — add checks here when new structural rules are established.
"""
import json, re, sys, subprocess, os
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
_ROOT = Path(__file__).resolve().parents[3]
HTML = str(_ROOT / "working" / "active" / "job_search_viz.html")
PY   = str(_ROOT / "working" / "scripts" / "viz" / "build_job_viz.py")

txt = open(HTML, encoding="utf-8").read()

if "Plotly.newPlot" not in txt:
    sys.path.insert(0, os.path.dirname(__file__))
    from check_viz_three import main as check_three_viz

    check_three_viz()
    sys.exit(0)

PASS, FAIL = [], []

def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
    else:
        FAIL.append(f"{name}" + (f": {detail}" if detail else ""))

# ── JS syntax (write to temp file — avoids Windows path-too-long on -e flag) ──
import tempfile
try:
    scripts = "".join(re.findall(r'<script[^>]*>(.*?)</script>', txt, re.DOTALL))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as tf:
        tf.write(scripts); tmppath = tf.name
    node_result = subprocess.run(["node", "--check", tmppath],
        capture_output=True, text=True, timeout=10)
    os.unlink(tmppath)
    check("JS syntax", node_result.returncode == 0, node_result.stderr[:100] if node_result.returncode else "")
except Exception as e:
    check("JS syntax", False, str(e))

# ── 7 traces ────────────────────────────────────────────────────────────────────
trace_match = re.search(r'var data\s*=\s*(\[.*?\]);', txt, re.DOTALL)
if trace_match:
    try:
        # Quick count: number of "type":"scatter3d" entries
        n_traces = len(re.findall(r'"type"\s*:\s*"scatter3d"', trace_match.group(1)))
        check("7 traces", n_traces == 7, f"found {n_traces}")
    except:
        check("7 traces", False, "parse error")
else:
    check("7 traces", False, "data array not found")

# ── no height in Plotly layout ──────────────────────────────────────────────────
check("no height in layout", '"height": 660' not in txt and '"height":660' not in txt,
      "height:660 found — breaks responsive sizing and rotate")

# ── no overflow:hidden on #viz ──────────────────────────────────────────────────
viz_css = re.search(r'#viz\s*\{([^}]+)\}', txt)
if viz_css:
    check("no overflow:hidden on #viz", "overflow:hidden" not in viz_css.group(1),
          "blocks Plotly wheel events for scroll-zoom")
else:
    check("no overflow:hidden on #viz", "overflow:hidden" not in txt.split("#viz")[1][:150]
          if "#viz" in txt else True)

# ── sidebar layout (not overlay-based) ─────────────────────────────────────────
check("sidebar layout present", 'id="sidebar"' in txt,
      "sidebar layout required to prevent controls overlaying chart")
check("no .sec-body rule", ".sec-body {" not in txt,
      "sec-body absolute panels cause phantom overlays")
check("timeline not position:fixed",
      "timeline-wrap" in txt and "position:fixed" not in txt.split("timeline-wrap")[1][:300],
      "fixed timeline conflicts with Plotly event surface")

# ── modal safety ────────────────────────────────────────────────────────────────
check("backdrop visible (not transparent)",
      "rgba(0,0,0,0.4)" in txt or "rgba(0,0,0,.4)" in txt,
      "transparent backdrop gets stuck and blocks all clicks")
check("escape key closes modal", "Escape" in txt)
check("modal backdrop present", 'id="modal-backdrop"' in txt)

# ── slider wiring ────────────────────────────────────────────────────────────────
check("sphere sliders wired", all(f'id="{s}"' in txt for s in ["sx","sy","sz","sr","ss"]),
      "sphere slider IDs missing")
check("updateSphere oninput", 'oninput="updateSphere()' in txt or "updateSphere()" in txt)
check("VIZ_READY guard", "VIZ_READY" in txt,
      "async init race: restyle calls before newPlot completes silently no-op")

# ── fitViz present ──────────────────────────────────────────────────────────────
check("fitViz present", "fitVizToContainer" in txt or "fitViz" in txt,
      "without resize call, chart may not fill flex container correctly")

# ── CEO bullet overflow guard (per-line targets documented) ────────────────────
check("PORTING_RECIPE overflow section",
      os.path.exists(str(_ROOT / "working" / "scripts" / "PORTING_RECIPE.md")) and
      "height_audit" in open(str(_ROOT / "working" / "scripts" / "PORTING_RECIPE.md"), encoding="utf-8").read(),
      "PORTING_RECIPE.md missing height-based overflow detection section")

check("height_audit.py present",
      os.path.exists(str(_ROOT / "working" / "scripts" / "utils" / "height_audit.py")))

# ── Python generator sync ───────────────────────────────────────────────────────
if os.path.exists(PY):
    py_txt = open(PY, encoding="utf-8").read()
    check("generator has no height:660", "height=660" not in py_txt,
          "generator still has height=660 — regeneration will reintroduce the bug")
    check("generator has VIZ_READY", "VIZ_READY" in py_txt,
          "generator missing async init guard — will be lost on next regeneration")
    check("generator has fitViz", "fitViz" in py_txt)
else:
    FAIL.append("build_job_viz.py not found")

# ── Ported entries: check JOBS_DATA not STATUS_MAP color definition ────────────
# Match "status": "Ported" in JOBS_DATA JSON (not STATUS_MAP colour mapping)
ported_in_jobs = len(re.findall(r'"status":\s*"Ported"', txt))
check("no stale Ported entries in JOBS_DATA",
      ported_in_jobs == 0,
      f"{ported_in_jobs} Ported entries in JOBS_DATA — update to Applied after export")

# ── Report ──────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"FULL VIZ CHECK  ({len(PASS)} pass, {len(FAIL)} fail)")
print(f"{'='*60}")
for p in PASS:
    print(f"  ✅  {p}")
for f in FAIL:
    print(f"  ❌  {f}")

if FAIL:
    print(f"\n{len(FAIL)} issue(s) found — fix before export or deploy")
    sys.exit(1)
else:
    print(f"\nAll checks passed. Viz is clean.")
