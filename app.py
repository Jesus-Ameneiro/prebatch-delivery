import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
import json
import copy
import re
import urllib.request
import urllib.error
import urllib.parse
from io import BytesIO
from pathlib import Path
from datetime import datetime, date
import calendar

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Prebatch Generator — Ruvixx",
    page_icon="🔶",
    layout="wide",
)

# ──────────────────────────────────────────────
# Load Assets
# ──────────────────────────────────────────────
LOGO_B64 = ""
logo_path = Path(__file__).parent / "logo.png"
if logo_path.exists():
    LOGO_B64 = base64.b64encode(logo_path.read_bytes()).decode()

DOC_B64 = ""
doc_pdf_path = Path(__file__).parent / "DOCUMENTATION.pdf"
if doc_pdf_path.exists():
    DOC_B64 = base64.b64encode(doc_pdf_path.read_bytes()).decode()

# ──────────────────────────────────────────────
# CSS / Branding
# ──────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --rx-orange: #F47920; --rx-orange-dark: #D4611A;
        --rx-black: #1A1A1A;  --rx-dark-gray: #2D2D2D; --rx-mid-gray: #4A4A4A;
        --rx-blue: #1E6FBF;   --rx-blue-dark: #155A9C;
    }
    header[data-testid="stHeader"] {
        background-color: var(--rx-black) !important;
        border-bottom: 3px solid var(--rx-orange) !important;
    }
    [data-testid="stActionButton"],
    [data-testid="stToolbarActionButton"][aria-label="Edit source"],
    header a[href*="github"], [data-testid="stAppDeployButton"],
    [data-testid="stSourceButton"] { display: none !important; }
    header button[title="Favorite"], header button[title="Star"],
    header button[title="Edit"], header button[title="Edit source"],
    header button[title="Fork this app"],
    header a[title*="GitHub"], header a[title*="github"],
    header a[title="View app source"] { display: none !important; }
    button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background-color: var(--rx-orange) !important; border-color: var(--rx-orange) !important;
        color: white !important; font-weight: 600 !important;
    }
    button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
        background-color: var(--rx-orange-dark) !important; border-color: var(--rx-orange-dark) !important;
    }
    section[data-testid="stSidebar"] { background-color: var(--rx-black) !important; }
    section[data-testid="stSidebar"] * { color: #D0D0D0 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 { color: var(--rx-orange) !important; }
    section[data-testid="stSidebar"] a { color: var(--rx-orange) !important; }
    section[data-testid="stSidebar"] hr { border-color: #3A3A3A !important; }
    section[data-testid="stSidebar"] code {
        background-color: var(--rx-dark-gray) !important; color: var(--rx-orange) !important;
    }
    .rx-title-bar {
        background: linear-gradient(135deg, var(--rx-black) 0%, var(--rx-dark-gray) 100%);
        padding: 1.2rem 2rem; border-radius: 10px; margin-bottom: 1.5rem;
        border-left: 5px solid var(--rx-orange); display: flex; align-items: center; gap: 1.5rem;
    }
    .rx-title-bar .rx-logo img { height: 60px; width: auto; }
    .rx-title-bar .rx-text h1 {
        color: white !important; margin: 0 !important;
        font-size: 1.6rem !important; line-height: 1.3 !important;
    }
    .rx-title-bar .rx-text p {
        color: #B0B0B0 !important; margin: 0.2rem 0 0 0 !important; font-size: 0.9rem !important;
    }
    [data-testid="stMetric"] {
        background-color: #FAFAFA; border: 1px solid #E0E0E0;
        border-top: 3px solid var(--rx-orange); padding: 0.8rem 1rem; border-radius: 8px;
    }
    [data-testid="stMetricLabel"] p { font-weight: 600 !important; color: var(--rx-mid-gray) !important; }
    [data-testid="stMetricValue"] { color: var(--rx-black) !important; }
    section[data-testid="stSidebar"] .rx-doc-btn {
        display: block !important; text-align: center !important; padding: 0.5rem 1rem !important;
        background-color: #F47920 !important; border: 2px solid #F47920 !important;
        border-radius: 6px !important; text-decoration: none !important; margin: 0 !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn:hover {
        background-color: #D4611A !important; border-color: #D4611A !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn .rx-doc-btn-text {
        color: #FFFFFF !important; font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 600 !important; font-size: 0.82rem !important; letter-spacing: 0.3px !important;
    }
    .val-ok  { color: #2E7D32; font-weight: 600; }
    .val-err { color: #B71C1C; font-weight: 600; }
    /* ── Region indicator banner ── */
    .rx-region-mcc {
        display: flex; align-items: center; gap: 1rem;
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
        border: 2px solid #F47920; border-radius: 10px;
        padding: 0.9rem 1.4rem; margin-bottom: 0.8rem;
    }
    .rx-region-cs {
        display: flex; align-items: center; gap: 1rem;
        background: linear-gradient(135deg, #0D1B2A 0%, #1A2E45 100%);
        border: 2px solid #1E6FBF; border-radius: 10px;
        padding: 0.9rem 1.4rem; margin-bottom: 0.8rem;
    }
    .rx-region-badge-mcc {
        background: #F47920; color: white; font-weight: 800;
        font-size: 1.1rem; padding: 0.3rem 0.9rem; border-radius: 6px;
        letter-spacing: 1px; white-space: nowrap;
    }
    .rx-region-badge-cs {
        background: #1E6FBF; color: white; font-weight: 800;
        font-size: 1.1rem; padding: 0.3rem 0.9rem; border-radius: 6px;
        letter-spacing: 1px; white-space: nowrap;
    }
    .rx-region-text { flex: 1; }
    .rx-region-text h3 { margin: 0 !important; font-size: 1rem !important; }
    .rx-region-text p  { margin: 0.1rem 0 0 0 !important; font-size: 0.82rem !important; color: #B0B0B0 !important; }
    .rx-region-mcc .rx-region-text h3 { color: #F47920 !important; }
    .rx-region-cs  .rx-region-text h3 { color: #1E6FBF !important; }
    /* ── Region-coloured batch section ── */
    .batch-section-mcc {
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
        border: 1px solid #F47920; border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 0.5rem;
    }
    .batch-section-mcc h3 { color: #F47920 !important; margin: 0 0 0.3rem 0 !important; font-size: 1.1rem !important; }
    .batch-section-mcc p  { color: #B0B0B0 !important; font-size: 0.88rem !important; margin: 0 !important; }
    .batch-section-cs {
        background: linear-gradient(135deg, #0D1B2A 0%, #1A2E45 100%);
        border: 1px solid #1E6FBF; border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 0.5rem;
    }
    .batch-section-cs h3 { color: #1E6FBF !important; margin: 0 0 0.3rem 0 !important; font-size: 1.1rem !important; }
    .batch-section-cs p  { color: #B0B0B0 !important; font-size: 0.88rem !important; margin: 0 !important; }
    .batch-section {
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
        border: 1px solid #F47920; border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 1rem;
    }
    .batch-section h3 { color: #F47920 !important; margin: 0 0 0.3rem 0 !important; font-size: 1.1rem !important; }
    .batch-section p  { color: #B0B0B0 !important; font-size: 0.88rem !important; margin: 0 !important; }
    .confirm-section {
        background: #F0FAF0; border: 2px solid #2E7D32;
        border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 1rem;
    }
    .confirm-section h3 { color: #2E7D32 !important; margin: 0 0 0.4rem 0 !important; font-size: 1.05rem !important; }
    .backlog-card {
        background: #FFF8F3; border: 1px solid #F47920;
        border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.5rem;
    }
    .rx-footer { margin-top: 3rem; padding: 1rem 0; border-top: 2px solid var(--rx-orange); text-align: center; }
    .rx-footer p { color: var(--rx-mid-gray) !important; font-size: 0.8rem !important; margin: 0.15rem 0 !important; }
    .rx-footer .rx-conf {
        font-weight: 700; color: var(--rx-orange) !important; text-transform: uppercase;
        letter-spacing: 0.5px; font-size: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
QS_REQUIRED = {"Case ID", "Case Tier", "Total Machines", "Actionable Machines", "Approved Machines", "First Event", "Last Event"}
PL_REQUIRED = {"External Case ID", "Updated"}
CC_REQUIRED = {"Case ID", "Machine Overview", "Investigation Notes", "Pleteo Entity Name", "Company Name", "Actionable Domains"}

MCC_COLUMNS = [
    "Date Added to This Sheet", "Is Multi-National", "Machine Overview",
    "Investigation Notes", "Case ID", "Company Name", "Entity Name",
    "Cylynt Organization Name", "Industry", "Address", "Countries",
    "Estimated Case Value", "Case Tier", "Case Category", "Actionable Category",
    "# All Time Machines", "# Actionable Machines", "# Difference",
    "Actionable Machine IDs", "First Event", "Last Event", "Time Span",
    "Generic Email Address", "Actionable Domains", "Website",
    "Last Updated At", "NNS License Count",
]
CS_COLUMNS = [
    "Date Added to This Sheet", "Is Multi-National", "Machine Overview",
    "Investigation Notes", "Case ID", "Company Name", "Entity Name",
    "Cylynt Organization Name", "Industry", "Addresses", "Country",
    "Case Tier", "Case Category", "Actionable Category",
    "# All Time Machines", "# Actionable Machines", "# Difference",
    "Actionable Machine IDs", "First Event", "Last Event", "Time Span",
    "Generic Email Address", "Actionable Domains", "Website",
]
MCC_COUNTRIES = ["Mexico", "Costa Rica", "Panama", "Dominican Republic",
                  "Honduras", "Belize", "Guatemala", "Nicaragua", "El Salvador"]
CS_COUNTRIES  = ["Chile", "Argentina", "Colombia", "Ecuador",
                  "Peru", "Uruguay", "Bolivia", "Paraguay"]

DEFAULT_MCC_DIST = {
    "name": "Standard MCC", "region": "MCC",
    "groups": [
        {"name": "Mexico", "countries": ["Mexico"], "quota": 40},
        {"name": "Panama · Costa Rica · Dominicana",
         "countries": ["Panama", "Costa Rica", "Dominican Republic"], "quota": 40},
        {"name": "Honduras · Belize · Guatemala · Nicaragua · El Salvador",
         "countries": ["Honduras", "Belize", "Guatemala", "Nicaragua", "El Salvador"], "quota": 40},
    ],
}
DEFAULT_CS_DIST = {
    "name": "Standard CS", "region": "CS",
    "groups": [
        {"name": "Chile",                          "countries": ["Chile"],                         "quota": 20},
        {"name": "Argentina",                      "countries": ["Argentina"],                     "quota": 25},
        {"name": "Colombia · Ecuador",             "countries": ["Colombia", "Ecuador"],           "quota": 35},
        {"name": "Peru",                           "countries": ["Peru"],                          "quota": 10},
        {"name": "Uruguay · Bolivia · Paraguay",   "countries": ["Uruguay", "Bolivia", "Paraguay"],"quota": 20},
    ],
}

HISTORY_FILE = "batch_history.json"
BATCH_LABELS = {
    "standard":    "📊 Batch Standard",
    "low":         "🔵 Batch Low",
    "traditional": "🟡 Batch Traditional",
    "golden":      "🟠 Batch Golden",
}


# ──────────────────────────────────────────────
# GitHub Persistent Storage
# ──────────────────────────────────────────────

def _gh_headers():
    token = st.secrets.get("GITHUB_TOKEN", "")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

def _gh_config():
    """Return (repo, path, branch) from secrets."""
    repo   = st.secrets.get("GITHUB_REPO", "")
    path   = st.secrets.get("HISTORY_FILE_PATH", HISTORY_FILE)
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    return repo, path, branch

def _gh_file_url():
    repo, path, _ = _gh_config()
    return f"https://api.github.com/repos/{repo}/contents/{path}", path

def load_history_from_github():
    """Fetch batch_history.json from GitHub. Returns (history_dict, sha, error_msg)."""
    repo, path, branch = _gh_config()
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    try:
        req = urllib.request.Request(url, headers=_gh_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content), data["sha"], None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"MCC": [], "CS": []}, None, None   # file doesn't exist yet — fresh start
        body = ""
        try: body = e.read().decode()
        except Exception: pass
        return None, None, f"GitHub HTTP {e.code} — {body}"
    except Exception as e:
        return None, None, str(e)

def save_history_to_github(history_dict, sha):
    """Push updated batch_history.json to GitHub. Returns (ok, error_msg, new_sha)."""
    repo, path, branch = _gh_config()
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    content_b64 = base64.b64encode(
        json.dumps(history_dict, indent=2, ensure_ascii=False).encode("utf-8")
    ).decode()
    payload = {
        "message": f"Update batch history — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": content_b64,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha   # required for updating an existing file
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=_gh_headers(), method="PUT")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
        new_sha = result.get("content", {}).get("sha", sha)
        return True, None, new_sha
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()
        except Exception: pass
        return False, f"GitHub HTTP {e.code} — {body}", sha
    except Exception as e:
        return False, str(e), sha


def diagnose_github() -> list:
    """
    Run a sequence of checks against GitHub and return a list of
    (label, ok: bool, detail: str) tuples.
    """
    results = []
    repo, path, branch = _gh_config()
    token = st.secrets.get("GITHUB_TOKEN", "")

    # 1 — Token present
    token_ok = bool(token and len(token) > 10)
    results.append(("Token configured", token_ok,
                    f"`ghp_...{token[-4:]}` ({len(token)} chars)" if token_ok
                    else "GITHUB_TOKEN is empty or missing in Streamlit secrets"))

    # 2 — Repo configured
    repo_ok = bool(repo and "/" in repo and len(repo.split("/")) == 2)
    results.append(("Repo format (owner/repo)", repo_ok,
                    f"`{repo}`" if repo_ok
                    else f"`{repo}` — must be `owner/repo-name` (e.g. `ruvixx/prebatch-delivery`)"))

    # 3 — Repo accessible via API
    if repo_ok and token_ok:
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}",
                headers=_gh_headers()
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                info = json.loads(resp.read().decode())
            default_branch = info.get("default_branch", "unknown")
            results.append(("Repo accessible", True,
                             f"Found `{info.get('full_name')}` · default branch: `{default_branch}`"))

            # 4 — Branch check
            branch_matches = (branch == default_branch)
            results.append((f"Branch `{branch}` matches default", branch_matches,
                             f"GITHUB_BRANCH=`{branch}` vs repo default=`{default_branch}`. "
                             f"{'OK' if branch_matches else f'Update GITHUB_BRANCH to `{default_branch}` in your secrets.'}"))
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()
            except Exception: pass
            if e.code == 401:
                results.append(("Repo accessible", False,
                                 "HTTP 401 — Token is invalid or expired. Regenerate it on GitHub."))
            elif e.code == 404:
                results.append(("Repo accessible", False,
                                 f"HTTP 404 — Repo `{repo}` not found. "
                                 "Check spelling and that the token has access to this repo."))
            else:
                results.append(("Repo accessible", False, f"HTTP {e.code} — {body}"))
        except Exception as e:
            results.append(("Repo accessible", False, str(e)))
    else:
        results.append(("Repo accessible", False, "Skipped — fix token/repo format first"))

    # 5 — History file path
    results.append(("History file path", True,
                     f"`{path}` — file will be created at repo root if it doesn't exist yet"))

    return results


# ──────────────────────────────────────────────
# Session State + History Bootstrap
# ──────────────────────────────────────────────
def _init_state():
    defaults = {
        "result_df": None,          # final output (post-distribution if enabled)
        "raw_df": None,             # full merge before distribution (reference only)
        "dist_report": None,        # distribution stats (shown in results if applied)
        "dist_warnings": [],        # distribution warnings
        "dist_applied": False,      # whether distribution was applied
        "unmatched": [], "grouped": [], "duplicates": [],
        "region_processed": None,
        "generation_log": [],
        # Batch distribution
        "dist_profiles": {
            "MCC": [copy.deepcopy(DEFAULT_MCC_DIST)],
            "CS":  [copy.deepcopy(DEFAULT_CS_DIST)],
        },
        "dist_defaults": {"MCC": "Standard MCC", "CS": "Standard CS"},
        "prebatch_ready_to_confirm": False,
        "editor_profile": None,
        # Delivery history (persistent via GitHub)
        "delivery_history": {"MCC": [], "CS": [], "BigDeals_MCC": [], "BigDeals_CS": []},
        "history_sha": None,
        "history_load_msg": "",
        "history_load_ok": False,
        # Validation gate
        "batch_validated": False,
        "validation_warnings": [],
        "validation_excluded": [],
        "validation_excl_msgs": [],
        "validation_clean": False,
        "excluded_count": 0,
        # App mode
        "app_mode": "Standard Batch",
        # Big Deals state
        "bd_result_df": None,
        "bd_flagged_cases": [],
        "bd_case_mo": {},
        "bd_region_processed": None,
        "bd_ready_to_confirm": False,
        "bd_unmatched": [], "bd_grouped": [], "bd_duplicates": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ──────────────────────────────────────────────
# GitHub History — Cached Fetch (no one-shot flag)
# ──────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_github_history():
    """Fetch batch_history.json. Cached 5 min, shared across sessions."""
    return load_history_from_github()


def _full_payload() -> dict:
    """
    Build the complete JSON payload for GitHub:
    delivery history  +  distribution profiles  +  distribution defaults.
    Always use this instead of passing delivery_history directly.
    """
    payload = dict(st.session_state.delivery_history)
    payload["dist_profiles"] = st.session_state.dist_profiles
    payload["dist_defaults"] = st.session_state.dist_defaults
    return payload


def _apply_history(history, sha):
    data = history or {"MCC": [], "CS": [], "BigDeals_MCC": [], "BigDeals_CS": []}
    for k in ("BigDeals_MCC", "BigDeals_CS"):
        data.setdefault(k, [])

    # Restore distribution profiles if stored (absent in older files → keep defaults)
    if "dist_profiles" in data:
        st.session_state.dist_profiles = data["dist_profiles"]
    if "dist_defaults" in data:
        st.session_state.dist_defaults = data["dist_defaults"]

    # Strip profile keys before storing as delivery_history
    delivery_keys = ("MCC", "CS", "BigDeals_MCC", "BigDeals_CS")
    st.session_state.delivery_history = {k: data.get(k, []) for k in delivery_keys}
    st.session_state.history_sha = sha
    bd_total = (len(data.get("BigDeals_MCC", [])) + len(data.get("BigDeals_CS", [])))
    st.session_state.history_load_ok = True
    st.session_state.history_load_msg = (
        f"✅ Batch history loaded — "
        f"MCC: {len(data.get('MCC', []))} batch(es) · "
        f"CS: {len(data.get('CS', []))} batch(es)"
        + (f" · Big Deals MCC: {len(data.get('BigDeals_MCC', []))} · "
           f"Big Deals CS: {len(data.get('BigDeals_CS', []))}"
           if bd_total > 0 else "")
    )


# Run on every render — cache keeps it fast, TTL keeps it fresh
_hist_data, _hist_sha, _hist_err = _fetch_github_history()
if _hist_err:
    st.session_state.history_load_ok = False
    st.session_state.history_load_msg = f"⚠️ Could not load batch history from GitHub: {_hist_err}"
else:
    _apply_history(_hist_data, _hist_sha)


# ──────────────────────────────────────────────
# History Load Status Banner
# ──────────────────────────────────────────────
if st.session_state.history_load_ok:
    _b_col, _r_col = st.columns([6, 1])
    with _b_col:
        st.success(st.session_state.history_load_msg)
    with _r_col:
        if st.button("🔄", key="reload_history_btn", help="Force reload history from GitHub"):
            _fetch_github_history.clear()
            st.rerun()
else:
    st.warning(st.session_state.history_load_msg)
    _rc1, _rc2 = st.columns([5, 1])
    with _rc2:
        if st.button("🔄 Retry", key="retry_history_btn", help="Retry loading from GitHub"):
            _fetch_github_history.clear()
            st.rerun()
    with st.expander("🔧 GitHub Connection Diagnostics", expanded=True):
        for label, ok, detail in diagnose_github():
            st.markdown(f"{'✅' if ok else '❌'} **{label}** — {detail}")


# ──────────────────────────────────────────────
# Title Bar
# ──────────────────────────────────────────────
logo_html = (f'<div class="rx-logo"><img src="data:image/png;base64,{LOGO_B64}" alt="Ruvixx"></div>'
             if LOGO_B64 else "")
st.markdown(f"""
<div class="rx-title-bar">
    {logo_html}
    <div class="rx-text">
        <h1>Prebatch / Precheck File Generator</h1>
        <p>Upload three source files to generate the Prebatch output for Master Sheet upload</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f'<div style="text-align:center;padding:1.2rem 0 0.6rem 0;">'
            f'<img src="data:image/png;base64,{LOGO_B64}" style="height:36px;width:auto;"></div>',
            unsafe_allow_html=True,
        )
    st.markdown('<hr style="margin:0.4rem 0 1.2rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    if DOC_B64:
        st.markdown(
            '<p style="color:#B0B0B0 !important;font-size:0.82rem;margin:0 0 0.4rem 0;'
            'font-weight:600;letter-spacing:0.2px;">See Documentation</p>',
            unsafe_allow_html=True,
        )
        components.html(f"""
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            button {{
                width: 100%;
                background-color: #F47920;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 0.55rem 1rem;
                font-size: 0.82rem;
                font-weight: 600;
                font-family: 'Source Sans Pro', sans-serif;
                cursor: pointer;
                letter-spacing: 0.3px;
                transition: background-color 0.2s;
            }}
            button:hover {{ background-color: #D4611A; }}
        </style>
        <button onclick="openPDF()">📄 Open Reference Guide</button>
        <script>
            function openPDF() {{
                var b64 = "{DOC_B64}";
                var binary = atob(b64);
                var len = binary.length;
                var bytes = new Uint8Array(len);
                for (var i = 0; i < len; i++) {{
                    bytes[i] = binary.charCodeAt(i);
                }}
                var blob = new Blob([bytes], {{ type: "application/pdf" }});
                var url = URL.createObjectURL(blob);
                window.open(url, "_blank");
            }}
        </script>
        """, height=46)
    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    # ── Delivery History (persistent) ──
    st.markdown("### Delivery History")
    for reg in ["MCC", "CS"]:
        batches = st.session_state.delivery_history.get(reg, [])
        if batches:
            st.markdown(f"**{reg}** — {len(batches)} batch(es)")
            for b in reversed(batches[-5:]):
                label = (f"#{b.get('batch_number','?')} · "
                         f"{b.get('delivery_date','?')} · "
                         f"{b.get('total_cases',0)} cases")
                with st.expander(label, expanded=False):
                    st.caption(f"Profile: {b.get('profile','—')}")
                    cases = b.get("cases", [])
                    if cases:
                        st.dataframe(
                            pd.DataFrame(cases, columns=["Case ID", "Entity Name"]),
                            use_container_width=True, hide_index=True, height=180,
                        )
            # Delete a batch
            with st.expander("🗑 Delete a batch", expanded=False):
                batch_options = {
                    f"#{b.get('batch_number','?')} · {b.get('delivery_date','?')} · {b.get('total_cases',0)} cases": b.get('batch_number')
                    for b in batches
                }
                del_sel = st.selectbox("Select batch to delete", options=list(batch_options.keys()),
                                       key=f"del_sel_{reg}")
                del_confirm = st.checkbox(f"Confirm delete", key=f"del_chk_{reg}")
                if st.button("🗑 Delete", key=f"del_btn_{reg}",
                             use_container_width=True, disabled=not del_confirm):
                    target_num = batch_options[del_sel]
                    st.session_state.delivery_history[reg] = [
                        b for b in batches if b.get("batch_number") != target_num
                    ]
                    ok, err, new_sha = save_history_to_github(
                        _full_payload(), st.session_state.history_sha
                    )
                    if ok:
                        st.session_state.history_sha = new_sha
                        _fetch_github_history.clear()  # bust cache so next render is fresh
                        st.toast(f"✅ Batch #{target_num} deleted from {reg}.", icon="✅")
                        st.rerun()
                    else:
                        st.error(f"GitHub save failed: {err}")
        else:
            st.caption(f"{reg}: No deliveries confirmed yet.")

    # ── Big Deals History ──
    bd_has_any = any(
        st.session_state.delivery_history.get(f"BigDeals_{reg}", [])
        for reg in ["MCC", "CS"]
    )
    if bd_has_any:
        st.markdown('<hr style="margin:0.6rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)
        st.markdown("### 🏆 Big Deals History")
        for reg in ["MCC", "CS"]:
            bd_key = f"BigDeals_{reg}"
            batches = st.session_state.delivery_history.get(bd_key, [])
            if batches:
                st.markdown(f"**Big Deals {reg}** — {len(batches)} batch(es)")
                for b in reversed(batches[-5:]):
                    label = (f"#{b.get('batch_number','?')} · "
                             f"{b.get('delivery_date','?')} · "
                             f"{b.get('total_cases',0)} cases")
                    with st.expander(label, expanded=False):
                        st.caption(f"Region: {reg} · Big Deals")
                        cases = b.get("cases", [])
                        if cases:
                            st.dataframe(
                                pd.DataFrame(cases, columns=["Case ID", "Entity Name"]),
                                use_container_width=True, hide_index=True, height=180,
                            )
                # Delete a Big Deals batch
                with st.expander("🗑 Delete a Big Deals batch", expanded=False):
                    bd_options = {
                        f"#{b.get('batch_number','?')} · {b.get('delivery_date','?')} · {b.get('total_cases',0)} cases": b.get('batch_number')
                        for b in batches
                    }
                    bd_del_sel = st.selectbox("Select batch to delete", options=list(bd_options.keys()),
                                              key=f"del_sel_{bd_key}")
                    bd_del_confirm = st.checkbox("Confirm delete", key=f"del_chk_{bd_key}")
                    if st.button("🗑 Delete", key=f"del_btn_{bd_key}",
                                 use_container_width=True, disabled=not bd_del_confirm):
                        target_num = bd_options[bd_del_sel]
                        st.session_state.delivery_history[bd_key] = [
                            b for b in batches if b.get("batch_number") != target_num
                        ]
                        ok, err, new_sha = save_history_to_github(
                            _full_payload(), st.session_state.history_sha
                        )
                        if ok:
                            st.session_state.history_sha = new_sha
                            _fetch_github_history.clear()  # bust cache so next render is fresh
                            st.toast(f"✅ Big Deals Batch #{target_num} deleted from {reg}.", icon="✅")
                            st.rerun()
                        else:
                            st.error(f"GitHub save failed: {err}")
    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    # ── Session Generation Log ──
    st.markdown("### Session Log")
    log = st.session_state.generation_log
    if not log:
        st.caption("No generations yet this session.")
    else:
        for entry in reversed(log):
            icon = "🟠" if entry["region"] == "MCC" else "🔵"
            with st.expander(
                f"{icon} {entry['region']} · {entry['timestamp']} · {entry['total']} cases",
                expanded=False,
            ):
                st.caption(f"Region: **{entry['region']}** | Generated: {entry['timestamp']}")
                st.caption(f"Total: {entry['total']} | Grouped: {entry['grouped']} | Unmatched: {entry['unmatched']} | Dupes: {entry['duplicates']}")
                if entry.get("confirmed"):
                    st.caption(f"✅ Delivered — Batch #{entry.get('batch_number','?')} on {entry.get('delivery_date','?')}")
                if entry["cases"]:
                    st.dataframe(pd.DataFrame(entry["cases"], columns=["Case ID", "Entity Name"]),
                                 use_container_width=True, hide_index=True, height=200)
        if st.button("Clear Session Log", use_container_width=True):
            st.session_state.generation_log = []
            st.rerun()

    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;font-size:0.72rem;color:#666 !important;margin:0;">'
        'Prebatch Generator v1.2 &middot; May 2026</p>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# Region Selector + File Uploaders
# ──────────────────────────────────────────────

# Initialise region in session state
if "region_choice" not in st.session_state:
    st.session_state.region_choice = "MCC"

rc1, rc2 = st.columns(2)
with rc1:
    if st.button(
        "🟠  MCC — México Central Caribe",
        use_container_width=True,
        type="primary" if st.session_state.region_choice == "MCC" else "secondary",
        key="btn_mcc",
    ):
        st.session_state.region_choice = "MCC"
        st.rerun()
with rc2:
    if st.button(
        "🔵  CS — Cono Sur",
        use_container_width=True,
        type="primary" if st.session_state.region_choice == "CS" else "secondary",
        key="btn_cs",
    ):
        st.session_state.region_choice = "CS"
        st.rerun()

region_code = st.session_state.region_choice

# Inject region-specific CSS overrides so primary button reflects region colour
if region_code == "CS":
    st.markdown("""
    <style>
        button[kind="primary"] {
            background-color: #1E6FBF !important;
            border-color: #1E6FBF !important;
        }
        button[kind="primary"]:hover {
            background-color: #155A9C !important;
            border-color: #155A9C !important;
        }
        [data-testid="stMetric"] { border-top-color: #1E6FBF !important; }
    </style>
    """, unsafe_allow_html=True)

# Region indicator banner
if region_code == "MCC":
    st.markdown("""
    <div class="rx-region-mcc">
        <span class="rx-region-badge-mcc">MCC</span>
        <div class="rx-region-text">
            <h3>México Central Caribe</h3>
            <p>Mexico · Costa Rica · Panama · Dominican Republic · Honduras · Belize · Guatemala · Nicaragua · El Salvador</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="rx-region-cs">
        <span class="rx-region-badge-cs">CS</span>
        <div class="rx-region-text">
            <h3>Cono Sur</h3>
            <p>Chile · Argentina · Colombia · Ecuador · Peru · Uruguay · Bolivia · Paraguay</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Reset validation when region changes
if st.session_state.get("_last_region") != region_code:
    st.session_state.batch_validated = False
    st.session_state.validation_warnings = []
    st.session_state.validation_excluded = []
    st.session_state.validation_clean = False
    st.session_state.prebatch_ready_to_confirm = False
    st.session_state.bd_result_df = None
    st.session_state.bd_flagged_cases = []
    st.session_state.bd_case_mo = {}
    st.session_state.bd_ready_to_confirm = False
    st.session_state._last_region = region_code

# ── Mode Selector ──
_accent = "#F47920" if region_code == "MCC" else "#1E6FBF"
st.markdown("")
mc1, mc2 = st.columns(2)
with mc1:
    if st.button(
        "📋  Standard Batch",
        use_container_width=True,
        type="primary" if st.session_state.app_mode == "Standard Batch" else "secondary",
        key="mode_standard_btn",
        help="Generate Prebatch files from QS, Pleteo, and Conflict Check exports.",
    ):
        st.session_state.app_mode = "Standard Batch"
        st.rerun()
with mc2:
    if st.button(
        "🏆  Big Deals — 15+ Machines",
        use_container_width=True,
        type="primary" if st.session_state.app_mode == "Big Deals" else "secondary",
        key="mode_bigdeals_btn",
        help="Special flow for cases with 15+ Total Machines. Conflict Check is optional.",
    ):
        st.session_state.app_mode = "Big Deals"
        st.rerun()

_app_mode = st.session_state.app_mode

st.divider()

# ── File Uploaders (mode-specific) ──
if _app_mode == "Standard Batch":
    st.subheader("Upload Source Files")
    col1, col2, col3 = st.columns(3)
    with col1:
        qs_files = st.file_uploader(
            "QS Delivery ID File",
            type=["csv","xlsx","xls"],
            accept_multiple_files=True,
            help="Upload one or more QS Delivery ID files. Multiple files are merged into one before processing.",
        )
    with col2:
        pl_file = st.file_uploader("PL Batch File (Pleteo Export)", type=["csv","xlsx","xls"],
            help="CRM export providing the 'Updated' timestamp for Last Updated At (MCC).")
    with col3:
        pc_file = st.file_uploader("Conflict Check File", type=["csv","xlsx","xls"],
            help="Investigation data: machine overviews, notes, entity details, and case attribution.")
    if qs_files and len(qs_files) > 1:
        st.info(f"📎 **{len(qs_files)} QS files uploaded** — they will be merged into one before processing.")

else:  # Big Deals
    _bd_cls = "batch-section-mcc" if region_code == "MCC" else "batch-section-cs"
    st.markdown(f"""
    <div class="{_bd_cls}">
        <h3>🏆 Big Deals — Special Batch Delivery</h3>
        <p>For cases with <strong>15+ Total Machines</strong>. Conflict Check is optional — Machine Overview
        will be generated from individual case files where missing. Previously delivered cases may be included.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    bd_col1, bd_col2, bd_col3 = st.columns(3)
    with bd_col1:
        bd_qs_files = st.file_uploader(
            "QS Delivery ID File(s)", type=["csv","xlsx","xls"],
            accept_multiple_files=True, key="bd_qs_uploader",
            help="One or more QS Delivery ID files. Merged before processing.",
        )
    with bd_col2:
        bd_pl_file = st.file_uploader(
            "PL Batch File (Pleteo Export)", type=["csv","xlsx","xls"],
            key="bd_pl_uploader",
            help="Pleteo CRM export. Required for Last Updated At (MCC).",
        )
    with bd_col3:
        bd_cc_file = st.file_uploader(
            "Conflict Check (optional)", type=["csv","xlsx","xls"],
            key="bd_cc_uploader",
            help="Optional. If provided, Machine Overview is pulled from it where available.",
        )
    if bd_cc_file is None:
        st.caption("ℹ️ No Conflict Check uploaded — Machine Overview will be generated from case sheets for all cases.")
    if bd_qs_files and len(bd_qs_files) > 1:
        st.info(f"📎 **{len(bd_qs_files)} QS files uploaded** — they will be merged before processing.")


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def read_file(f):
    f.seek(0)
    name = f.name.lower()
    return (pd.read_csv(f, dtype=str, keep_default_na=False)
            if name.endswith(".csv")
            else pd.read_excel(f, dtype=str, keep_default_na=False))

def merge_qs_files(uploaded_files):
    """Read and vertically concatenate one or more QS files into a single DataFrame."""
    frames = []
    for f in uploaded_files:
        frames.append(read_file(f))
    if not frames:
        return pd.DataFrame()
    merged = pd.concat(frames, ignore_index=True)
    return merged

def clean_df(df):
    df.columns = [str(c).strip() for c in df.columns]
    return df.replace("", pd.NA).dropna(how="all").fillna("")

def validate_file(df, required_cols):
    missing = required_cols - set(df.columns)
    return len(missing) == 0, missing

def show_validation(uploaded_file, required_cols, label):
    if uploaded_file is None:
        return None, False
    try:
        df = clean_df(read_file(uploaded_file))
        ok, missing = validate_file(df, required_cols)
        if ok:
            st.markdown(f'<span class="val-ok">✔ {label}</span> — {len(df)} rows, {len(df.columns)} columns', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="val-err">✘ {label}</span> — missing: `{"`, `".join(sorted(missing))}`', unsafe_allow_html=True)
        return df, ok
    except Exception as e:
        st.markdown(f'<span class="val-err">✘ {label}</span> — could not read file: {e}', unsafe_allow_html=True)
        return None, False

def normalize_date(value: str) -> str:
    if not value or value.strip() == "":
        return value
    v = value.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", v):
        return v
    for fmt in ["%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
                "%d-%m-%Y %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    try:
        return pd.to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return value

def safe_get(source, col, default=""):
    if isinstance(source, pd.Series) and col in source.index:
        val = source[col]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return str(val).strip()
    return default

def build_lookup(df, key_col):
    return {str(row.get(key_col,"")).strip(): row
            for _, row in df.iterrows()
            if str(row.get(key_col,"")).strip() and str(row.get(key_col,"")).strip().lower() != "nan"}

def get_latest_updated(pl_lookup, case_ids):
    latest = ""
    for cid in case_ids:
        row = pl_lookup.get(cid)
        if row is not None:
            upd = safe_get(row, "Updated")
            if upd and upd > latest:
                latest = upd
    return latest

def combine_machine_overviews(cc_lookup, case_ids):
    seen, unique = set(), []
    for cid in case_ids:
        row = cc_lookup.get(cid)
        if row is not None:
            mo = safe_get(row, "Machine Overview")
            if mo and mo not in seen:
                seen.add(mo); unique.append(mo)
    return ", ".join(unique)

def combine_investigation_notes(cc_lookup, case_ids):
    notes = [safe_get(cc_lookup[cid], "Investigation Notes")
             for cid in case_ids if cid in cc_lookup
             and safe_get(cc_lookup[cid], "Investigation Notes")]
    if not notes: return ""
    return notes[0] if len(notes) == 1 else "\n\n---\n\n".join(notes)

def to_excel(df, sheet_name="Prebatch"):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        for i, col in enumerate(df.columns, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(len(str(col)) + 4, 42)
    return buf.getvalue()

def generate_id_strings(ids: list, chunk_size: int = 100) -> list:
    return [",".join(ids[i:i + chunk_size]) for i in range(0, len(ids), chunk_size)]


# ──────────────────────────────────────────────
# Batch History Validation
# ──────────────────────────────────────────────

def normalize_case_id(case_id: str) -> str:
    """Sort sub-IDs alphabetically so order never affects comparison."""
    parts = sorted(c.strip() for c in case_id.split(",") if c.strip())
    return ",".join(parts)


def six_months_ago() -> date:
    """Return today minus exactly 6 months."""
    today = date.today()
    month = today.month - 6
    year  = today.year
    if month <= 0:
        month += 12
        year  -= 1
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(today.day, max_day))


def validate_against_history(case_ids: list, region: str):
    """
    Check Case IDs against delivery history (Standard + Big Deals).

    Rules:
    - Delivered within the last 6 months → EXCLUDED from generation (returned in excluded_ids).
    - Delivered more than 6 months ago   → WARNING only (can still be generated).
    - Sub-ID order is normalised before comparison.

    Returns:
        excluded_ids  — set of normalised Case IDs to auto-remove at generation
        excluded_msgs — human-readable lines for the excluded group
        warning_msgs  — human-readable lines for the eligible-but-repeated group
        is_clean      — True when both excluded and warnings are empty
    """
    cutoff = six_months_ago()

    # Build lookup: normalised_case_id → (batch_num, delivery_date, batch_type)
    delivered: dict = {}
    for hist_key in [region, f"BigDeals_{region}"]:
        for batch in st.session_state.delivery_history.get(hist_key, []):
            b_num  = batch.get("batch_number", "?")
            b_date = batch.get("delivery_date", "?")
            b_type = "Big Deals" if hist_key.startswith("BigDeals_") else "Standard"
            for case in batch.get("cases", []):
                raw_cid = case[0] if isinstance(case, (list, tuple)) else case.get("case_id", "")
                norm    = normalize_case_id(raw_cid)
                # Keep the most recent delivery if a case appears in multiple batches
                if norm not in delivered:
                    delivered[norm] = (b_num, b_date, b_type)
                else:
                    existing_date = delivered[norm][1]
                    if b_date > existing_date:
                        delivered[norm] = (b_num, b_date, b_type)

    excluded_ids:  set  = set()
    excluded_msgs: list = []
    warning_msgs:  list = []

    for cid in case_ids:
        norm = normalize_case_id(cid)
        if norm not in delivered:
            continue
        b_num, b_date, b_type = delivered[norm]

        # Parse delivery date for 6-month comparison
        try:
            delivered_on = datetime.strptime(b_date, "%Y-%m-%d").date()
        except ValueError:
            delivered_on = None

        if delivered_on and delivered_on >= cutoff:
            # Within 6 months → exclude from generation
            excluded_ids.add(norm)
            months_since = (date.today().year - delivered_on.year) * 12 + \
                           (date.today().month - delivered_on.month)
            excluded_msgs.append(
                f"🚫 **{cid}** — delivered {months_since}mo ago in {b_type} Batch "
                f"**#{b_num}** on {b_date}. **Automatically excluded** (within 6-month window)."
            )
        else:
            # Older than 6 months → warn but allow
            warning_msgs.append(
                f"⚠️ **{cid}** — previously delivered in {b_type} Batch "
                f"**#{b_num}** on {b_date}. Eligible for relaunch (older than 6 months)."
            )

    is_clean = not excluded_ids and not warning_msgs
    return excluded_ids, excluded_msgs, warning_msgs, is_clean


# ──────────────────────────────────────────────
# Core Processing
# ──────────────────────────────────────────────

def process_data(qs_df, pl_df, cc_df, region_code):
    qs_df, pl_df, cc_df = clean_df(qs_df), clean_df(pl_df), clean_df(cc_df)
    cc_lookup = build_lookup(cc_df, "Case ID")
    pl_lookup = build_lookup(pl_df, "External Case ID")

    # Cases to exclude due to 6-month window (set of normalised IDs)
    excluded_norm = st.session_state.get("validation_excluded", set())

    output_rows, unmatched_cases, grouped_cases = [], [], []
    seen_case_ids, duplicate_cases = {}, []
    excluded_count = 0

    for idx, (_, qs_row) in enumerate(qs_df.iterrows()):
        case_id_raw = str(qs_row.get("Case ID","")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue
        if case_id_raw in seen_case_ids:
            duplicate_cases.append(case_id_raw)
            continue
        seen_case_ids[case_id_raw] = idx

        # Skip cases excluded by the 6-month window
        if normalize_case_id(case_id_raw) in excluded_norm:
            excluded_count += 1
            continue

        case_ids = [c.strip() for c in case_id_raw.split(",") if c.strip()]
        if not case_ids: continue
        if len(case_ids) > 1: grouped_cases.append(case_id_raw)

        cc_row = next((cc_lookup[cid] for cid in case_ids if cid in cc_lookup), None)
        if cc_row is None:
            unmatched_cases.append(case_id_raw)
            cc_row = pd.Series(dtype=str)

        machine_overview = (combine_machine_overviews(cc_lookup, case_ids) if len(case_ids) > 1
                            else safe_get(cc_row, "Machine Overview"))
        investigation_notes = (combine_investigation_notes(cc_lookup, case_ids) if len(case_ids) > 1
                               else safe_get(cc_row, "Investigation Notes"))
        actionable_domains = safe_get(cc_row, "Actionable Domains") or safe_get(qs_row, "Actionable Domains")
        website = safe_get(cc_row, "Website") or safe_get(qs_row, "Websites")
        entity_name = safe_get(cc_row, "Pleteo Entity Name") or safe_get(qs_row, "Company Name")
        first_event = normalize_date(safe_get(qs_row, "First Event"))
        last_event  = normalize_date(safe_get(qs_row, "Last Event"))

        base = {
            "Date Added to This Sheet": "", "Is Multi-National": safe_get(cc_row, "Is Multi National"),
            "Machine Overview": machine_overview, "Investigation Notes": investigation_notes,
            "Case ID": case_id_raw, "Company Name": safe_get(cc_row, "Company Name"),
            "Entity Name": entity_name, "Cylynt Organization Name": safe_get(cc_row, "Cylynt Organization Name"),
            "Industry": safe_get(cc_row, "Industry"), "Case Tier": safe_get(qs_row, "Case Tier"),
            "Case Category": safe_get(qs_row, "[Cfa]-Category"),
            "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
            "# All Time Machines": safe_get(qs_row, "Total Machines"),
            "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
            "# Difference": safe_get(qs_row, "[CFa]-Difference"),
            "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
            "First Event": first_event, "Last Event": last_event,
            "Time Span": safe_get(cc_row, "Time Span"),
            "Generic Email Address": safe_get(cc_row, "Generic Email Addresses"),
            "Actionable Domains": actionable_domains, "Website": website,
        }

        if region_code == "MCC":
            last_updated = normalize_date(get_latest_updated(pl_lookup, case_ids))
            row_data = {**base,
                "Address": safe_get(cc_row, "Address"), "Countries": safe_get(cc_row, "Countries"),
                "Estimated Case Value": "", "Last Updated At": last_updated, "NNS License Count": "",
            }
        else:
            row_data = {**base,
                "Addresses": safe_get(cc_row, "Address"), "Country": safe_get(cc_row, "Countries"),
            }
        output_rows.append(row_data)

    target_cols = MCC_COLUMNS if region_code == "MCC" else CS_COLUMNS
    result_df = pd.DataFrame(output_rows, columns=target_cols)
    return result_df, unmatched_cases, grouped_cases, duplicate_cases, excluded_count


# ──────────────────────────────────────────────
# Batch Distribution — Core Algorithm
# ──────────────────────────────────────────────

def case_matches_group(country_val: str, group_countries: list) -> bool:
    cv = str(country_val).lower()
    return any(gc.lower() in cv for gc in group_countries)

def apply_batch_distribution(df, distribution, region_code, batch_type="standard"):
    """
    batch_type:
        "standard"    — fill by country availability, no machine filtering
        "low"         — <3 machines only, fill by country, overflow any unused <3
        "golden"      — 3+ first, overflow unused 3+, then fill remainder with anything; warn if <3 used
        "traditional" — 50% global 3+ by country, then 50% <3 by country, then overflow anything
    """
    country_col = "Countries" if region_code == "MCC" else "Country"
    df_work = df.copy().reset_index(drop=True)
    df_work["_m"] = pd.to_numeric(df_work["# All Time Machines"], errors="coerce").fillna(0)

    groups       = distribution["groups"]
    total_quota  = sum(g["quota"] for g in groups)
    n_groups     = len(groups)

    warnings         = []
    group_selections = [[] for _ in range(n_groups)]
    used             = set()

    # ── Build per-group country pools from the full dataset ──
    def country_pool(source_idx, group):
        return [i for i in source_idx
                if i not in used
                and case_matches_group(df_work.loc[i, country_col], group["countries"])]

    # ── Generic first-pass fill ──
    def fill_groups(source_idx, per_group_caps=None):
        """Fill each group from source_idx up to its cap (or group quota if cap not given)."""
        for gi, group in enumerate(groups):
            cap = per_group_caps[gi] if per_group_caps else group["quota"]
            already = len(group_selections[gi])
            remaining = cap - already
            if remaining <= 0:
                continue
            pool = country_pool(source_idx, group)
            take = pool[:remaining]
            group_selections[gi].extend(take)
            used.update(take)

    # ── Overflow: fill shortfalls from any eligible pool, from other groups' countries ──
    def overflow_fill(eligible_idx):
        """After main passes, fill any remaining shortfalls from eligible_idx."""
        for gi, group in enumerate(groups):
            shortfall = group["quota"] - len(group_selections[gi])
            if shortfall <= 0:
                continue
            # Borrow from eligible pool regardless of country
            available = [i for i in eligible_idx if i not in used]
            take = available[:shortfall]
            if take:
                group_selections[gi].extend(take)
                used.update(take)

    # ────────────────────────────────────────────
    # STANDARD
    # ────────────────────────────────────────────
    if batch_type == "standard":
        all_idx = list(df_work.index)
        fill_groups(all_idx)
        overflow_fill(all_idx)

    # ────────────────────────────────────────────
    # LOW  (<3 machines only)
    # ────────────────────────────────────────────
    elif batch_type == "low":
        low_idx = df_work[df_work["_m"] < 3].index.tolist()
        fill_groups(low_idx)
        overflow_fill(low_idx)

    # ────────────────────────────────────────────
    # GOLDEN  (3+ first, overflow 3+, then anything)
    # ────────────────────────────────────────────
    elif batch_type == "golden":
        premium_idx = (df_work[df_work["_m"] >= 3]
                       .sort_values("_m", ascending=False).index.tolist())

        # Pass 1 — 3+ by country
        fill_groups(premium_idx)

        # Overflow — unused 3+ from other groups
        overflow_fill(premium_idx)

        # Pass 2 — if still short, use anything remaining
        total_selected_so_far = sum(len(s) for s in group_selections)
        if total_selected_so_far < total_quota:
            any_remaining = [i for i in df_work.index if i not in used]
            # sort 3+ first, then <3
            any_remaining.sort(key=lambda i: -df_work.loc[i, "_m"])
            under3_used = False
            still_needed_global = total_quota - total_selected_so_far
            overflow_taken = any_remaining[:still_needed_global]
            for idx_val in overflow_taken:
                if df_work.loc[idx_val, "_m"] < 3:
                    under3_used = True
                for gi, group in enumerate(groups):
                    if len(group_selections[gi]) < group["quota"]:
                        group_selections[gi].append(idx_val)
                        used.add(idx_val)
                        break
                else:
                    group_selections[0].append(idx_val)
                    used.add(idx_val)
            if under3_used:
                warnings.append(
                    "⚠️ **Golden Batch:** Cases with < 3 machines were included to complete "
                    "the total quota because not enough 3+ machine cases were available."
                )

    # ────────────────────────────────────────────
    # TRADITIONAL  (50% 3+, then 50% <3, then overflow)
    # ────────────────────────────────────────────
    elif batch_type == "traditional":
        premium_target = total_quota // 2
        premium_idx = (df_work[df_work["_m"] >= 3]
                       .sort_values("_m", ascending=False).index.tolist())
        under3_idx  = df_work[df_work["_m"] < 3].index.tolist()

        # Pass 1 — 3+ cases, globally capped at premium_target
        premium_selected = 0
        for gi, group in enumerate(groups):
            if premium_selected >= premium_target:
                break
            pool = country_pool(premium_idx, group)
            can_take = min(len(pool), group["quota"], premium_target - premium_selected)
            take = pool[:can_take]
            group_selections[gi].extend(take)
            used.update(take)
            premium_selected += len(take)

        # Pass 2 — <3 cases, fill remaining per-group quota
        fill_groups(under3_idx)

        # Pass 3 — overflow: any unused cases for remaining shortfalls
        all_idx = list(df_work.index)
        overflow_fill(all_idx)

    # ────────────────────────────────────────────
    # Build group reports + overflow warnings
    # ────────────────────────────────────────────
    group_reports = []
    for gi, group in enumerate(groups):
        filled   = len(group_selections[gi])
        shortfall = group["quota"] - filled
        # Detect overflow: cases in this group not from its own country pool
        own_countries = group["countries"]
        overflow_cases = [
            i for i in group_selections[gi]
            if not case_matches_group(df_work.loc[i, country_col], own_countries)
        ]
        overflow_note = f"{len(overflow_cases)} overflow case(s) from other groups" if overflow_cases else ""
        group_reports.append({
            "group":    group["name"],
            "quota":    group["quota"],
            "filled":   filled,
            "shortfall": max(shortfall, 0),
            "overflow_note": overflow_note,
        })
        if overflow_cases:
            warnings.append(
                f"⚠️ Group **{group['name']}**: {len(overflow_cases)} case(s) were filled "
                f"with overflow from other country groups to meet the quota."
            )

    # Total quota warning
    total_selected = sum(len(s) for s in group_selections)
    if total_selected < total_quota:
        warnings.append(
            f"🚨 **Total batch quota not met:** {total_selected} of {total_quota} cases selected. "
            f"Not enough cases available in the uploaded file to complete the full batch."
        )

    # ── Build output DataFrame ──
    all_selected_idx = sorted(set(idx for sel in group_selections for idx in sel))
    drop_cols = [c for c in ["_m"] if c in df_work.columns]
    selected_df = (df_work.loc[all_selected_idx]
                   .drop(columns=drop_cols)
                   .reset_index(drop=True))

    # Backlog
    backlog_df = df_work[~df_work.index.isin(all_selected_idx)].copy()
    backlog_summary = {}
    for _, row in backlog_df.iterrows():
        cv = str(row.get(country_col, "Unknown")).strip()
        ctries = [c.strip() for c in re.split(r"[,|;\s/]+", cv) if c.strip()] or ["Unknown"]
        m = float(row.get("_m", 0))
        for c in ctries:
            if c not in backlog_summary:
                backlog_summary[c] = {"total": 0, "priority": 0, "standard": 0}
            backlog_summary[c]["total"] += 1
            if m >= 3: backlog_summary[c]["priority"] += 1
            else:       backlog_summary[c]["standard"] += 1

    backlog_table = pd.DataFrame([
        {"Country": c, "Total Backlog": v["total"],
         "3+ Machines": v["priority"], "< 3 Machines": v["standard"]}
        for c, v in sorted(backlog_summary.items(), key=lambda x: -x[1]["total"])
    ])

    report = {
        "groups": group_reports, "total_selected": total_selected,
        "total_quota": total_quota, "total_backlog": len(backlog_df),
        "backlog_table": backlog_table, "profile_name": distribution["name"],
        "batch_type": batch_type,
    }
    return selected_df, report, warnings


# ──────────────────────────────────────────────
# Distribution Profile Helpers
# ──────────────────────────────────────────────

def get_profiles(region):     return st.session_state.dist_profiles.get(region, [])
def get_profile_names(region): return [p["name"] for p in get_profiles(region)]
def get_profile(region, name): return next((p for p in get_profiles(region) if p["name"] == name), None)

def save_profile(region, profile):
    profiles = st.session_state.dist_profiles.setdefault(region, [])
    for i, p in enumerate(profiles):
        if p["name"] == profile["name"]:
            profiles[i] = copy.deepcopy(profile); return
    profiles.append(copy.deepcopy(profile))

def delete_profile(region, name):
    st.session_state.dist_profiles[region] = [
        p for p in st.session_state.dist_profiles.get(region, []) if p["name"] != name
    ]
    if st.session_state.dist_defaults.get(region) == name:
        remaining = st.session_state.dist_profiles[region]
        st.session_state.dist_defaults[region] = remaining[0]["name"] if remaining else None

def set_default(region, name): st.session_state.dist_defaults[region] = name

def export_profiles_json():
    return json.dumps({"profiles": st.session_state.dist_profiles,
                       "defaults": st.session_state.dist_defaults}, indent=2)

def import_profiles_json(raw_json):
    data = json.loads(raw_json)
    if "profiles" in data: st.session_state.dist_profiles = data["profiles"]
    if "defaults" in data: st.session_state.dist_defaults = data["defaults"]

def next_batch_number(region):
    batches = st.session_state.delivery_history.get(region, [])
    if not batches: return 1
    try:
        return max(int(b.get("batch_number", 0)) for b in batches) + 1
    except Exception:
        return len(batches) + 1


# ──────────────────────────────────────────────
# Big Deals — Helper Functions
# ──────────────────────────────────────────────

def parse_version_year(version_str: str):
    """
    Parse a version string and return the 4-digit year inferred from the
    highest version's first segment.
    Handles formats: '21.0: 78, 18.1: 12'  or  '21.25.4525'  or  '21.0'
    First two digits + 2000 = year  (e.g. 21 → 2021, 18 → 2018).
    Returns a 4-char year string or None.
    """
    if not version_str or str(version_str).strip().lower() in ("", "nan", "none"):
        return None
    # Find all leading version numbers before first dot  (e.g. '21' from '21.0')
    matches = re.findall(r'\b(\d{1,2})\.\d', str(version_str))
    if not matches:
        return None
    highest = max(int(m) for m in matches)
    if 1 <= highest <= 99:
        return str(2000 + highest)
    return None


def generate_machine_overview_from_files(machines_df: pd.DataFrame,
                                          events_df: pd.DataFrame = None) -> str:
    """
    Build Machine Overview string from a case's exported machines file.
    Only counts machines with Approval Status = 'Approved'.
    Uses the Products column; resolves year via Version if absent from product name.
    Returns format: 'SketchUp Pro 2021 (3x), SketchUp Make 2017 (1x)'
    """
    machines_df = clean_df(machines_df.copy())
    if "Approval Status" not in machines_df.columns:
        return ""

    approved = machines_df[
        machines_df["Approval Status"].str.strip().str.lower() == "approved"
    ]
    if approved.empty:
        return ""

    product_counts: dict = {}

    for _, row in approved.iterrows():
        products_raw = str(row.get("Products", "")).strip()
        version_raw  = str(row.get("Version",  "")).strip()

        if not products_raw or products_raw.lower() in ("nan", ""):
            continue

        for product in [p.strip() for p in products_raw.split(",") if p.strip()]:
            # Keep year if already present (e.g. 'SketchUp Pro 2021')
            if re.search(r'\b20\d{2}\b', product):
                resolved = product
            else:
                year = parse_version_year(version_raw)
                resolved = f"{product} {year}" if year else product
            product_counts[resolved] = product_counts.get(resolved, 0) + 1

    if not product_counts:
        return ""

    return ", ".join(
        f"{name} ({cnt}x)"
        for name, cnt in sorted(product_counts.items(), key=lambda x: -x[1])
    )


def process_big_deals_data(qs_df, pl_df, cc_df, region_code):
    """
    Process Big Deals cases (Total Machines ≥ 15).
    cc_df may be None — Machine Overview left blank and case is flagged.
    Returns: result_df, flagged_case_ids, unmatched, grouped, duplicates
    """
    qs_df = clean_df(qs_df)
    pl_df = clean_df(pl_df)
    cc_df = clean_df(cc_df) if cc_df is not None else None

    cc_lookup = build_lookup(cc_df, "Case ID") if cc_df is not None else {}
    pl_lookup  = build_lookup(pl_df, "External Case ID")

    output_rows, flagged_cases = [], []
    unmatched_cases, grouped_cases, duplicate_cases = [], [], []
    seen_ids: dict = {}

    for idx, (_, qs_row) in enumerate(qs_df.iterrows()):
        case_id_raw = str(qs_row.get("Case ID", "")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue
        if case_id_raw in seen_ids:
            duplicate_cases.append(case_id_raw)
            continue
        seen_ids[case_id_raw] = idx

        # 15+ machines gate
        total_m = pd.to_numeric(qs_row.get("Total Machines", 0), errors="coerce")
        if pd.isna(total_m) or int(total_m) < 15:
            continue

        case_ids = [c.strip() for c in case_id_raw.split(",") if c.strip()]
        if len(case_ids) > 1:
            grouped_cases.append(case_id_raw)

        cc_row = next((cc_lookup[cid] for cid in case_ids if cid in cc_lookup), None)
        if cc_row is None:
            if cc_df is not None:
                unmatched_cases.append(case_id_raw)
            cc_row = pd.Series(dtype=str)

        machine_overview = (
            combine_machine_overviews(cc_lookup, case_ids) if len(case_ids) > 1
            else safe_get(cc_row, "Machine Overview")
        )

        actionable_domains = safe_get(cc_row, "Actionable Domains") or safe_get(qs_row, "Actionable Domains")
        website     = safe_get(cc_row, "Website")  or safe_get(qs_row, "Websites")
        entity_name = safe_get(cc_row, "Pleteo Entity Name") or safe_get(qs_row, "Company Name")
        first_event = normalize_date(safe_get(qs_row, "First Event"))
        last_event  = normalize_date(safe_get(qs_row, "Last Event"))

        base = {
            "Date Added to This Sheet": "",
            "Is Multi-National": safe_get(cc_row, "Is Multi National"),
            "Machine Overview": machine_overview,
            "Investigation Notes": (
                combine_investigation_notes(cc_lookup, case_ids) if len(case_ids) > 1
                else safe_get(cc_row, "Investigation Notes")
            ),
            "Case ID": case_id_raw,
            "Company Name": safe_get(cc_row, "Company Name"),
            "Entity Name": entity_name,
            "Cylynt Organization Name": safe_get(cc_row, "Cylynt Organization Name"),
            "Industry": safe_get(cc_row, "Industry"),
            "Case Tier": safe_get(qs_row, "Case Tier"),
            "Case Category": safe_get(qs_row, "[Cfa]-Category"),
            "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
            "# All Time Machines": safe_get(qs_row, "Total Machines"),
            "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
            "# Difference": safe_get(qs_row, "[CFa]-Difference"),
            "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
            "First Event": first_event, "Last Event": last_event,
            "Time Span": safe_get(cc_row, "Time Span"),
            "Generic Email Address": safe_get(cc_row, "Generic Email Addresses"),
            "Actionable Domains": actionable_domains,
            "Website": website,
        }

        if region_code == "MCC":
            last_updated = normalize_date(get_latest_updated(pl_lookup, case_ids))
            row_data = {**base,
                "Address": safe_get(cc_row, "Address"),
                "Countries": safe_get(cc_row, "Countries"),
                "Estimated Case Value": "",
                "Last Updated At": last_updated,
                "NNS License Count": "",
            }
        else:
            row_data = {**base,
                "Addresses": safe_get(cc_row, "Address"),
                "Country": safe_get(cc_row, "Countries"),
            }

        if not machine_overview:
            flagged_cases.append(case_id_raw)

        output_rows.append(row_data)

    target_cols = MCC_COLUMNS if region_code == "MCC" else CS_COLUMNS
    result_df = pd.DataFrame(output_rows, columns=target_cols)
    return result_df, flagged_cases, unmatched_cases, grouped_cases, duplicate_cases


# ──────────────────────────────────────────────
# Batch Distribution Config (Standard Batch only)
# ──────────────────────────────────────────────
if _app_mode == "Standard Batch":
    _batch_cls = "batch-section-mcc" if region_code == "MCC" else "batch-section-cs"
    st.markdown("")
    st.markdown(f"""
    <div class="{_batch_cls}">
        <h3>📦 Batch Distribution</h3>
        <p>Optional tool to automatically distribute large Pleteo exports by country group and quota,
           without manually selecting cases. Use this when working with large batches where cases
           haven't been pre-selected. If cases were already manually curated for delivery,
           skip this section and proceed directly to Generate.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    enable_batch = st.toggle(
        "Enable Batch Distribution",
        value=False, key="batch_toggle",
        help=(
            "Use this when you have a large Pleteo export and want the app to automatically "
            "select cases by country group and quota. "
            "If you've already manually selected the cases for this delivery, leave this off."
        ),
    )

    if enable_batch:
        st.info(
            "💡 **About Batch Distribution:** This tool helps deliver large batches from a full "
            "Pleteo case export without manually picking cases. It selects cases automatically based "
            "on country group quotas. If you already have a curated list of cases for this batch, "
            "you don't need to use this — simply generate the Prebatch file directly.",
            icon=None,
        )

        _rp_for_config = region_code
        _region_profiles = get_profile_names(_rp_for_config)
        _default_name = st.session_state.dist_defaults.get(_rp_for_config)

        # Use pending selection if a save just happened, then clear it
        _pending = st.session_state.pop("_pending_dist_select", None)
        if _pending and _pending in _region_profiles:
            _select_idx = _region_profiles.index(_pending)
        elif _default_name in _region_profiles:
            _select_idx = _region_profiles.index(_default_name)
        else:
            _select_idx = 0

        ps_col, def_col, del_col = st.columns([3, 1.2, 1])
        with ps_col:
            selected_profile_name = st.selectbox("Distribution Profile", options=_region_profiles,
                                                  index=_select_idx, key="dist_select")
        with def_col:
            _is_default = (st.session_state.dist_defaults.get(_rp_for_config) == selected_profile_name)
            st.markdown("<br>", unsafe_allow_html=True)
            if _is_default:
                st.success("Default ✓")
            else:
                if st.button("Set as Default", key="set_default_btn", use_container_width=True):
                    set_default(_rp_for_config, selected_profile_name)
                    _ok, _err, _sha = save_history_to_github(_full_payload(), st.session_state.history_sha)
                    if _ok:
                        st.session_state.history_sha = _sha
                        _fetch_github_history.clear()
                    st.rerun()
        with del_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if len(_region_profiles) > 1:
                if st.button("🗑 Delete", key="del_profile_btn", use_container_width=True):
                    delete_profile(_rp_for_config, selected_profile_name)
                    _ok, _err, _sha = save_history_to_github(_full_payload(), st.session_state.history_sha)
                    if _ok:
                        st.session_state.history_sha = _sha
                        _fetch_github_history.clear()
                    st.rerun()
            else:
                st.button("🗑 Delete", disabled=True, use_container_width=True, key="del_profile_dis")

        _selected_profile = get_profile(_rp_for_config, selected_profile_name)
        if _selected_profile is None:
            st.error("Profile not found. Please select another.")
            st.stop()

        if (st.session_state.editor_profile is None
                or st.session_state.editor_profile.get("_editing_name") != selected_profile_name):
            ep = copy.deepcopy(_selected_profile)
            ep["_editing_name"] = selected_profile_name
            st.session_state.editor_profile = ep

        ep = st.session_state.editor_profile

        BATCH_TYPE_OPTIONS = {
            "standard":    "📊 Batch Standard — Fill by country availability (no machine filter)",
            "low":         "🔵 Batch Low — Cases with < 3 machines only",
            "traditional": "🟡 Batch Traditional — 50% cases with 3+ machines, rest with 1–2 machines",
            "golden":      "🟠 Batch Golden — 100% cases with 3+ machines (overflow with anything if needed)",
        }

        batch_type = st.radio(
            "Batch Type",
            options=list(BATCH_TYPE_OPTIONS.keys()),
            format_func=lambda k: BATCH_TYPE_OPTIONS[k],
            index=0,
            key="batch_type_radio",
            help=(
                "**Standard** — Default. Fill by country quota, no machine filtering.\n\n"
                "**Low** — Only selects cases with < 3 Total Machines.\n\n"
                "**Traditional** — First fills 50% of the total quota with 3+ machine cases "
                "(by country), then completes with 1–2 machine cases.\n\n"
                "**Golden** — Selects only 3+ machine cases. Falls back to any available cases "
                "only if the quota cannot be met with 3+ cases alone (warning shown)."
            ),
        )

        with st.expander("✏️ Edit Profile", expanded=False):
            new_name = st.text_input("Profile Name", value=ep["name"], key="ep_name")
            ep["name"] = new_name
            st.markdown("**Groups** — set countries and quota for each group.")
            country_list = MCC_COUNTRIES if _rp_for_config == "MCC" else CS_COUNTRIES

            groups_to_delete = []
            for gi, grp in enumerate(ep["groups"]):
                other_used = {c for gj, grp_j in enumerate(ep["groups"])
                              if gj != gi for c in grp_j.get("countries", [])}
                available_options = [c for c in country_list if c not in other_used]
                current_selection = [c for c in grp.get("countries", []) if c in available_options]
                with st.container():
                    gc1, gc2, gc3, gc4 = st.columns([2.5, 3, 1.2, 0.5])
                    with gc1:
                        grp["name"] = st.text_input("Group Name", value=grp["name"],
                                                     key=f"gname_{gi}", label_visibility="collapsed")
                    with gc2:
                        grp["countries"] = st.multiselect(
                            "Countries", options=available_options, default=current_selection,
                            key=f"gcountries_{gi}", label_visibility="collapsed",
                            help="Countries already assigned to another group are hidden.",
                        )
                    with gc3:
                        grp["quota"] = st.number_input("Quota", min_value=1, max_value=500,
                                                        value=int(grp["quota"]), step=1,
                                                        key=f"gquota_{gi}", label_visibility="collapsed")
                    with gc4:
                        if st.button("✕", key=f"gdel_{gi}", help="Remove this group"):
                            groups_to_delete.append(gi)

            for gi in reversed(groups_to_delete):
                ep["groups"].pop(gi)
            if groups_to_delete: st.rerun()

            total_quota = sum(g["quota"] for g in ep["groups"])
            st.caption(f"Total quota across all groups: **{total_quota}** cases")

            if st.button("＋ Add Group", key="add_group_btn"):
                ep["groups"].append({"name": "New Group", "countries": [], "quota": 10}); st.rerun()

            st.markdown("---")
            save_col, saveas_col = st.columns(2)

            def _sync_ep_from_widgets(ep_dict):
                """Explicitly pull latest widget values from st.session_state into ep."""
                ep_dict["name"] = st.session_state.get("ep_name", ep_dict["name"])
                for gi, grp in enumerate(ep_dict["groups"]):
                    grp["name"]      = st.session_state.get(f"gname_{gi}",      grp["name"])
                    grp["countries"] = st.session_state.get(f"gcountries_{gi}", grp["countries"])
                    grp["quota"]     = int(st.session_state.get(f"gquota_{gi}", grp["quota"]))
                return ep_dict

            with save_col:
                if st.button("💾 Update Profile", type="primary", use_container_width=True, key="save_profile"):
                    _sync_ep_from_widgets(ep)
                    profile_to_save = {k: v for k, v in ep.items() if not k.startswith("_")}
                    old_name = ep.get("_editing_name", "")
                    if old_name != profile_to_save["name"] and old_name:
                        delete_profile(_rp_for_config, old_name)
                        if st.session_state.dist_defaults.get(_rp_for_config) == old_name:
                            set_default(_rp_for_config, profile_to_save["name"])
                    save_profile(_rp_for_config, profile_to_save)
                    ep["_editing_name"] = profile_to_save["name"]
                    st.session_state["_pending_dist_select"] = profile_to_save["name"]
                    # Persist profiles to GitHub
                    _ok, _err, _sha = save_history_to_github(_full_payload(), st.session_state.history_sha)
                    if _ok:
                        st.session_state.history_sha = _sha
                        _fetch_github_history.clear()
                    else:
                        st.warning(f"Profile saved locally but GitHub push failed: {_err}")
                    st.toast(f"✅ Profile **{profile_to_save['name']}** updated.", icon="✅")
                    st.rerun()

            with saveas_col:
                new_profile_name = st.text_input(
                    "Save as new profile name", key="saveas_name",
                    placeholder="New profile name…",
                )
                if st.button("💾 Save as New", use_container_width=True, key="saveas_btn"):
                    clean_name = st.session_state.get("saveas_name", "").strip()
                    if clean_name:
                        _sync_ep_from_widgets(ep)
                        new_p = copy.deepcopy({k: v for k, v in ep.items() if not k.startswith("_")})
                        new_p["name"] = clean_name
                        save_profile(_rp_for_config, new_p)
                        st.session_state["_pending_dist_select"] = clean_name
                        st.session_state["saveas_name"] = ""
                        new_ep = copy.deepcopy(new_p)
                        new_ep["_editing_name"] = clean_name
                        st.session_state.editor_profile = new_ep
                        # Persist profiles to GitHub
                        _ok, _err, _sha = save_history_to_github(_full_payload(), st.session_state.history_sha)
                        if _ok:
                            st.session_state.history_sha = _sha
                            _fetch_github_history.clear()
                        else:
                            st.warning(f"Profile saved locally but GitHub push failed: {_err}")
                        st.toast(f"✅ New profile **{clean_name}** created.", icon="✅")
                        st.rerun()
                    else:
                        st.warning("Enter a name for the new profile.")

        with st.expander("⬆ Import / Export Profiles (JSON)", expanded=False):
            exp_col, imp_col = st.columns(2)
            with exp_col:
                st.download_button("⬇ Export All Profiles as JSON", data=export_profiles_json(),
                                   file_name="batch_distributions.json", mime="application/json",
                                   use_container_width=True, key="export_json")
            with imp_col:
                imp_file = st.file_uploader("Import profiles JSON", type=["json"], key="import_json_file")
                if imp_file:
                    try:
                        import_profiles_json(imp_file.read().decode())
                        st.success("Profiles imported successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Import failed: {e}")
    else:
        # Toggle OFF — load default profile silently, apply Standard type
        _default_name = st.session_state.dist_defaults.get(region_code)
        ep = copy.deepcopy(get_profile(region_code, _default_name)) if _default_name else None
        if ep:
            ep["_editing_name"] = _default_name
        batch_type = "standard"


    # ──────────────────────────────────────────────
    # Confirm from Existing Prebatch File
    # ──────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📥 Confirm from Existing Prebatch File", expanded=False):
        st.markdown(
            "Use this if the app restarted after you already downloaded a Prebatch file. "
            "Upload the file to confirm it directly without re-generating."
        )
        cf_upload = st.file_uploader(
            "Upload Prebatch file (XLSX or CSV)",
            type=["xlsx", "xls", "csv"],
            key="confirm_from_file_upload",
        )
        if cf_upload is not None:
            try:
                cf_df = clean_df(read_file(cf_upload))

                # Auto-detect region from column structure
                if "Country" in cf_df.columns and "Countries" not in cf_df.columns:
                    cf_region = "CS"
                elif "Countries" in cf_df.columns:
                    cf_region = "MCC"
                else:
                    cf_region = region_code  # fall back to active region

                # Validate required columns
                if "Case ID" not in cf_df.columns:
                    st.error("File does not contain a 'Case ID' column. Please upload a valid Prebatch file.")
                else:
                    n_cases = len(cf_df)
                    st.success(
                        f"**{n_cases} cases** detected · Region auto-detected: **{cf_region}**"
                    )
                    st.dataframe(
                        cf_df[["Case ID", "Entity Name"]].head(20) if "Entity Name" in cf_df.columns
                        else cf_df[["Case ID"]].head(20),
                        use_container_width=True, hide_index=True,
                        height=min(35 * min(n_cases, 20) + 40, 380),
                    )
                    if n_cases > 20:
                        st.caption(f"Showing first 20 of {n_cases} cases.")

                    st.markdown("**Confirm this delivery:**")
                    cf_col1, cf_col2 = st.columns(2)
                    with cf_col1:
                        cf_date = st.date_input(
                            "Delivery Date", value=datetime.today(),
                            key="cf_delivery_date",
                        )
                    with cf_col2:
                        cf_suggested = next_batch_number(cf_region)
                        cf_batch_num = st.number_input(
                            "Batch Number", min_value=1,
                            value=cf_suggested, step=1,
                            key="cf_batch_number",
                            help=f"Suggested: {cf_suggested} (last confirmed + 1 for {cf_region})",
                        )

                    cf_existing = [
                        b.get("batch_number")
                        for b in st.session_state.delivery_history.get(cf_region, [])
                    ]
                    cf_is_dup = int(cf_batch_num) in cf_existing
                    if cf_is_dup:
                        st.warning(
                            f"⚠️ Batch **#{int(cf_batch_num)}** already exists for **{cf_region}**. "
                            "Tick the checkbox to replace it."
                        )
                        cf_overwrite_ok = st.checkbox(
                            f"Yes, replace Batch #{int(cf_batch_num)} for {cf_region}",
                            key="cf_overwrite_chk",
                        )
                    else:
                        cf_overwrite_ok = True

                    st.caption(
                        f"**{n_cases} cases** will be confirmed · "
                        f"Profile: **Manual confirmation from file** · Region: **{cf_region}**"
                    )

                    if st.button(
                        "✅ Confirm Delivery from File", type="primary",
                        use_container_width=True, key="cf_confirm_btn",
                        disabled=cf_is_dup and not cf_overwrite_ok,
                    ):
                        cf_entry = {
                            "batch_number": int(cf_batch_num),
                            "delivery_date": cf_date.strftime("%Y-%m-%d"),
                            "region": cf_region,
                            "profile": "Manual confirmation from file",
                            "total_cases": n_cases,
                            "cases": [
                                [str(row["Case ID"]), str(row.get("Entity Name", ""))]
                                for _, row in cf_df.iterrows()
                            ],
                        }
                        cf_batches = st.session_state.delivery_history.setdefault(cf_region, [])
                        replaced = False
                        for i, b in enumerate(cf_batches):
                            if b.get("batch_number") == int(cf_batch_num):
                                cf_batches[i] = cf_entry
                                replaced = True
                                break
                        if not replaced:
                            cf_batches.append(cf_entry)
                        st.session_state.delivery_history[cf_region] = sorted(
                            cf_batches, key=lambda b: b.get("batch_number", 0)
                        )
                        with st.spinner("Saving to GitHub..."):
                            ok, err, new_sha = save_history_to_github(
                                _full_payload(), st.session_state.history_sha
                            )
                        if ok:
                            st.session_state.history_sha = new_sha
                            _fetch_github_history.clear()
                            st.success(
                                f"🎉 Batch **#{int(cf_batch_num)}** for **{cf_region}** confirmed from file! "
                                f"**{n_cases} cases** registered on **{cf_date.strftime('%Y-%m-%d')}**."
                            )
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to save to GitHub: {err}")
                            with st.expander("🔧 GitHub Diagnostics", expanded=True):
                                for label, ok_c, detail in diagnose_github():
                                    st.markdown(f"{'✅' if ok_c else '❌'} **{label}** — {detail}")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # ──────────────────────────────────────────────
    # Delivery ID Search String Generator
    # ──────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔗 Delivery ID Search String Generator", expanded=False):
        st.markdown(
            "Upload a Pleteo export to generate **External Case ID** search strings "
            "for the QuickSuite Delivery ID search bar. Split at 100 IDs each by default. "
            "Use the **copy button** (top-right of each code block) to copy directly."
        )
        id_file = st.file_uploader("Upload Pleteo export (CSV / XLSX)", type=["csv","xlsx","xls"],
                                    key="id_gen_file")
        if id_file is not None:
            try:
                df_id = clean_df(read_file(id_file))
                col_options = list(df_id.columns)
                preferred = ["External Case ID", "external_case_id", "ExternalCaseID", "Case ID"]
                default_col = next((c for c in preferred if c in col_options), col_options[0])
                ic1, ic2 = st.columns([2, 1])
                with ic1:
                    id_col = st.selectbox("ID Column", options=col_options,
                                          index=col_options.index(default_col), key="id_col_select")
                with ic2:
                    chunk_size = st.number_input("IDs per string", min_value=10, max_value=500,
                                                  value=100, step=10, key="id_chunk_size")
                # Extract IDs — split each cell by comma, flatten, deduplicate (order-preserving)
                seen_ids: dict = {}
                for cell_val in df_id[id_col]:
                    cell_str = str(cell_val).strip()
                    if not cell_str or cell_str.lower() in ("nan", "none", ""):
                        continue
                    for sub in cell_str.split(","):
                        sub = sub.strip()
                        if sub and sub.lower() not in ("nan", "none", ""):
                            seen_ids[sub] = None   # dict preserves insertion order
                ids = list(seen_ids.keys())

                if not ids:
                    st.warning("No valid IDs found in the selected column.")
                else:
                    strings = generate_id_strings(ids, int(chunk_size))
                    total_strings = len(strings)
                    st.success(f"**{len(ids)}** IDs → **{total_strings}** string{'s' if total_strings > 1 else ''} "
                               f"(≤ {int(chunk_size)} IDs each)")
                    for si, s in enumerate(strings, 1):
                        n_ids = len(s.split(","))
                        st.markdown(
                            f"**String {si} of {total_strings}** &nbsp;·&nbsp; "
                            f"<span style='color:#F47920;font-weight:600;'>{n_ids} IDs</span>",
                            unsafe_allow_html=True,
                        )
                        st.code(s, language=None)
            except Exception as e:
                st.error(f"Error reading file: {e}")


    # ──────────────────────────────────────────────
    # Processing Area
    # ──────────────────────────────────────────────
    st.divider()
    all_uploaded = bool(qs_files and pl_file and pc_file)
    qs_df_v = pl_df_v = cc_df_v = None
    all_valid = False

    if any([qs_files, pl_file, pc_file]):
        with st.expander("File Validation", expanded=True):
            vc1, vc2, vc3 = st.columns(3)
            with vc1:
                if qs_files:
                    try:
                        merged_qs = clean_df(merge_qs_files(qs_files))
                        ok, missing = validate_file(merged_qs, QS_REQUIRED)
                        label = f"QS Delivery ID ({len(qs_files)} file{'s' if len(qs_files) > 1 else ''})"
                        if ok:
                            st.markdown(f'<span class="val-ok">✔ {label}</span> — {len(merged_qs)} rows, {len(merged_qs.columns)} columns', unsafe_allow_html=True)
                            qs_df_v, qs_ok = merged_qs, True
                        else:
                            st.markdown(f'<span class="val-err">✘ {label}</span> — missing: `{"`, `".join(sorted(missing))}`', unsafe_allow_html=True)
                            qs_df_v, qs_ok = None, False
                    except Exception as e:
                        st.markdown(f'<span class="val-err">✘ QS Delivery ID</span> — could not read file(s): {e}', unsafe_allow_html=True)
                        qs_df_v, qs_ok = None, False
                else:
                    qs_ok = False
            with vc2: pl_df_v, pl_ok = show_validation(pl_file, PL_REQUIRED, "PL Batch")
            with vc3: cc_df_v, cc_ok = show_validation(pc_file, CC_REQUIRED, "Conflict Check")
        all_valid = all_uploaded and qs_ok and pl_ok and cc_ok

    # ── Action Buttons Row ──
    if all_uploaded:
        if not all_valid:
            st.warning("One or more files failed validation. Resolve the column errors before continuing.")

        btn_col1, btn_col2 = st.columns(2)

        # ── Validate Batch ──
        with btn_col1:
            if st.button("🔍 Validate Batch", use_container_width=True, disabled=not all_valid,
                         help="Check Case IDs against previously confirmed deliveries."):
                try:
                    qs_temp = clean_df(merge_qs_files(qs_files))
                    case_ids_to_validate = [
                        str(v).strip() for v in qs_temp.get("Case ID", qs_temp.iloc[:, 0])
                        if str(v).strip() and str(v).strip().lower() != "nan"
                    ]
                    excl_ids, excl_msgs, warn_msgs, is_clean = validate_against_history(
                        case_ids_to_validate, region_code
                    )
                    st.session_state.validation_excluded = excl_ids
                    st.session_state.validation_warnings = warn_msgs
                    st.session_state.validation_clean    = is_clean
                    st.session_state.batch_validated     = True
                    st.session_state.prebatch_ready_to_confirm = False
                    st.session_state.result_df = None
                    # Store excluded messages separately for display
                    st.session_state.validation_excl_msgs = excl_msgs
                except Exception as e:
                    st.error(f"Validation error: {e}")

        # ── Generate Prebatch (only after validation) ──
        with btn_col2:
            generate_disabled = not all_valid or not st.session_state.batch_validated
            generate_help = (
                "Run Validate Batch first." if not st.session_state.batch_validated else
                "Resolve file validation errors first." if not all_valid else
                "Generate the Prebatch output file."
            )
            if st.button("▶ Generate Prebatch File", type="primary", use_container_width=True,
                         disabled=generate_disabled, help=generate_help):
                with st.spinner("Processing files..."):
                    try:
                        raw_df, unmatched, grouped, duplicates, excluded_ct = process_data(
                            qs_df_v, pl_df_v, cc_df_v, region_code
                        )
                        st.session_state.raw_df          = raw_df
                        st.session_state.unmatched       = unmatched
                        st.session_state.grouped         = grouped
                        st.session_state.duplicates      = duplicates
                        st.session_state.excluded_count  = excluded_ct
                        st.session_state.region_processed = region_code
                        st.session_state.dist_report   = None
                        st.session_state.dist_warnings = []
                        st.session_state.dist_applied  = False
                        st.session_state.prebatch_ready_to_confirm = True

                        # Always apply distribution — toggle controls type/profile choice only
                        # Toggle OFF = Standard type with default profile
                        if ep is not None:
                            profile_clean = {k: v for k, v in ep.items() if not k.startswith("_")}
                            try:
                                final_df, report, dw = apply_batch_distribution(
                                    raw_df, profile_clean, region_code, batch_type=batch_type
                                )
                                st.session_state.result_df     = final_df
                                st.session_state.dist_report   = report
                                st.session_state.dist_warnings = dw
                                st.session_state.dist_applied  = True
                            except Exception as dist_err:
                                st.warning(f"Distribution could not be applied: {dist_err}. Using full merge.")
                                st.session_state.result_df = raw_df
                        else:
                            st.session_state.result_df = raw_df

                        # Log entry — always records the final output cases
                        final = st.session_state.result_df
                        st.session_state.generation_log.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "region": region_code, "total": len(final),
                            "grouped": len(grouped), "unmatched": len(unmatched),
                            "duplicates": len(duplicates), "confirmed": False,
                            "batch_number": None, "delivery_date": None,
                            "cases": [(r["Case ID"], r.get("Entity Name","")) for _, r in final.iterrows()],
                        })
                    except Exception as e:
                        st.error(f"Error processing files: {str(e)}")
                        st.exception(e)

        # ── Validation Result Display ──
        if st.session_state.batch_validated:
            excl_ids  = st.session_state.get("validation_excluded", set())
            excl_msgs = st.session_state.get("validation_excl_msgs", [])
            warn_msgs = st.session_state.get("validation_warnings", [])

            if st.session_state.validation_clean:
                st.success(
                    "✅ **Batch validated — No repeated Case IDs found.** "
                    "All cases are new to the delivery history. You may now generate the Prebatch file."
                )
            else:
                if excl_ids:
                    st.error(
                        f"🚫 **{len(excl_ids)} case(s) automatically excluded** — "
                        f"delivered within the last 6 months. They will be removed from the output."
                    )
                    with st.expander(f"View {len(excl_msgs)} excluded case(s)", expanded=True):
                        for m in excl_msgs:
                            st.markdown(f"- {m}")

                if warn_msgs:
                    st.warning(
                        f"⚠️ **{len(warn_msgs)} case(s) previously delivered but eligible** — "
                        f"delivered more than 6 months ago. Included as relaunch/recontact."
                    )
                    with st.expander(f"View {len(warn_msgs)} eligible relaunch case(s)", expanded=False):
                        for w in warn_msgs:
                            st.markdown(f"- {w}")

                if excl_ids:
                    st.info("Generate is available — excluded cases will be automatically removed from the output.")

    else:
        missing = [n for f, n in [(qs_files,"QS Delivery ID"),(pl_file,"PL Batch"),(pc_file,"Conflict Check")] if not f]
        st.info(f"Upload the remaining file(s) to proceed: **{', '.join(missing)}**")


    # ──────────────────────────────────────────────
    # Results + Confirm Batch Delivery
    # ──────────────────────────────────────────────
    if st.session_state.result_df is not None:
        result_df = st.session_state.result_df
        raw_df    = st.session_state.raw_df if st.session_state.raw_df is not None else result_df
        rp        = st.session_state.region_processed
        dist_applied  = st.session_state.dist_applied
        dist_report   = st.session_state.dist_report
        dist_warnings = st.session_state.dist_warnings

        st.divider()

        # ── Top metrics ──
        if dist_applied and dist_report:
            batch_label = BATCH_LABELS.get(dist_report.get("batch_type", "standard"), "Batch")
            is_custom = enable_batch
            st.markdown(
                f"**Prebatch — {dist_report['profile_name']} · {batch_label}** "
                f"&nbsp;·&nbsp; {len(result_df)} of {len(raw_df)} cases selected"
            )
            for w in dist_warnings:
                st.warning(w)

            if is_custom:
                gr_cols = st.columns(len(dist_report["groups"]))
                for col, grp in zip(gr_cols, dist_report["groups"]):
                    overflow_note = " (+overflow)" if grp.get("overflow_note") else ""
                    delta_val = "On target" if grp["shortfall"] == 0 else f"-{grp['shortfall']} short"
                    col.metric(
                        label=grp["group"],
                        value=f"{grp['filled']} / {grp['quota']}",
                        delta=f"{delta_val}{overflow_note}",
                        delta_color="normal" if grp["shortfall"] == 0 else "inverse",
                    )

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Cases in Prebatch",       len(result_df))
            m2.metric("Total Available",          len(raw_df))
            m3.metric("Backlog",                  dist_report.get("total_backlog", 0))
            m4.metric("Duplicates Removed",       len(st.session_state.duplicates))
            m5.metric("Excluded (6-mo) 🚫",       st.session_state.get("excluded_count", 0))
        else:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Cases",              len(result_df))
            m2.metric("Grouped Entities",         len(st.session_state.grouped))
            m3.metric("Unmatched",                len(st.session_state.unmatched))
            m4.metric("Duplicates Removed",       len(st.session_state.duplicates))
            m5.metric("Excluded (6-mo) 🚫",       st.session_state.get("excluded_count", 0))

        # ── Diagnostics ──
        dcols = st.columns(3)
        with dcols[0]:
            if st.session_state.unmatched:
                with st.expander(f"⚠ Unmatched ({len(st.session_state.unmatched)})"):
                    st.caption("Included with blank Conflict Check fields.")
                    for c in st.session_state.unmatched: st.code(c)
        with dcols[1]:
            if st.session_state.grouped:
                with st.expander(f"ℹ Grouped ({len(st.session_state.grouped)})"):
                    st.caption("Machine Overview and Notes combined.")
                    for c in st.session_state.grouped: st.code(c)
        with dcols[2]:
            if st.session_state.duplicates:
                with st.expander(f"🚫 Duplicates Removed ({len(st.session_state.duplicates)})"):
                    st.caption("First occurrence kept.")
                    for c in st.session_state.duplicates: st.code(c)

        # ── Full merge reference (only shown when distribution was applied) ──
        if dist_applied and raw_df is not None and len(raw_df) != len(result_df):
            with st.expander(f"📋 Full merge reference ({len(raw_df)} cases before distribution)", expanded=False):
                st.caption("All cases from the file merge, before distribution filtering was applied.")
                st.dataframe(raw_df, use_container_width=True, height=300)

        # ── Backlog report (only when distribution applied) ──
        if dist_applied and dist_report and not dist_report["backlog_table"].empty:
            with st.expander("📋 Backlog Report — cases not included in this Prebatch", expanded=False):
                st.caption("Available for the next batch delivery, broken down by country.")
                st.dataframe(dist_report["backlog_table"], use_container_width=True,
                             hide_index=True,
                             height=min(35 * len(dist_report["backlog_table"]) + 40, 380))
                st.download_button(
                    "⬇ Download Backlog Report",
                    data=to_excel(dist_report["backlog_table"], sheet_name="Backlog"),
                    file_name=f"Backlog_{rp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_backlog",
                )

        # ── Prebatch preview + download ──
        st.subheader("Prebatch Preview")
        st.dataframe(result_df, use_container_width=True, height=380)
        st.download_button(
            label=f"⬇ Download Prebatch_{rp}.xlsx",
            data=to_excel(result_df),
            file_name=f"Prebatch_{rp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary", use_container_width=True,
        )

        # ════════════════════════════════════════
        # CONFIRM BATCH DELIVERY
        # ════════════════════════════════════════
        if st.session_state.prebatch_ready_to_confirm:
            st.markdown("")
            st.markdown("""
            <div class="confirm-section">
                <h3>✅ Confirm Batch Delivery</h3>
                <p>Complete the delivery details below and confirm to register this Prebatch permanently in the delivery history.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

            suggested_batch = next_batch_number(rp)
            cf1, cf2 = st.columns(2)
            with cf1:
                delivery_date = st.date_input(
                    "Delivery Date", value=datetime.today(), key="confirm_date",
                )
            with cf2:
                batch_number = st.number_input(
                    "Batch Number", min_value=1, value=suggested_batch, step=1,
                    key="confirm_batch_num",
                    help=f"Suggested: {suggested_batch} (last confirmed + 1 for {rp})",
                )

            existing_nums = [b.get("batch_number") for b in
                             st.session_state.delivery_history.get(rp, [])]
            is_duplicate = int(batch_number) in existing_nums

            if is_duplicate:
                st.warning(
                    f"⚠️ Batch **#{int(batch_number)}** already exists for **{rp}**. "
                    "Confirming will **replace** the existing entry. "
                    "Tick the checkbox below to proceed."
                )
                overwrite_confirmed = st.checkbox(
                    f"Yes, I want to replace Batch #{int(batch_number)} for {rp}",
                    value=False,
                    key="overwrite_confirm_checkbox",
                )
            else:
                overwrite_confirmed = True

            if dist_applied and dist_report:
                profile_name = dist_report.get("profile_name", "—")
                batch_label  = BATCH_LABELS.get(dist_report.get("batch_type","standard"), "Batch")
                confirm_label = f"{profile_name} · {batch_label}"
            else:
                confirm_label = "Full Prebatch (no distribution applied)"

            st.caption(
                f"**{len(result_df)} cases** will be confirmed · "
                f"Profile: **{confirm_label}** · Region: **{rp}**"
            )

            if st.button("✅ Confirm Batch Delivery", type="primary",
                         use_container_width=True, key="confirm_delivery_btn",
                         disabled=is_duplicate and not overwrite_confirmed):
                batch_entry = {
                    "batch_number": int(batch_number),
                    "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                    "region": rp, "profile": confirm_label,
                    "total_cases": len(result_df),
                    "cases": [[row["Case ID"], row.get("Entity Name", "")]
                               for _, row in result_df.iterrows()],
                }
                region_batches = st.session_state.delivery_history.setdefault(rp, [])
                replaced = False
                for i, b in enumerate(region_batches):
                    if b.get("batch_number") == int(batch_number):
                        region_batches[i] = batch_entry; replaced = True; break
                if not replaced:
                    region_batches.append(batch_entry)
                st.session_state.delivery_history[rp] = sorted(
                    region_batches, key=lambda b: b.get("batch_number", 0)
                )
                with st.spinner("Saving batch history to GitHub..."):
                    ok, err, new_sha = save_history_to_github(
                        _full_payload(), st.session_state.history_sha
                    )
                if ok:
                    st.session_state.history_sha = new_sha
                    _fetch_github_history.clear()  # bust cache so next render is fresh
                    st.session_state.prebatch_ready_to_confirm = False
                    if st.session_state.generation_log:
                        last = st.session_state.generation_log[-1]
                        last.update({"confirmed": True, "batch_number": int(batch_number),
                                     "delivery_date": delivery_date.strftime("%Y-%m-%d")})
                    st.success(
                        f"🎉 Batch **#{int(batch_number)}** for **{rp}** confirmed and saved! "
                        f"**{len(result_df)}** cases registered on **{delivery_date.strftime('%Y-%m-%d')}**."
                    )
                    st.rerun()
                else:
                    st.error(f"❌ Failed to save to GitHub: {err}")
                    st.info("Batch added to in-memory history but not persisted. "
                            "Check your GitHub secrets and retry.")
                    with st.expander("🔧 Run GitHub Diagnostics", expanded=True):
                        for label, ok_check, detail in diagnose_github():
                            st.markdown(f"{'✅' if ok_check else '❌'} **{label}** — {detail}")
                        st.markdown("---")
                        st.markdown(
                            "**Common fixes:**\n"
                            "- `GITHUB_REPO` must be `owner/repo-name`\n"
                            "- `GITHUB_BRANCH` must match your default branch\n"
                            "- `GITHUB_TOKEN` must have `repo` scope\n"
                            "- Update secrets in Streamlit Cloud → App Settings → Secrets, then reboot"
                        )


    # ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# Big Deals Processing & UI
# ──────────────────────────────────────────────
elif _app_mode == "Big Deals":
    # ── Validate + Process ──────────────────────
    bd_all_uploaded = bool(bd_qs_files and bd_pl_file)
    bd_all_valid = False
    bd_qs_df_v = bd_pl_df_v = bd_cc_df_v = None

    if bd_qs_files or bd_pl_file or bd_cc_file:
        with st.expander("File Validation", expanded=True):
            bv1, bv2, bv3 = st.columns(3)
            with bv1:
                if bd_qs_files:
                    try:
                        merged_bd_qs = clean_df(merge_qs_files(bd_qs_files))
                        ok, miss = validate_file(merged_bd_qs, QS_REQUIRED)
                        lbl = f"QS Delivery ID ({len(bd_qs_files)} file{'s' if len(bd_qs_files)>1 else ''})"
                        if ok:
                            st.markdown(f'<span class="val-ok">✔ {lbl}</span> — {len(merged_bd_qs)} rows', unsafe_allow_html=True)
                            bd_qs_df_v, bd_qs_ok = merged_bd_qs, True
                        else:
                            st.markdown(f'<span class="val-err">✘ {lbl}</span> — missing: `{"`, `".join(sorted(miss))}`', unsafe_allow_html=True)
                            bd_qs_df_v, bd_qs_ok = None, False
                    except Exception as e:
                        st.markdown(f'<span class="val-err">✘ QS</span> — {e}', unsafe_allow_html=True)
                        bd_qs_df_v, bd_qs_ok = None, False
                else:
                    bd_qs_ok = False
            with bv2:
                bd_pl_df_v, bd_pl_ok = show_validation(bd_pl_file, PL_REQUIRED, "PL Batch")
            with bv3:
                if bd_cc_file:
                    bd_cc_df_v, _ = show_validation(bd_cc_file, CC_REQUIRED, "Conflict Check")
                else:
                    st.markdown('<span style="color:#888;">— Conflict Check not uploaded (optional)</span>', unsafe_allow_html=True)
        bd_all_valid = bd_qs_ok and bd_pl_ok

    if not bd_all_uploaded:
        missing_bd = []
        if not bd_qs_files: missing_bd.append("QS Delivery ID")
        if not bd_pl_file: missing_bd.append("PL Batch")
        st.info(f"Upload the required file(s) to proceed: **{', '.join(missing_bd)}**")
    else:
        if not bd_all_valid:
            st.warning("One or more files failed validation. Resolve errors before processing.")

        if st.button("▶ Process Big Deals Cases", type="primary",
                     use_container_width=True, disabled=not bd_all_valid,
                     key="bd_process_btn"):
            with st.spinner("Processing Big Deals cases..."):
                try:
                    bd_res, bd_flagged, bd_unm, bd_grp, bd_dup = process_big_deals_data(
                        bd_qs_df_v, bd_pl_df_v,
                        bd_cc_df_v if bd_cc_file else None,
                        region_code,
                    )
                    st.session_state.bd_result_df       = bd_res
                    st.session_state.bd_flagged_cases   = bd_flagged
                    st.session_state.bd_case_mo         = {}        # reset MO cache
                    st.session_state.bd_region_processed = region_code
                    st.session_state.bd_unmatched       = bd_unm
                    st.session_state.bd_grouped         = bd_grp
                    st.session_state.bd_duplicates      = bd_dup
                    st.session_state.bd_ready_to_confirm = False
                except Exception as e:
                    st.error(f"Processing error: {e}")
                    st.exception(e)

    # ── Results ─────────────────────────────────
    if st.session_state.bd_result_df is not None:
        bd_df  = st.session_state.bd_result_df
        bd_rp  = st.session_state.bd_region_processed
        n_flag = len(st.session_state.bd_flagged_cases)
        n_ok   = len(bd_df) - n_flag

        st.divider()
        bm1, bm2, bm3, bm4 = st.columns(4)
        bm1.metric("Big Deals Cases (15+ machines)", len(bd_df))
        bm2.metric("Machine Overview ✅",  n_ok)
        bm3.metric("Flagged — MO Missing ⚠️", n_flag)
        bm4.metric("Duplicates Removed", len(st.session_state.bd_duplicates))

        if st.session_state.bd_unmatched:
            with st.expander(f"⚠ Unmatched in CC ({len(st.session_state.bd_unmatched)})"):
                for c in st.session_state.bd_unmatched: st.code(c)

        # ── Flagged Cases — per-case file uploaders ──
        if st.session_state.bd_flagged_cases:
            already_resolved = [c for c in st.session_state.bd_flagged_cases
                                 if c in st.session_state.bd_case_mo]
            still_missing    = [c for c in st.session_state.bd_flagged_cases
                                 if c not in st.session_state.bd_case_mo]

            st.markdown("")
            st.markdown(f"""
            <div class="backlog-card">
                <strong style="color:#F47920;">⚠️ {n_flag} case(s) missing Machine Overview</strong><br>
                <span style="font-size:0.85rem;color:#4A4A4A;">
                Upload the Machine Sheet and Case Event Sheet for each case below.
                Machine Overview will be generated automatically when both files are uploaded.
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

            for case_id in st.session_state.bd_flagged_cases:
                safe_key = re.sub(r'[^a-zA-Z0-9]', '_', case_id)

                # Get entity name for display
                row_match = bd_df[bd_df["Case ID"] == case_id]
                entity = row_match["Entity Name"].iloc[0] if not row_match.empty else ""
                resolved_mo = st.session_state.bd_case_mo.get(case_id, "")

                status_icon = "✅" if resolved_mo else "⚠️"
                with st.expander(
                    f"{status_icon} **{case_id}** — {entity}",
                    expanded=not bool(resolved_mo),
                ):
                    if resolved_mo:
                        st.success(f"Machine Overview generated: **{resolved_mo}**")
                        if st.button("🔄 Re-upload sheets", key=f"bd_reup_{safe_key}"):
                            st.session_state.bd_case_mo.pop(case_id, None)
                            st.rerun()
                    else:
                        # How many Case IDs are in this entity (comma-separated)
                        n_sub_cases = len([c for c in case_id.split(",") if c.strip()])
                        multi_hint = (
                            f" Upload one file per sub-case ({n_sub_cases} expected)."
                            if n_sub_cases > 1 else ""
                        )
                        uc1, uc2 = st.columns(2)
                        with uc1:
                            mach_files = st.file_uploader(
                                "Machine Sheet(s)",
                                type=["csv","xlsx","xls"],
                                accept_multiple_files=True,
                                key=f"bd_mach_{safe_key}",
                                help=f"Exported Machines file(s) for this case.{multi_hint} Multiple files are merged before processing.",
                            )
                        with uc2:
                            evt_files = st.file_uploader(
                                "Case Event Sheet(s)",
                                type=["csv","xlsx","xls"],
                                accept_multiple_files=True,
                                key=f"bd_evt_{safe_key}",
                                help=f"Exported Case Events file(s) for this case.{multi_hint} Multiple files are merged before processing.",
                            )
                        if n_sub_cases > 1:
                            st.caption(
                                f"ℹ️ This entity has **{n_sub_cases} sub-cases** — "
                                f"upload one Machine Sheet and one Event Sheet per sub-case. "
                                f"All files will be merged into a single Machine Overview."
                            )
                        if mach_files and evt_files:
                            with st.spinner(f"Generating Machine Overview for {case_id}…"):
                                try:
                                    # Merge all machine files into one DataFrame
                                    mach_frames = [read_file(f) for f in mach_files]
                                    mach_df = pd.concat(mach_frames, ignore_index=True) if len(mach_frames) > 1 else mach_frames[0]

                                    # Merge all event files into one DataFrame
                                    evt_frames = [read_file(f) for f in evt_files]
                                    evt_df = pd.concat(evt_frames, ignore_index=True) if len(evt_frames) > 1 else evt_frames[0]

                                    mo = generate_machine_overview_from_files(mach_df, evt_df)
                                    if mo:
                                        st.session_state.bd_case_mo[case_id] = mo
                                        st.success(f"Generated: **{mo}**")
                                        st.rerun()
                                    else:
                                        st.warning(
                                            "No Approved machines found across the uploaded files. "
                                            "Check that the Approval Status column contains 'Approved' entries."
                                        )
                                except Exception as e:
                                    st.error(f"Error processing sheets: {e}")

        # ── Build final DataFrame with MOs applied ──
        bd_final = bd_df.copy()
        for case_id, mo in st.session_state.bd_case_mo.items():
            bd_final.loc[bd_final["Case ID"] == case_id, "Machine Overview"] = mo

        # Remaining unfilled MO
        still_unfilled = bd_final[bd_final["Machine Overview"].str.strip() == ""]["Case ID"].tolist()
        if still_unfilled:
            st.caption(
                f"⚠️ {len(still_unfilled)} case(s) still have no Machine Overview and will be "
                "included in the output with an empty cell."
            )

        # ── Preview ─────────────────────────────────
        st.subheader("📋 Big Deals Prebatch Preview")
        # Highlight rows with missing MO
        def _highlight_missing(row):
            if not str(row.get("Machine Overview", "")).strip():
                return ["background-color: #FFF3CD; color: #1A1A1A;" for _ in row]
            return ["" for _ in row]
        st.dataframe(
            bd_final.style.apply(_highlight_missing, axis=1),
            use_container_width=True, height=400,
        )

        # ── Generate + Download ─────────────────────
        st.download_button(
            label=f"⬇ Download Big Deals Prebatch_{bd_rp}.xlsx",
            data=to_excel(bd_final),
            file_name=f"BigDeals_Prebatch_{bd_rp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary", use_container_width=True, key="bd_download_btn",
        )
        st.session_state.bd_ready_to_confirm = True

        # ── Confirm Delivery ─────────────────────────
        if st.session_state.bd_ready_to_confirm:
            st.markdown("")
            st.markdown("""
            <div class="confirm-section">
                <h3>✅ Confirm Big Deals Delivery</h3>
                <p>Register this Big Deals batch permanently in the delivery history.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

            bd_suggested = next_batch_number(f"BigDeals_{bd_rp}")
            bdc1, bdc2 = st.columns(2)
            with bdc1:
                bd_delivery_date = st.date_input(
                    "Delivery Date", value=datetime.today(), key="bd_confirm_date")
            with bdc2:
                bd_batch_number = st.number_input(
                    "Batch Number", min_value=1, value=bd_suggested, step=1,
                    key="bd_confirm_batch_num",
                    help=f"Suggested: {bd_suggested} (last Big Deals confirmed + 1 for {bd_rp})",
                )

            _bd_hist_key = f"BigDeals_{bd_rp}"
            bd_existing_nums = [b.get("batch_number") for b in
                                 st.session_state.delivery_history.get(_bd_hist_key, [])]
            bd_is_dup = int(bd_batch_number) in bd_existing_nums
            if bd_is_dup:
                st.warning(
                    f"⚠️ Big Deals Batch **#{int(bd_batch_number)}** already exists for **{bd_rp}**. "
                    "Tick the checkbox to replace it."
                )
                bd_overwrite_ok = st.checkbox(
                    f"Yes, replace Big Deals Batch #{int(bd_batch_number)} for {bd_rp}",
                    key="bd_overwrite_checkbox",
                )
            else:
                bd_overwrite_ok = True

            st.caption(
                f"**{len(bd_final)} cases** will be confirmed · "
                f"Stored as: **BigDeals_{bd_rp}** · Batch **#{int(bd_batch_number)}**"
            )

            if st.button("✅ Confirm Big Deals Delivery", type="primary",
                         use_container_width=True, key="bd_confirm_btn",
                         disabled=bd_is_dup and not bd_overwrite_ok):
                bd_entry = {
                    "batch_number": int(bd_batch_number),
                    "delivery_date": bd_delivery_date.strftime("%Y-%m-%d"),
                    "region": bd_rp, "profile": "Big Deals (15+ machines)",
                    "total_cases": len(bd_final),
                    "cases": [[r["Case ID"], r.get("Entity Name","")]
                               for _, r in bd_final.iterrows()],
                }
                region_batches = st.session_state.delivery_history.setdefault(_bd_hist_key, [])
                replaced = False
                for i, b in enumerate(region_batches):
                    if b.get("batch_number") == int(bd_batch_number):
                        region_batches[i] = bd_entry; replaced = True; break
                if not replaced:
                    region_batches.append(bd_entry)
                st.session_state.delivery_history[_bd_hist_key] = sorted(
                    region_batches, key=lambda b: b.get("batch_number", 0)
                )
                with st.spinner("Saving to GitHub..."):
                    ok, err, new_sha = save_history_to_github(
                        _full_payload(), st.session_state.history_sha
                    )
                if ok:
                    st.session_state.history_sha = new_sha
                    _fetch_github_history.clear()  # bust cache so next render is fresh
                    st.session_state.bd_ready_to_confirm = False
                    st.success(
                        f"🎉 Big Deals Batch **#{int(bd_batch_number)}** for **{bd_rp}** confirmed "
                        f"under **BigDeals_{bd_rp}**! "
                        f"**{len(bd_final)} cases** registered on **{bd_delivery_date.strftime('%Y-%m-%d')}**."
                    )
                    st.rerun()
                else:
                    st.error(f"❌ Failed to save to GitHub: {err}")
                    with st.expander("🔧 Run GitHub Diagnostics", expanded=True):
                        for label, ok_c, detail in diagnose_github():
                            st.markdown(f"{'✅' if ok_c else '❌'} **{label}** — {detail}")
# Footer
# ──────────────────────────────────────────────
st.markdown("""
<div class="rx-footer">
    <p class="rx-conf">CONFIDENTIAL — FOR INTERNAL USE ONLY</p>
    <p>This tool and all data processed through it are the proprietary property of Ruvixx
    and its clients. Unauthorized access, distribution, or reproduction is strictly prohibited.</p>
    <p>&copy; 2026 Ruvixx &mdash; Case Investigation Operations &middot; Trimble SketchUp License Compliance</p>
</div>
""", unsafe_allow_html=True)
