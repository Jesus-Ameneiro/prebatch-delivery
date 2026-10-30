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
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

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

def _secret(name, default=""):
    """Read one Streamlit secret as a stripped string. Never raises: a missing secrets
    file, a missing key or a stray trailing space must not crash the page."""
    try:
        val = st.secrets.get(name, default)
    except Exception:
        return str(default)
    return str(default) if val is None else str(val).strip()

def _gh_headers():
    token = _secret("GITHUB_TOKEN")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

def _gh_config():
    """Return (repo, path, branch) from secrets."""
    repo   = _secret("GITHUB_REPO")
    path   = _secret("HISTORY_FILE_PATH", HISTORY_FILE) or HISTORY_FILE
    branch = _secret("GITHUB_BRANCH", "main") or "main"
    return repo, path, branch

def github_config_problem():
    """Plain-language explanation if the GitHub secrets are unusable, otherwise None.
    Checked BEFORE any request so a missing secret is reported as what it is, not as a
    confusing GitHub '404 Not Found'."""
    token = _secret("GITHUB_TOKEN")
    repo  = _secret("GITHUB_REPO")
    missing = []
    if len(token) <= 10:
        missing.append("GITHUB_TOKEN")
    if not repo:
        missing.append("GITHUB_REPO")
    if missing:
        return (
            "GitHub storage is not configured: " + " and ".join(missing)
            + (" is" if len(missing) == 1 else " are")
            + " empty or missing in this app's Streamlit secrets, so the delivery history "
              "can be neither read nor saved. Add the secrets in the app's Settings → Secrets "
              "and reboot the app."
        )
    if repo.count("/") != 1 or repo.startswith("/") or repo.endswith("/"):
        return f"GITHUB_REPO is `{repo}` but must look like `owner/repo-name`."
    return None

def _gh_status(url):
    """HTTP status of a GET against the GitHub API, or None if the request itself failed."""
    try:
        req = urllib.request.Request(url, headers=_gh_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None

_GH_HINTS = {
    401: "The token was rejected (expired, revoked or mistyped).",
    403: "The token lacks permission for this repo, or GitHub is rate-limiting the request.",
    404: "GitHub cannot find the repo, branch or file (it typically also answers 404 for a private repo the token cannot see).",
    409: "The history file changed on GitHub after this page loaded it. Press 🔄 to reload, then retry.",
    422: "GitHub rejected the update. This usually means the file already exists and this session does not hold its latest version. Press 🔄 to reload, then retry.",
}

def _gh_file_url():
    repo, path, _ = _gh_config()
    return f"https://api.github.com/repos/{repo}/contents/{path}", path

def load_history_from_github():
    """Fetch batch_history.json from GitHub. Returns (history_dict, sha, error_msg)."""
    problem = github_config_problem()
    if problem:
        return None, None, problem
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
            # A 404 means "no history file yet" ONLY when the repo and branch really exist.
            # Otherwise (wrong repo, wrong branch, token cannot see a private repo) it is a
            # configuration error and must NOT masquerade as an empty history.
            repo_ok   = _gh_status(f"https://api.github.com/repos/{repo}") == 200
            branch_ok = repo_ok and _gh_status(
                f"https://api.github.com/repos/{repo}/branches/{urllib.parse.quote(branch, safe='/')}"
            ) == 200
            if repo_ok and branch_ok:
                return {"MCC": [], "CS": []}, None, None      # genuinely a fresh start
            return None, None, (
                f"GitHub returned 404 for `{repo}` (branch `{branch}`, file `{path}`) and the "
                f"repo/branch could not be confirmed with this token. {_GH_HINTS[404]}"
            )
        body = ""
        try: body = e.read().decode()
        except Exception: pass
        return None, None, f"GitHub HTTP {e.code} — {_GH_HINTS.get(e.code, '')} {body}".strip()
    except Exception as e:
        return None, None, str(e)

def save_history_to_github(history_dict, sha):
    """Push updated batch_history.json to GitHub. Returns (ok, error_msg, new_sha)."""
    problem = github_config_problem()
    if problem:
        return False, problem, sha
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
        return False, f"GitHub HTTP {e.code} — {_GH_HINTS.get(e.code, '')} {body}".strip(), sha
    except Exception as e:
        return False, str(e), sha


def diagnose_github() -> list:
    """
    Run a sequence of checks against GitHub and return a list of
    (label, ok: bool, detail: str) tuples.
    """
    results = []
    repo, path, branch = _gh_config()
    token = _secret("GITHUB_TOKEN")

    # 0 — which secrets can the running app actually see? (names only, never values)
    try:
        visible = sorted(str(k) for k in st.secrets.keys())
    except Exception:
        visible = []
    if not visible:
        results.append(("Secrets visible to the app", False,
                        "none — Streamlit is passing no secrets to this app instance. Possible causes: "
                        "the Secrets box of THIS app is empty, you are on a different app instance than "
                        "the one you edited, or the app was not rebooted after saving."))
    elif {"GITHUB_TOKEN", "GITHUB_REPO"} <= set(visible):
        results.append(("Secrets visible to the app", True, ", ".join(f"`{n}`" for n in visible)))
    else:
        results.append(("Secrets visible to the app", False,
                        ", ".join(f"`{n}`" for n in visible)
                        + " — GITHUB_TOKEN and/or GITHUB_REPO are not among these top-level names. "
                          "Keys placed under a [section] header are nested and are not found by the app."))

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
        "editor_rev": 0,     # bumped whenever the profile editor must rebuild its widgets
        "dist_nav": 0,       # bumped to force the profile dropdown onto a given profile
        "manual_added_ids": [],   # backlog cases the user added by hand in the preview
        "manual_rev": 0,          # bumped to clear the "cases to add" picker after each add
        "dist_inputs": None,      # profile / batch type / TWD flags used by the last Generate
        "comp_inputs": None,      # TWD flags + whether the Pleteo file had Tags (for the composition cards)
        # Delivery history (persistent via GitHub)
        "delivery_history": {"MCC": [], "CS": []},
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
        "sub_id_deduped": [],
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
    """Fetch batch_history.json. Cached 5 min, shared across sessions.
    A failure RAISES instead of returning: Streamlit does not cache exceptions, so a failed
    load is retried on the next run instead of being remembered for 5 minutes."""
    history, sha, err = load_history_from_github()
    if err:
        raise RuntimeError(err)
    return history, sha


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
    data = history or {"MCC": [], "CS": []}
    # Restore distribution profiles if stored (absent in older files → keep defaults)
    if "dist_profiles" in data:
        st.session_state.dist_profiles = data["dist_profiles"]
    if "dist_defaults" in data:
        st.session_state.dist_defaults = data["dist_defaults"]

    # Strip profile keys before storing as delivery_history
    delivery_keys = ("MCC", "CS")
    st.session_state.delivery_history = {k: data.get(k, []) for k in delivery_keys}
    st.session_state.history_sha = sha
    st.session_state.history_load_ok = True
    st.session_state.history_load_msg = (
        f"✅ Batch history loaded — "
        f"MCC: {len(st.session_state.delivery_history.get('MCC', []))} batch(es) · "
        f"CS: {len(st.session_state.delivery_history.get('CS', []))} batch(es)"
    )


# Run on every render — cache keeps it fast, TTL keeps it fresh
try:
    _hist_data, _hist_sha = _fetch_github_history()
    _hist_err = None
except Exception as _hist_exc:
    _hist_data, _hist_sha, _hist_err = None, None, str(_hist_exc)
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
            st.caption(f"{reg}: History unavailable: GitHub is not connected (see the warning at the top)." if not st.session_state.history_load_ok else f"{reg}: No deliveries confirmed yet.")

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
    st.session_state._last_region = region_code

st.divider()

# ── File Uploaders (mode-specific) ──
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

def normalize_sub_ids(case_id_raw: str) -> tuple:
    """
    Deduplicate sub-IDs within a comma-separated Case ID, preserving
    first-occurrence order.

    "4456084#1,4456084#1,4456084#1" → ("4456084#1", True)
    "595983#1,595983#1,4610281#1"   → ("595983#1,4610281#1", True)
    "4543813#1,4455925#1"           → ("4543813#1,4455925#1", False)

    Returns (cleaned_string, was_changed).
    """
    parts  = [s.strip() for s in case_id_raw.split(",") if s.strip()]
    deduped = list(dict.fromkeys(parts))
    cleaned = ",".join(deduped)
    return cleaned, (cleaned != case_id_raw.replace(" ", ""))


def normalize_case_id(case_id: str) -> str:
    """Deduplicate, then sort sub-IDs alphabetically for order-independent comparison."""
    parts = sorted(set(c.strip() for c in case_id.split(",") if c.strip()))
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
    Check Case IDs against delivery history.

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
    for hist_key in [region]:
        for batch in st.session_state.delivery_history.get(hist_key, []):
            b_num  = batch.get("batch_number", "?")
            b_date = batch.get("delivery_date", "?")
            batch_type = "Standard"
            for case in batch.get("cases", []):
                raw_cid = case[0] if isinstance(case, (list, tuple)) else case.get("case_id", "")
                norm    = normalize_case_id(raw_cid)
                # Keep the most recent delivery if a case appears in multiple batches
                if norm not in delivered:
                    delivered[norm] = (b_num, b_date, batch_type)
                else:
                    existing_date = delivered[norm][1]
                    if b_date > existing_date:
                        delivered[norm] = (b_num, b_date, batch_type)

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
    sub_id_deduped = []   # cases where sub-IDs were silently cleaned

    for idx, (_, qs_row) in enumerate(qs_df.iterrows()):
        case_id_raw = str(qs_row.get("Case ID","")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue

        # Deduplicate sub-IDs before any further processing
        case_id_raw, was_deduped = normalize_sub_ids(case_id_raw)
        if was_deduped:
            sub_id_deduped.append(case_id_raw)

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

        # ── Machine count fields ──
        # When sub-IDs were deduped the QS totals are inflated.
        # CC is the authoritative source; use it when available and it differs from QS.
        qs_total    = safe_get(qs_row, "Total Machines")
        qs_action   = safe_get(qs_row, "Actionable Machines")
        qs_diff     = safe_get(qs_row, "[CFa]-Difference")
        qs_ids      = safe_get(qs_row, "Approved Machines")

        cc_total    = safe_get(cc_row, "# All Time Machines")   if cc_row is not None else ""
        cc_action   = safe_get(cc_row, "# Actionable Machines") if cc_row is not None else ""
        cc_ids      = safe_get(cc_row, "Actionable Machine IDs") if cc_row is not None else ""

        if cc_total and cc_total != qs_total:
            # CC overrides QS — recalculate difference
            out_total  = cc_total
            out_action = cc_action if cc_action else qs_action
            out_ids    = cc_ids    if cc_ids    else qs_ids
            try:
                out_diff = str(int(float(out_total)) - int(float(out_action)))
            except Exception:
                out_diff = qs_diff
        else:
            out_total  = qs_total
            out_action = qs_action
            out_diff   = qs_diff
            out_ids    = qs_ids

        base = {
            "Date Added to This Sheet": "", "Is Multi-National": safe_get(cc_row, "Is Multi National"),
            "Machine Overview": machine_overview, "Investigation Notes": investigation_notes,
            "Case ID": case_id_raw, "Company Name": safe_get(cc_row, "Company Name"),
            "Entity Name": entity_name, "Cylynt Organization Name": safe_get(cc_row, "Cylynt Organization Name"),
            "Industry": safe_get(cc_row, "Industry"), "Case Tier": safe_get(qs_row, "Case Tier"),
            "Case Category": safe_get(qs_row, "[Cfa]-Category"),
            "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
            "# All Time Machines": out_total,
            "# Actionable Machines": out_action,
            "# Difference": out_diff,
            "Actionable Machine IDs": out_ids,
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
    return result_df, unmatched_cases, grouped_cases, duplicate_cases, excluded_count, sub_id_deduped


# ──────────────────────────────────────────────
# Batch Distribution — Core Algorithm
# ──────────────────────────────────────────────

def case_matches_group(country_val: str, group_countries: list) -> bool:
    cv = str(country_val).lower()
    return any(gc.lower() in cv for gc in group_countries)

def apply_batch_distribution(df, distribution, region_code, batch_type="standard",
                             twd_ids=None, manual_ids=None):
    """
    batch_type:
        "standard"    — fill by country availability, no machine filtering
        "low"         — <3 machines only, fill by country, overflow any unused <3
        "golden"      — 3+ first, overflow unused 3+, then fill remainder with anything; warn if <3 used
        "traditional" — 50% global 3+ by country, then 50% <3 by country, then overflow anything

    Optional case criteria stored in the profile. They never add cases or groups; they only steer
    which cases fill each country group's quota while the list is generated:
        distribution["twd"]     = {"enabled", "percent"}          cases listed in `twd_ids`
                                  (Pleteo tag "Relaunch"): hard cap, % of the batch, split across
                                  the country groups in proportion to their quotas.
        distribution["vintage"] = {"enabled", "percent", "year"}  Last Event year <= year:
                                  a target, % of the batch, picked first; a group's unused slots
                                  roll over to groups that have more vintage cases.
    manual_ids: Case IDs the user chose to add after seeing the preview. They join the selection
    after the normal pass, ignore the TWD cap, and can never take the batch past its size.
    """
    country_col = "Countries" if region_code == "MCC" else "Country"
    df_work = df.copy().reset_index(drop=True)
    df_work["_m"] = pd.to_numeric(df_work["# All Time Machines"], errors="coerce").fillna(0)

    groups       = distribution["groups"]
    quotas       = [g["quota"] for g in groups]
    total_quota  = sum(quotas)
    n_groups     = len(groups)

    # ── Case criteria: flags, batch-level numbers, per-group allowances ──
    cfg_t, cfg_v   = distribution.get("twd") or {}, distribution.get("vintage") or {}
    twd_on, vin_on = bool(cfg_t.get("enabled")), bool(cfg_v.get("enabled"))
    cutoff   = int(cfg_v.get("year") or 2024)
    twd_set  = {str(x) for x in (twd_ids or ())}
    case_ids = df_work["Case ID"].astype(str).tolist()
    years    = ([_year_of(v) for v in df_work["Last Event"]]
                if "Last Event" in df_work.columns else [None] * len(df_work))
    is_twd   = [twd_on and cid in twd_set for cid in case_ids]
    is_vint  = [vin_on and (y is not None) and y <= cutoff for y in years]

    def _pct(cfg, default):
        try:
            return max(0.0, min(100.0, float(cfg.get("percent", default))))
        except (TypeError, ValueError):
            return float(default)
    twd_pct, vin_pct = _pct(cfg_t, 20.0), _pct(cfg_v, 10.0)
    quota_w = [Decimal(int(q)) for q in quotas]
    twd_cap_total = vin_target_total = 0
    twd_caps, vin_targets = [0] * n_groups, [0] * n_groups
    if total_quota > 0:
        if twd_on:      # a maximum rounds DOWN
            twd_cap_total = int((Decimal(total_quota) * _dec(twd_pct) / 100).to_integral_value(rounding=ROUND_FLOOR))
            twd_caps = _largest_remainder(twd_cap_total, quota_w)
        if vin_on:      # a target rounds to the nearest case
            vin_target_total = int((Decimal(total_quota) * _dec(vin_pct) / 100).to_integral_value(rounding=ROUND_HALF_UP))
            vin_targets = _largest_remainder(vin_target_total, quota_w)

    warnings         = []
    group_selections = [[] for _ in range(n_groups)]
    used             = set()
    twd_count        = [0] * n_groups
    vin_count        = [0] * n_groups
    manual_set       = set()

    def _group_of(i):
        """First group whose countries match the case (None when it belongs to no group)."""
        for gi_, grp_ in enumerate(groups):
            if case_matches_group(df_work.loc[i, country_col], grp_["countries"]):
                return gi_
        return None

    def _mark(gi, i):
        group_selections[gi].append(i)
        used.add(i)
        if is_twd[i]:
            twd_count[gi] += 1
        if is_vint[i]:
            vin_count[gi] += 1

    def take(gi, candidates, n):
        """Pick up to n unused candidates for group gi, in the order given. Vintage cases go first
        until the group's vintage target is met; TWD cases are skipped once its TWD cap is reached."""
        got = 0
        if n <= 0:
            return got
        if vin_on:
            for i in candidates:
                if got >= n or vin_count[gi] >= vin_targets[gi]:
                    break
                if i in used or not is_vint[i]:
                    continue
                if is_twd[i] and twd_count[gi] >= twd_caps[gi]:
                    continue
                _mark(gi, i)
                got += 1
        for i in candidates:
            if got >= n:
                break
            if i in used:
                continue
            if is_twd[i] and twd_count[gi] >= twd_caps[gi]:
                continue
            _mark(gi, i)
            got += 1
        return got

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
            remaining = cap - len(group_selections[gi])
            if remaining <= 0:
                continue
            take(gi, country_pool(source_idx, group), remaining)

    # ── Overflow: fill shortfalls from any eligible pool, from other groups' countries ──
    def overflow_fill(eligible_idx):
        """After main passes, fill any remaining shortfalls from eligible_idx."""
        for gi, group in enumerate(groups):
            shortfall = group["quota"] - len(group_selections[gi])
            if shortfall > 0:
                take(gi, eligible_idx, shortfall)     # borrows regardless of country

    # ── Vintage roll-over: a group short of vintage cases passes its unused slots on ──
    if vin_on and vin_target_total > 0:
        if batch_type == "low":
            vint_pool = [i for i in df_work.index if df_work.loc[i, "_m"] < 3]
        elif batch_type == "golden":
            vint_pool = [i for i in df_work.index if df_work.loc[i, "_m"] >= 3]
        else:
            vint_pool = list(df_work.index)
        n_free, n_twd = [0] * n_groups, [0] * n_groups
        for i in vint_pool:
            if not is_vint[i]:
                continue
            g_ = _group_of(i)
            if g_ is None:
                continue
            if is_twd[i]:
                n_twd[g_] += 1
            else:
                n_free[g_] += 1
        avail = [min(n_free[g_] + min(n_twd[g_], twd_caps[g_]), quotas[g_]) for g_ in range(n_groups)]
        eff   = [min(vin_targets[g_], avail[g_]) for g_ in range(n_groups)]
        unmet = vin_target_total - sum(eff)
        for g_ in range(n_groups):
            if unmet <= 0:
                break
            add = min(avail[g_] - eff[g_], unmet)
            eff[g_] += add
            unmet   -= add
        vin_targets = eff

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
            before = set(used)
            for gi, group in enumerate(groups):
                take(gi, any_remaining, group["quota"] - len(group_selections[gi]))
            if any(df_work.loc[i, "_m"] < 3 for i in used - before):
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
            premium_selected += take(gi, country_pool(premium_idx, group),
                                     min(group["quota"], premium_target - premium_selected))

        # Pass 2 — <3 cases, fill remaining per-group quota
        fill_groups(under3_idx)

        # Pass 3 — overflow: any unused cases for remaining shortfalls
        all_idx = list(df_work.index)
        overflow_fill(all_idx)

    # ────────────────────────────────────────────
    # Cases the user added by hand from the backlog (after the normal pass)
    # ────────────────────────────────────────────
    manual_added = []
    if manual_ids:
        by_cid = {}
        for i in df_work.index:
            if i not in used:
                by_cid.setdefault(case_ids[i], i)
        for cid in manual_ids:
            if sum(len(s) for s in group_selections) >= total_quota:
                break                                  # never past the batch size
            i = by_cid.get(str(cid))
            if i is None or i in used:
                continue
            g_ = _group_of(i)
            if g_ is None:
                continue
            _mark(g_, i)
            manual_set.add(i)
            manual_added.append(case_ids[i])

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
            "added":    sum(1 for i in group_selections[gi] if i in manual_set),
        })
        if overflow_cases:
            warnings.append(
                f"⚠️ Group **{group['name']}**: {len(overflow_cases)} case(s) were filled "
                f"with overflow from other country groups to meet the quota."
            )

    total_selected = sum(len(s) for s in group_selections)
    all_selected_idx = sorted(set(idx for sel in group_selections for idx in sel))
    selected_set = set(all_selected_idx)

    # Backlog cases the user could still add by hand (only for the criteria that are switched on)
    cand_rows = []
    if twd_on or vin_on:
        for i in df_work.index:
            if i in selected_set or not (is_twd[i] or is_vint[i]):
                continue
            g_ = _group_of(i)
            if g_ is None:
                continue
            cand_rows.append({
                "Case ID": case_ids[i],
                "Entity Name": df_work.at[i, "Entity Name"] if "Entity Name" in df_work.columns else "",
                "Country": df_work.at[i, country_col],
                "# All Time Machines": df_work.at[i, "# All Time Machines"],
                "Last Event": df_work.at[i, "Last Event"] if "Last Event" in df_work.columns else "",
                "TWD": "Yes" if is_twd[i] else "",
                "Vintage": "Yes" if is_vint[i] else "",
                "Group": groups[g_]["name"], "_g": g_, "_m": float(df_work.at[i, "_m"]),
            })
    cand_rows.sort(key=lambda r: (r["_g"], -r["_m"]))
    manual_candidates = pd.DataFrame(
        [{k: v for k, v in r.items() if not k.startswith("_")} for r in cand_rows],
        columns=["Case ID", "Entity Name", "Country", "# All Time Machines", "Last Event", "TWD", "Vintage", "Group"])

    # Total quota warning
    if total_selected < total_quota:
        msg = (f"🚨 **Total batch quota not met:** {total_selected} of {total_quota} cases selected. "
               f"Not enough cases available in the uploaded file to complete the full batch.")
        if cand_rows:
            parts = []
            n_t = sum(1 for r in cand_rows if r["TWD"])
            n_v = sum(1 for r in cand_rows if r["Vintage"])
            if n_t: parts.append(f"{n_t} TWD")
            if n_v: parts.append(f"{n_v} Vintage")
            msg += f" The backlog still holds {' and '.join(parts)} case(s) that you can add manually in the preview."
        warnings.append(msg)

    twd_selected, vin_selected = sum(twd_count), sum(vin_count)
    if vin_on and vin_target_total > 0 and vin_selected < vin_target_total:
        warnings.append(
            f"⚠️ **Vintage target not met:** {vin_selected} of {vin_target_total} vintage case(s) "
            f"(last event in or before {cutoff}) could be included. Not enough eligible vintage cases were available."
        )

    # ── Build output DataFrame ──
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
        "mode": distribution.get("mode", "fixed"),
        "total": distribution.get("total"),
        "criteria": {
            "twd": {"enabled": twd_on, "percent": twd_pct, "cap_total": twd_cap_total,
                    "selected": twd_selected, "caps": list(twd_caps), "by_group": list(twd_count)},
            "vintage": {"enabled": vin_on, "percent": vin_pct, "year": cutoff,
                        "target_total": vin_target_total, "selected": vin_selected,
                        "targets": list(vin_targets), "by_group": list(vin_count)},
        },
        "manual_added": manual_added,
        "manual_candidates": manual_candidates,
        "shortfall": max(total_quota - total_selected, 0),
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

# ── Fixed vs Percentage group distribution: helpers ──────────────────────
def _largest_remainder(total, weights):
    """Split `total` into whole numbers proportional to `weights` (Decimals, sum > 0).
    Every share is rounded down, then the leftover units go to the biggest fractional
    parts (ties -> earlier position), so the result always adds up to `total`."""
    wsum = sum(weights)
    raw  = [Decimal(total) * w / wsum for w in weights]
    base = [int(r.to_integral_value(rounding=ROUND_FLOOR)) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: (-(raw[i] - base[i]), i))[: total - sum(base)]:
        base[i] += 1
    return base

def _dec(x):
    """Widget number -> exact Decimal with at most 2 decimals."""
    try:
        return Decimal(str(round(float(x), 2)))
    except Exception:
        return Decimal(0)

def percent_problem(percents):
    """None when the percentages are valid (none negative, adding up to exactly 100), else a message."""
    vals = [_dec(x) for x in percents]
    if not vals:
        return "Add at least one group."
    if any(v < 0 for v in vals):
        return "Percentages cannot be negative."
    s = sum(vals)
    if s != Decimal(100):
        return f"Percentages add up to {s.normalize():f}%, they must add up to exactly 100%."
    return None

def percents_from_quotas(quotas):
    """Each quota's share as a percentage with 2 decimals, adding up to exactly 100.00."""
    q = [Decimal(int(x)) for x in quotas]
    if not q:
        return []
    if sum(q) == 0:
        q = [Decimal(1)] * len(q)
    return [float(Decimal(u) / Decimal(100)) for u in _largest_remainder(10000, q)]

def quotas_from_percent(total, percents, strict=True):
    """Whole-case quotas for `total` cases. strict=True requires the percentages to add up to 100;
    strict=False (used only when converting modes) normalises whatever is there."""
    vals = [_dec(x) for x in percents]
    if strict:
        msg = percent_problem(percents)
        if msg:
            raise ValueError(msg)
    elif sum(vals) <= 0:
        vals = [Decimal(1)] * len(vals)
    return _largest_remainder(int(total), vals)

def _year_of(v):
    """Year of a Last Event value (ISO text first, then a general parse); None when unreadable."""
    s = str(v).strip()
    m = re.match(r"(\d{4})-\d{1,2}-\d{1,2}", s)
    if m:
        return int(m.group(1))
    try:
        ts = pd.to_datetime(s, errors="coerce")
        return None if pd.isna(ts) else int(ts.year)
    except Exception:
        return None

def compute_twd_ids(pl_df, case_ids):
    """Case IDs (as they appear in the Prebatch) carrying the Pleteo tag "Relaunch": the exact tag,
    any capitalization. For a grouped case, any of its sub-IDs counts."""
    if pl_df is None or "Tags" not in pl_df.columns or "External Case ID" not in pl_df.columns:
        return set()
    relaunch = set()
    for ext, tags in zip(pl_df["External Case ID"], pl_df["Tags"]):
        toks = {t.strip().lower() for t in re.split(r"[;,|]", str(tags)) if t.strip()}
        if "relaunch" in toks:
            relaunch.add(str(ext).strip())
    return {str(cid) for cid in case_ids
            if any(s.strip() in relaunch for s in str(cid).split(","))}

def batch_composition(df, twd_ids, tags_ok, vintage_year):
    """Counts for the batch in the preview. HIGH = 3 or more total machines, LOW = fewer than 3
    (so HIGH + LOW is the whole batch). TWD (Relaunch tag) and Vintage (last event in or before
    the cutoff year) are flags that can overlap. TWD is None when the Pleteo file had no Tags."""
    n = len(df)
    if n and "# All Time Machines" in df.columns:
        m = pd.to_numeric(df["# All Time Machines"], errors="coerce").fillna(0)
    else:
        m = pd.Series([0.0] * n)                       # missing column: nothing counts as HIGH
    high = int((m >= 3).sum())
    ids = df["Case ID"].astype(str) if (n and "Case ID" in df.columns) else []
    twd = sum(1 for cid in ids if cid in twd_ids) if tags_ok else None
    years = [_year_of(v) for v in df["Last Event"]] if ("Last Event" in df.columns and n) else []
    return {"n": n, "high": high, "low": n - high, "twd": twd,
            "vintage": sum(1 for y in years if y is not None and y <= vintage_year),
            "vintage_year": vintage_year}

def country_representation(df, profile, country_col):
    """Target vs actual cases per profile group, using each case's OWN country (not the group
    slot it filled). A case listing several countries counts once, under the first matching
    group. Cases from countries in no group are reported as "Other (no group)"."""
    groups = profile.get("groups", [])
    n = len(df)
    quotas = [int(g.get("quota", 0)) for g in groups]
    total_target = sum(quotas)
    pct_mode = profile.get("mode") == "percentage"
    actual, other, no_country = [0] * len(groups), 0, 0
    per_country = [{c: 0 for c in g.get("countries", [])} for g in groups]
    values = df[country_col] if (n and country_col in df.columns) else []
    for cv in values:
        if str(cv).strip().lower() in ("", "nan", "none"):
            no_country += 1                     # no country data at all (e.g. a case missing from the Conflict Check)
            continue
        gi = next((i for i, g in enumerate(groups) if case_matches_group(cv, g.get("countries", []))), None)
        if gi is None:
            other += 1
            continue
        actual[gi] += 1
        text = str(cv).lower()
        for c in groups[gi].get("countries", []):
            if c.lower() in text:
                per_country[gi][c] += 1
                break
    rows = []
    for gi, g in enumerate(groups):
        t_pct = (float(g["percent"]) if (pct_mode and g.get("percent") is not None)
                 else (100.0 * quotas[gi] / total_target if total_target else 0.0))
        a_pct = 100.0 * actual[gi] / n if n else 0.0
        rows.append({"group": g["name"], "target": quotas[gi], "target_pct": t_pct, "actual": actual[gi],
                     "actual_pct": a_pct, "diff": actual[gi] - quotas[gi], "diff_pp": a_pct - t_pct})
    for label, k in (("Other (no group)", other), ("No country data", no_country)):
        if k:
            k_pct = 100.0 * k / n if n else 0.0
            rows.append({"group": label, "target": 0, "target_pct": 0.0, "actual": k,
                         "actual_pct": k_pct, "diff": k, "diff_pp": k_pct})
    return {"rows": rows, "per_country": per_country, "n": n, "total_target": total_target, "pct_mode": pct_mode}

def _fmt_pct(x):
    return f"{x:.1f}%"

def _signed(n):
    return f"+{n}" if n > 0 else str(n)

def representation_tables(rep):
    """Display pieces for the country panel: (summary line, groups table, countries-inside-groups table)."""
    rows = rep["rows"]
    groups_tbl = pd.DataFrame([{
        "Group": r["group"],
        "Target cases": r["target"], "Target %": _fmt_pct(r["target_pct"]),
        "Actual cases": r["actual"], "Actual %": _fmt_pct(r["actual_pct"]),
        "Difference": _signed(r["diff"]),
        "Match": "✅ exact" if r["diff"] == 0 else ("▲ over" if r["diff"] > 0 else "▼ under"),
    } for r in rows])
    gaps = [r for r in rows if r["diff"] != 0]
    real = [r for r in rows if r["group"] not in ("Other (no group)", "No country data")]
    if not gaps:
        summary = "✅ Every group matches the profile exactly."
    else:
        worst = max(gaps, key=lambda r: abs(r["diff"]))
        summary = (f"{sum(1 for r in real if r['diff'] == 0)} of {len(real)} groups match exactly. "
                   f"Biggest gap: **{worst['group']}** {_signed(worst['diff'])} case(s) "
                   f"({_fmt_pct(worst['actual_pct'])} actual vs {_fmt_pct(worst['target_pct'])} target).")
    crows = []
    for gi, pc in enumerate(rep["per_country"]):
        for c, k in pc.items():
            crows.append({"Group": rows[gi]["group"], "Country": c, "Cases": k,
                          "% of batch": _fmt_pct(100.0 * k / rep["n"] if rep["n"] else 0.0)})
    for r in rows[len(rep["per_country"]):]:       # "Other (no group)" / "No country data": keep the table adding up to the batch
        crows.append({"Group": "—", "Country": r["group"], "Cases": r["actual"],
                      "% of batch": _fmt_pct(100.0 * r["actual"] / rep["n"] if rep["n"] else 0.0)})
    countries_tbl = pd.DataFrame(crows, columns=["Group", "Country", "Cases", "% of batch"])
    return summary, groups_tbl, countries_tbl

def _apply_manual(manual_ids):
    """Re-run the distribution of the last Generate with the user's manual additions (or none)."""
    inp = st.session_state.dist_inputs
    final_df, report, dw = apply_batch_distribution(
        st.session_state.raw_df, inp["profile"], inp["region"], batch_type=inp["batch_type"],
        twd_ids=inp["twd_ids"], manual_ids=list(manual_ids))
    st.session_state.result_df = final_df
    st.session_state.dist_report = report
    st.session_state.dist_warnings = dw
    st.session_state.manual_added_ids = list(report.get("manual_added", []))
    st.session_state.manual_rev += 1
    log = st.session_state.generation_log
    if log and not log[-1].get("confirmed"):
        log[-1]["total"] = len(final_df)
        log[-1]["cases"] = [(r["Case ID"], r.get("Entity Name", "")) for _, r in final_df.iterrows()]

def normalize_profile(p):
    """Copy of a stored profile with every field the editor needs. Profiles saved before the
    percentage mode existed have no mode and are Fixed."""
    q = copy.deepcopy(p)
    q["mode"] = q.get("mode") if q.get("mode") in ("fixed", "percentage") else "fixed"
    groups = q.setdefault("groups", [])
    for g in groups:
        g.setdefault("countries", [])
        g["quota"] = int(g["quota"]) if g.get("quota") is not None else 1
    if not q.get("total"):
        q["total"] = max(sum(g["quota"] for g in groups), 1)
    q["total"] = int(q["total"])
    if any(g.get("percent") is None for g in groups):
        for g, pc in zip(groups, percents_from_quotas([g["quota"] for g in groups])):
            if g.get("percent") is None:
                g["percent"] = pc
    # Case criteria (TWD / Vintage): off unless the profile says otherwise
    t = q.get("twd") if isinstance(q.get("twd"), dict) else {}
    v = q.get("vintage") if isinstance(q.get("vintage"), dict) else {}
    q["twd"] = {"enabled": bool(t.get("enabled", False)), "percent": float(t.get("percent", 20.0))}
    q["vintage"] = {"enabled": bool(v.get("enabled", False)), "percent": float(v.get("percent", 10.0)),
                    "year": int(v.get("year", 2024))}
    return q

def resolve_profile(p):
    """(profile with final whole-case quotas, problem). Fixed profiles pass through unchanged;
    Percentage profiles get their quotas computed from total + percentages."""
    if p is None:
        return None, None
    q = copy.deepcopy(p)
    if q.get("mode", "fixed") != "percentage":
        return q, None
    groups = q.get("groups", [])
    if int(q.get("total") or 0) < 1:
        return q, "Enter the total number of cases for this batch (at least 1)."
    msg = percent_problem([g.get("percent", 0) for g in groups])
    if msg:
        return q, msg
    for g, n in zip(groups, quotas_from_percent(q["total"], [g["percent"] for g in groups])):
        g["quota"] = n
    return q, None

def _convert_mode(ep_dict, new_mode):
    """Switch the working profile's mode, carrying the values over instead of starting empty."""
    groups = ep_dict["groups"]
    if new_mode == "percentage":
        quotas = [int(g["quota"]) for g in groups]
        ep_dict["total"] = min(max(sum(quotas), 1), 2000)
        for g, pc in zip(groups, percents_from_quotas(quotas)):
            g["percent"] = pc
    else:
        pcts = [g.get("percent", 0.0) for g in groups]
        for g, n in zip(groups, quotas_from_percent(int(ep_dict.get("total") or 1), pcts, strict=False)):
            g["quota"] = min(max(int(n), 1), 500)
    ep_dict["mode"] = new_mode

def _wk(name, gi=None):
    """Widget key for the profile editor. The editor revision is part of every key, so loading
    another profile (or adding/removing a group) builds fresh widgets instead of reusing stale values."""
    rev = st.session_state.get("editor_rev", 0)
    return f"{name}_{rev}" if gi is None else f"{name}_{rev}_{gi}"

def _sync_ep_from_widgets(ep_dict):
    """Copy the editor widgets' current values into the working copy."""
    ss = st.session_state
    ep_dict["name"] = ss.get(_wk("ep_name"), ep_dict["name"])
    pct = ep_dict.get("mode") == "percentage"
    if pct:
        ep_dict["total"] = int(ss.get(_wk("ep_total"), ep_dict.get("total", 1)))
    for gi, g in enumerate(ep_dict["groups"]):
        g["name"]      = ss.get(_wk("gname", gi), g["name"])
        g["countries"] = list(ss.get(_wk("gcountries", gi), g["countries"]))
        if pct:
            g["percent"] = float(round(float(ss.get(_wk("gpct", gi), g.get("percent", 0.0))), 2))
        else:
            g["quota"] = int(ss.get(_wk("gquota", gi), g["quota"]))
    t, v = ep_dict.setdefault("twd", {}), ep_dict.setdefault("vintage", {})
    t["enabled"] = bool(ss.get(_wk("ep_twd_on"), t.get("enabled", False)))
    t["percent"] = float(ss.get(_wk("ep_twd_pct"), t.get("percent", 20.0)))
    v["enabled"] = bool(ss.get(_wk("ep_vin_on"), v.get("enabled", False)))
    v["percent"] = float(ss.get(_wk("ep_vin_pct"), v.get("percent", 10.0)))
    v["year"]    = int(ss.get(_wk("ep_vin_year"), v.get("year", 2024)))
    return ep_dict

def _profile_save_problem(ep_dict):
    """Why this working profile may not be saved (None if it is fine)."""
    if not str(ep_dict.get("name", "")).strip():
        return "The profile name cannot be empty."
    if not ep_dict.get("groups"):
        return "Add at least one group."
    if ep_dict.get("mode") == "percentage":
        if int(ep_dict.get("total") or 0) < 1:
            return "Enter the total number of cases for this batch (at least 1)."
        return percent_problem([g.get("percent", 0) for g in ep_dict["groups"]])
    return None

def _final_profile_for_save(ep_dict):
    """Clean copy for storage: no editor-only keys, and quotas/percent/total always coherent."""
    q = copy.deepcopy({k: v for k, v in ep_dict.items() if not k.startswith("_")})
    if q.get("mode") == "percentage":
        for g, n in zip(q["groups"], quotas_from_percent(q["total"], [g["percent"] for g in q["groups"]])):
            g["quota"] = n
    else:
        q["mode"] = "fixed"
        q["total"] = max(sum(int(g["quota"]) for g in q["groups"]), 1)
        for g, pc in zip(q["groups"], percents_from_quotas([g["quota"] for g in q["groups"]])):
            g["percent"] = pc
    t, v = q.get("twd") or {}, q.get("vintage") or {}
    q["twd"] = {"enabled": bool(t.get("enabled", False)), "percent": float(t.get("percent", 20.0))}
    q["vintage"] = {"enabled": bool(v.get("enabled", False)), "percent": float(v.get("percent", 10.0)),
                    "year": int(v.get("year", 2024))}
    return q

def replace_profile(region, old_name, profile):
    """Replace `old_name` in place (keeps list order); append if it isn't there."""
    profiles = st.session_state.dist_profiles.setdefault(region, [])
    idx = next((i for i, pr in enumerate(profiles) if pr["name"] == old_name), None)
    if idx is None:
        profiles.append(copy.deepcopy(profile))
    else:
        profiles[idx] = copy.deepcopy(profile)

def _profile_snapshot():
    return copy.deepcopy(st.session_state.dist_profiles), copy.deepcopy(st.session_state.dist_defaults)

def _profile_restore(snap):
    st.session_state.dist_profiles, st.session_state.dist_defaults = snap

def _push_profiles():
    """Push history + profiles/defaults to GitHub. Returns (ok, error)."""
    ok, err, sha = save_history_to_github(_full_payload(), st.session_state.history_sha)
    if ok:
        st.session_state.history_sha = sha
        _fetch_github_history.clear()
    return ok, err


enable_batch = st.toggle(
    "Enable Batch Distribution",
    value=False, key="batch_toggle",
    help=(
        "Use this when you have a large Pleteo export and want the app to automatically "
        "select cases by country group and quota. "
        "If you've already manually selected the cases for this delivery, leave this off."
    ),
)

dist_problem = None   # why the chosen profile cannot be turned into quotas (blocks Generate)

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

    # After a save the dropdown key changes, so `index` takes effect and lands on the saved profile
    _pending = st.session_state.pop("_pending_dist_select", None)
    if _pending and _pending in _region_profiles:
        _select_idx = _region_profiles.index(_pending)
    elif _default_name in _region_profiles:
        _select_idx = _region_profiles.index(_default_name)
    else:
        _select_idx = 0

    _action_err = None
    ps_col, def_col, del_col = st.columns([3, 1.2, 1])
    with ps_col:
        selected_profile_name = st.selectbox("Distribution Profile", options=_region_profiles,
                                              index=_select_idx, key=f"dist_select_{st.session_state.dist_nav}")
    with def_col:
        _is_default = (st.session_state.dist_defaults.get(_rp_for_config) == selected_profile_name)
        st.markdown("<br>", unsafe_allow_html=True)
        if _is_default:
            st.success("Default ✓")
        else:
            if st.button("Set as Default", key="set_default_btn", use_container_width=True):
                _snap = _profile_snapshot()
                set_default(_rp_for_config, selected_profile_name)
                _ok, _err = _push_profiles()
                if _ok:
                    st.rerun()
                _profile_restore(_snap)
                _action_err = f"❌ Not saved: GitHub could not be updated, so the default was not changed. {_err}"
    with del_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if len(_region_profiles) > 1:
            if st.button("🗑 Delete", key="del_profile_btn", use_container_width=True):
                _snap = _profile_snapshot()
                delete_profile(_rp_for_config, selected_profile_name)
                _ok, _err = _push_profiles()
                if _ok:
                    st.session_state.dist_nav += 1
                    st.rerun()
                _profile_restore(_snap)
                _action_err = f"❌ Not deleted: GitHub could not be updated, so nothing was changed. {_err}"
        else:
            st.button("🗑 Delete", disabled=True, use_container_width=True, key="del_profile_dis")
    if _action_err:
        st.error(_action_err)

    _selected_profile = get_profile(_rp_for_config, selected_profile_name)
    if _selected_profile is None:
        st.error("Profile not found. Please select another.")
        st.stop()

    _ed = st.session_state.editor_profile
    if (_ed is None or _ed.get("_editing_name") != selected_profile_name
            or _ed.get("_editing_region") != _rp_for_config):
        _loaded = normalize_profile(_selected_profile)
        _loaded["_editing_name"] = selected_profile_name
        _loaded["_editing_region"] = _rp_for_config
        st.session_state.editor_profile = _loaded
        st.session_state.editor_rev += 1          # fresh editor widgets for the profile just loaded
    ep = st.session_state.editor_profile

    # ── Group distribution mode (stored in the profile) ──
    MODE_LABELS = {
        "fixed":      "Fixed — a case count per group",
        "percentage": "Percentage — a share (%) of the batch total per group",
    }
    _mode = st.radio(
        "Group distribution", options=list(MODE_LABELS),
        format_func=lambda k: MODE_LABELS[k],
        index=0 if ep.get("mode", "fixed") == "fixed" else 1,
        horizontal=True, key=_wk("ep_mode"),
        help=(
            "**Fixed:** you set how many cases each group receives.\n\n"
            "**Percentage:** you enter the batch total once and a percentage per group. The app turns "
            "that into whole-case quotas: every share is rounded down, then the leftover cases go to the "
            "groups with the biggest fractional parts, so the quotas always add up to your total."
        ),
    )
    if _mode != ep.get("mode", "fixed"):
        _sync_ep_from_widgets(ep)                 # keep edits made under the old mode
        _convert_mode(ep, _mode)
        st.session_state.editor_rev += 1
        st.rerun()

    if ep["mode"] == "percentage":
        ep["total"] = int(st.number_input(
            "Total cases for this batch", min_value=1, max_value=2000,
            value=min(int(ep.get("total") or 1), 2000), step=1, key=_wk("ep_total"),
            help="How many cases this delivery needs. Press Update Profile to keep it as the profile's "
                 "default; otherwise it applies to this delivery only.",
        ))

    # ── Case criteria (stored in the profile): TWD and Vintage ──
    st.markdown("**Case criteria** — considered only when the batch list is generated. They don't add "
                "cases or groups; they steer which cases fill each country group's quota.")
    _cr1, _cr2 = st.columns(2)
    with _cr1:
        ep["twd"]["enabled"] = st.toggle(
            "TWD — cases tagged “Relaunch”", value=bool(ep["twd"]["enabled"]), key=_wk("ep_twd_on"),
            help="Cases whose Pleteo tags include “Relaunch”. Limits how many of them the batch may "
                 "contain. Needs the Tags column in the Pleteo export.")
        ep["twd"]["percent"] = float(st.number_input(
            "TWD: maximum % of the batch", min_value=0.0, max_value=100.0, value=float(ep["twd"]["percent"]),
            step=1.0, format="%.1f", key=_wk("ep_twd_pct"), disabled=not ep["twd"]["enabled"],
            help="A hard cap, split across the country groups in proportion to their quotas."))
    with _cr2:
        ep["vintage"]["enabled"] = st.toggle(
            "Vintage — old cases", value=bool(ep["vintage"]["enabled"]), key=_wk("ep_vin_on"),
            help="Cases whose last event is in or before the cutoff year. They are picked first until "
                 "the target is met; a warning shows if there aren't enough.")
        _vc1, _vc2 = st.columns(2)
        with _vc1:
            ep["vintage"]["percent"] = float(st.number_input(
                "Vintage: target % of the batch", min_value=0.0, max_value=100.0,
                value=float(ep["vintage"]["percent"]), step=1.0, format="%.1f", key=_wk("ep_vin_pct"),
                disabled=not ep["vintage"]["enabled"]))
        with _vc2:
            ep["vintage"]["year"] = int(st.number_input(
                "Cutoff year", min_value=1990, max_value=2100, value=int(ep["vintage"]["year"]),
                step=1, key=_wk("ep_vin_year"), disabled=not ep["vintage"]["enabled"],
                help="A case is vintage when its last event year is this year or earlier."))

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
        ep["name"] = st.text_input("Profile Name", value=ep["name"], key=_wk("ep_name"))
        _pct = ep["mode"] == "percentage"
        st.markdown("**Groups** — " + ("set the countries and the share (%) of the batch each group receives."
                                       if _pct else "set countries and quota for each group."))
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
                                                 key=_wk("gname", gi), label_visibility="collapsed")
                with gc2:
                    grp["countries"] = st.multiselect(
                        "Countries", options=available_options, default=current_selection,
                        key=_wk("gcountries", gi), label_visibility="collapsed",
                        help="Countries already assigned to another group are hidden.",
                    )
                with gc3:
                    if _pct:
                        grp["percent"] = float(st.number_input(
                            "Percent", min_value=0.0, max_value=100.0, value=float(grp.get("percent", 0.0)),
                            step=0.5, format="%.2f", key=_wk("gpct", gi), label_visibility="collapsed",
                            help="This group's share of the batch total, in %."))
                    else:
                        grp["quota"] = st.number_input("Quota", min_value=1, max_value=500,
                                                        value=int(grp["quota"]), step=1,
                                                        key=_wk("gquota", gi), label_visibility="collapsed")
                with gc4:
                    if st.button("✕", key=f"gdel_{gi}", help="Remove this group"):
                        groups_to_delete.append(gi)

        if groups_to_delete:
            _sync_ep_from_widgets(ep)
            for gi in reversed(groups_to_delete):
                ep["groups"].pop(gi)
            st.session_state.editor_rev += 1      # widgets are keyed by position: rebuild them
            st.rerun()

        if _pct:
            _pcts = [g.get("percent", 0.0) for g in ep["groups"]]
            _pmsg = percent_problem(_pcts)
            if _pmsg:
                st.error(f"🚫 {_pmsg}")
            else:
                _qs = quotas_from_percent(ep["total"], _pcts)
                st.success("✅ Percentages add up to 100%.")
                st.markdown(f"**Resulting cases** (total {sum(_qs)}): "
                            + " · ".join(f"{g['name']} **{n}**" for g, n in zip(ep["groups"], _qs)))
                for g, n in zip(ep["groups"], _qs):
                    if n == 0:
                        st.warning(f"Group **{g['name']}** rounds to 0 cases.")
        else:
            total_quota = sum(g["quota"] for g in ep["groups"])
            st.caption(f"Total quota across all groups: **{total_quota}** cases")

        if st.button("＋ Add Group", key="add_group_btn"):
            _sync_ep_from_widgets(ep)
            ep["groups"].append({"name": "New Group", "countries": [], "quota": 10, "percent": 0.0})
            st.session_state.editor_rev += 1
            st.rerun()

        st.markdown("---")
        _save_err = None
        save_col, saveas_col = st.columns(2)

        with save_col:
            if st.button("💾 Update Profile", type="primary", use_container_width=True, key="save_profile"):
                _sync_ep_from_widgets(ep)
                _old = ep.get("_editing_name", "")
                _new_name = str(ep.get("name", "")).strip()
                _problem = _profile_save_problem(ep)
                if not _problem and _new_name != _old and _new_name in get_profile_names(_rp_for_config):
                    _problem = f"A profile named “{_new_name}” already exists. Pick another name."
                if _problem:
                    _save_err = f"🚫 Not saved. {_problem}"
                else:
                    ep["name"] = _new_name
                    _to_save = _final_profile_for_save(ep)
                    _snap = _profile_snapshot()
                    _was_default = st.session_state.dist_defaults.get(_rp_for_config) == _old
                    replace_profile(_rp_for_config, _old, _to_save)
                    if _was_default and _old != _new_name:
                        set_default(_rp_for_config, _new_name)
                    _ok, _err = _push_profiles()
                    if _ok:
                        ep["_editing_name"] = _new_name
                        st.session_state["_pending_dist_select"] = _new_name
                        st.session_state.dist_nav += 1
                        st.session_state.editor_rev += 1
                        st.toast(f"✅ Profile **{_new_name}** updated.", icon="✅")
                        st.rerun()
                    _profile_restore(_snap)
                    _save_err = f"❌ Not saved: GitHub could not be updated, so nothing was changed. {_err}"

        with saveas_col:
            st.text_input("Save as new profile name", key=_wk("saveas_name"),
                          placeholder="New profile name…")
            if st.button("💾 Save as New", use_container_width=True, key="saveas_btn"):
                _clean = st.session_state.get(_wk("saveas_name"), "").strip()
                _sync_ep_from_widgets(ep)
                if not _clean:
                    _problem = "Enter a name for the new profile."
                elif _clean in get_profile_names(_rp_for_config):
                    _problem = f"A profile named “{_clean}” already exists. Choose a different name."
                else:
                    _tmp = copy.deepcopy(ep)
                    _tmp["name"] = _clean
                    _problem = _profile_save_problem(_tmp)
                if _problem:
                    _save_err = f"🚫 Not saved. {_problem}"
                else:
                    _new_p = _final_profile_for_save({**ep, "name": _clean})
                    _snap = _profile_snapshot()
                    st.session_state.dist_profiles.setdefault(_rp_for_config, []).append(copy.deepcopy(_new_p))
                    _ok, _err = _push_profiles()
                    if _ok:
                        _new_ep = normalize_profile(_new_p)
                        _new_ep["_editing_name"] = _clean
                        _new_ep["_editing_region"] = _rp_for_config
                        st.session_state.editor_profile = _new_ep
                        st.session_state["_pending_dist_select"] = _clean
                        st.session_state.dist_nav += 1
                        st.session_state.editor_rev += 1
                        st.toast(f"✅ New profile **{_clean}** created.", icon="✅")
                        st.rerun()
                    _profile_restore(_snap)
                    _save_err = f"❌ Not saved: GitHub could not be updated, so nothing was changed. {_err}"
        if _save_err:
            st.error(_save_err)

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
    # Toggle OFF — the region's default profile (fixed or percentage), Standard type
    _default_name = st.session_state.dist_defaults.get(region_code)
    _dp = get_profile(region_code, _default_name) if _default_name else None
    ep = normalize_profile(_dp) if _dp else None
    if ep:
        ep["_editing_name"] = _default_name
    batch_type = "standard"
    if ep and ((ep.get("twd") or {}).get("enabled") or (ep.get("vintage") or {}).get("enabled")):
        st.caption(f"ℹ️ The default profile “{_default_name}” has TWD / Vintage switched on, so they apply to this batch.")

# Turn the working profile into final whole-case quotas (percentage profiles are converted here)
if ep is not None:
    ep_resolved, dist_problem = resolve_profile(ep)
else:
    ep_resolved, dist_problem = None, None
if dist_problem:
    st.error(f"🚫 The distribution profile can't be applied yet: {dist_problem} "
             "Generate Prebatch File stays locked until this is fixed.")


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

                _cf_problem = github_config_problem()
                if _cf_problem:
                    st.error(
                        f"🚫 {_cf_problem}\n\n"
                        "Nothing can be registered until this is fixed. Keep the Prebatch file; after the "
                        "reboot, upload it here again."
                    )

                if st.button(
                    "✅ Confirm Delivery from File", type="primary",
                    use_container_width=True, key="cf_confirm_btn",
                    disabled=(cf_is_dup and not cf_overwrite_ok) or bool(_cf_problem),
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
                    _prev_history = copy.deepcopy(st.session_state.delivery_history)
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
                        st.session_state.delivery_history = _prev_history   # nothing was saved: keep no phantom batch
                        st.error(f"❌ Failed to save to GitHub: {err}")
                        st.info("Nothing was saved, so this batch is NOT in the delivery history yet. "
                                "Fix the connection and press the button again.")
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

    if not st.session_state.history_load_ok:
        st.error(
            "🚫 Validate Batch is locked because the delivery history could not be loaded from "
            "GitHub. Without it the 6-month rule and the repeated-case checks cannot run, and an "
            "empty result would look like an all-clear. See the warning at the top of the page, "
            "fix the GitHub connection, then press 🔄."
        )

    _tags_missing = bool(ep_resolved and (ep_resolved.get("twd") or {}).get("enabled")
                         and pl_df_v is not None and "Tags" not in pl_df_v.columns)
    if _tags_missing:
        st.error("🚫 TWD needs the **Tags** column from the Pleteo export, and the uploaded Pleteo file "
                 "doesn't have it. Re-export it with tags, or switch TWD off in the profile. "
                 "Generate Prebatch File stays locked.")

    btn_col1, btn_col2 = st.columns(2)

    # ── Validate Batch ──
    with btn_col1:
        if st.button("🔍 Validate Batch", use_container_width=True,
                     disabled=(not all_valid) or (not st.session_state.history_load_ok),
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
        generate_disabled = (not all_valid or not st.session_state.batch_validated
                             or bool(dist_problem) or _tags_missing)
        generate_help = (
            "Run Validate Batch first." if not st.session_state.batch_validated else
            "Resolve file validation errors first." if not all_valid else
            "Fix the distribution profile first (see the message in the Batch Distribution section)." if dist_problem else
            "TWD needs the Tags column in the Pleteo export." if _tags_missing else
            "Generate the Prebatch output file."
        )
        if st.button("▶ Generate Prebatch File", type="primary", use_container_width=True,
                     disabled=generate_disabled, help=generate_help):
            with st.spinner("Processing files..."):
                try:
                    raw_df, unmatched, grouped, duplicates, excluded_ct, deduped = process_data(
                        qs_df_v, pl_df_v, cc_df_v, region_code
                    )
                    st.session_state.raw_df          = raw_df
                    st.session_state.unmatched       = unmatched
                    st.session_state.grouped         = grouped
                    st.session_state.duplicates      = duplicates
                    st.session_state.excluded_count  = excluded_ct
                    st.session_state.sub_id_deduped  = deduped
                    st.session_state.region_processed = region_code
                    st.session_state.dist_report   = None
                    st.session_state.dist_warnings = []
                    st.session_state.dist_applied  = False
                    st.session_state.manual_added_ids = []      # a fresh Generate starts without manual additions
                    st.session_state.dist_inputs   = None
                    st.session_state.prebatch_ready_to_confirm = True

                    _tags_ok = bool(pl_df_v is not None and "Tags" in pl_df_v.columns)
                    _twd_all = compute_twd_ids(pl_df_v, raw_df["Case ID"]) if _tags_ok else set()
                    st.session_state.comp_inputs = {"twd_ids": _twd_all, "tags_ok": _tags_ok}

                    # Always apply distribution — toggle controls type/profile choice only
                    # Toggle OFF = Standard type with default profile
                    if ep_resolved is not None:
                        profile_clean = {k: v for k, v in ep_resolved.items() if not k.startswith("_")}
                        try:
                            _twd_ids = _twd_all      # only enforced when the profile's TWD toggle is on
                            final_df, report, dw = apply_batch_distribution(
                                raw_df, profile_clean, region_code, batch_type=batch_type, twd_ids=_twd_ids
                            )
                            st.session_state.result_df     = final_df
                            st.session_state.dist_report   = report
                            st.session_state.dist_warnings = dw
                            st.session_state.dist_applied  = True
                            st.session_state.dist_inputs   = {"profile": profile_clean, "batch_type": batch_type,
                                                              "region": region_code, "twd_ids": _twd_ids}
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


def _render_batch_panel(result_df, rp, dist_applied, dist_report):
    """Batch composition cards + country representation for the batch shown in the preview."""
    # ── Batch composition + country representation (recomputed on every run, so manual additions show up) ──
    _ci = st.session_state.comp_inputs or {}
    _prof = (st.session_state.dist_inputs or {}).get("profile") if dist_applied else None
    _vyear = int(((_prof or {}).get("vintage") or {}).get("year", 2024))
    _comp = batch_composition(result_df, _ci.get("twd_ids", set()), bool(_ci.get("tags_ok")), _vyear)
    _crit = (dist_report.get("criteria") or {}) if (dist_applied and dist_report) else {}
    _pcs = lambda x: f"{100.0 * x / _comp['n']:.1f}%" if _comp["n"] else "0.0%"
    st.markdown("**Batch composition**")
    _k1, _k2, _k3, _k4 = st.columns(4)
    _k1.metric("HIGH · 3+ machines", f"{_comp['high']} ({_pcs(_comp['high'])})")
    _k2.metric("LOW · under 3 machines", f"{_comp['low']} ({_pcs(_comp['low'])})")
    if _comp["twd"] is None:
        _k3.metric("TWD · Relaunch tag", "n/a", delta="needs the Tags column", delta_color="off")
    elif (_crit.get("twd") or {}).get("enabled"):
        _cap = _crit["twd"]["cap_total"]
        _k3.metric("TWD · Relaunch tag", f"{_comp['twd']} ({_pcs(_comp['twd'])})",
                   delta=(f"over max {_cap}" if _comp["twd"] > _cap else f"max {_cap}"),
                   delta_color=("inverse" if _comp["twd"] > _cap else "off"))
    else:
        _k3.metric("TWD · Relaunch tag", f"{_comp['twd']} ({_pcs(_comp['twd'])})")
    if (_crit.get("vintage") or {}).get("enabled"):
        _tgt = _crit["vintage"]["target_total"]
        _k4.metric(f"Vintage · last event ≤ {_comp['vintage_year']}", f"{_comp['vintage']} ({_pcs(_comp['vintage'])})",
                   delta=(f"below target {_tgt}" if _comp["vintage"] < _tgt else f"target {_tgt}"),
                   delta_color=("inverse" if _comp["vintage"] < _tgt else "off"))
    else:
        _k4.metric(f"Vintage · last event ≤ {_comp['vintage_year']}", f"{_comp['vintage']} ({_pcs(_comp['vintage'])})")
    st.caption(f"HIGH + LOW = all {_comp['n']} cases in the preview. TWD and Vintage are flags and can overlap.")

    if _prof:
        _rep = country_representation(result_df, _prof, "Countries" if rp == "MCC" else "Country")
        _summary, _gtbl, _ctbl = representation_tables(_rep)
        with st.expander("🌎 Country representation vs profile", expanded=True):
            st.markdown(_summary)
            st.dataframe(_gtbl, hide_index=True, use_container_width=True)
            if _rep["n"] != _rep["total_target"]:
                st.caption(f"The preview has {_rep['n']} of the {_rep['total_target']} requested cases, so actual % "
                           f"is a share of the {_rep['n']} cases shown.")
            if _rep["pct_mode"]:
                st.caption("Percentage profile: the target % is the one set in the profile; target cases are its whole-case result.")
            st.caption("Actual counts use each case's own country. A case listing several countries counts once, "
                       "under the first matching group. \"Other (no group)\" = a country that is in no profile group; "
                       "\"No country data\" = the case has no country (for example, it is missing from the Conflict Check).")
        with st.expander("Countries inside each group", expanded=False):
            st.dataframe(_ctbl, hide_index=True, use_container_width=True)



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
            f"**Prebatch — {dist_report['profile_name']} · {batch_label}"
            f"{(' · % of ' + str(dist_report.get('total'))) if dist_report.get('mode') == 'percentage' else ''}** "
            f"&nbsp;·&nbsp; {len(result_df)} of {len(raw_df)} cases selected"
        )
        for w in dist_warnings:
            st.warning(w)

        if is_custom:
            gr_cols = st.columns(len(dist_report["groups"]))
            for col, grp in zip(gr_cols, dist_report["groups"]):
                overflow_note = " (+overflow)" if grp.get("overflow_note") else ""
                if grp.get("added"):
                    overflow_note += f" (+{grp['added']} added)"
                delta_val = "On target" if grp["shortfall"] == 0 else f"-{grp['shortfall']} short"
                col.metric(
                    label=grp["group"],
                    value=f"{grp['filled']} / {grp['quota']}",
                    delta=f"{delta_val}{overflow_note}",
                    delta_color="normal" if grp["shortfall"] == 0 else "inverse",
                )

        _crit = dist_report.get("criteria") or {}
        _t, _v = _crit.get("twd") or {}, _crit.get("vintage") or {}
        if _t.get("enabled") or _v.get("enabled"):
            _cc1, _cc2 = st.columns(2)
            if _t.get("enabled"):
                _over_t = _t["selected"] - _t["cap_total"]
                _cc1.metric("TWD (Relaunch)", f"{_t['selected']} / max {_t['cap_total']}",
                            delta=(f"+{_over_t} over the cap (added manually)" if _over_t > 0 else "within the cap"),
                            delta_color=("inverse" if _over_t > 0 else "off"))
            if _v.get("enabled"):
                _gap_v = _v["selected"] - _v["target_total"]
                _cc2.metric(f"Vintage (≤ {_v['year']})", f"{_v['selected']} / target {_v['target_total']}",
                            delta=("target met" if _gap_v >= 0 else f"{_gap_v} short"),
                            delta_color=("off" if _gap_v >= 0 else "inverse"))
            with st.expander("TWD / Vintage detail by group", expanded=False):
                _rows = []
                for gi_, g_ in enumerate(dist_report["groups"]):
                    _rows.append({"Group": g_["group"],
                                  "TWD (selected / cap)": (f"{_t['by_group'][gi_]} / {_t['caps'][gi_]}" if _t.get("enabled") else "off"),
                                  "Vintage (selected / target)": (f"{_v['by_group'][gi_]} / {_v['targets'][gi_]}" if _v.get("enabled") else "off")})
                st.dataframe(pd.DataFrame(_rows), hide_index=True, use_container_width=True)

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
    dcols = st.columns(4)
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
    with dcols[3]:
        deduped_list = st.session_state.get("sub_id_deduped", [])
        if deduped_list:
            with st.expander(f"🔧 Sub-IDs Cleaned ({len(deduped_list)})"):
                st.caption("Repeated sub-IDs deduplicated automatically.")
                for c in deduped_list: st.code(c)

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

    try:
        _render_batch_panel(result_df, rp, dist_applied, dist_report)
    except Exception as _panel_err:          # informational panel: never let it block the results or Confirm
        st.warning(f"The batch composition panel could not be built: {_panel_err}")

    _added_ids = list(dist_report.get("manual_added", [])) if (dist_applied and dist_report) else []
    if _added_ids:
        _aset = set(_added_ids)
        def _mark_added(row):
            return ["background-color: #FFF3CD; color: #1A1A1A;" if str(row["Case ID"]) in _aset else "" for _ in row]
        st.dataframe(result_df.style.apply(_mark_added, axis=1), use_container_width=True, height=380)
    else:
        st.dataframe(result_df, use_container_width=True, height=380)

    # ── Add TWD / Vintage cases from the backlog (only while the batch is short) ──
    if dist_applied and dist_report and st.session_state.prebatch_ready_to_confirm and st.session_state.dist_inputs:
        if _added_ids:
            st.info(f"✋ {len(_added_ids)} case(s) were added manually from the backlog (highlighted in the preview).")
            if st.button("↩ Remove the manually added cases", key="manual_undo_btn"):
                _apply_manual([])
                st.rerun()
        _cands = dist_report.get("manual_candidates")
        _short = int(dist_report.get("shortfall", 0))
        if _short > 0 and _cands is not None and len(_cands) > 0:
            with st.expander(f"➕ Add TWD / Vintage cases from the backlog — the batch is short by {_short}", expanded=True):
                st.caption(f"These cases were not selected (for example, held back by the TWD cap). You can add up to "
                           f"{_short} of them. Each one counts toward its own country group.")
                st.dataframe(_cands, hide_index=True, use_container_width=True,
                             height=min(35 * len(_cands) + 40, 320))
                _labels = {r["Case ID"]: (f"{r['Case ID']} — {r['Entity Name']} · {r['Country']} · "
                                          f"{r['# All Time Machines']} machines"
                                          f"{' · TWD' if r['TWD'] else ''}{' · Vintage' if r['Vintage'] else ''}")
                           for _, r in _cands.iterrows()}
                _pick = st.multiselect("Cases to add", options=list(_labels), format_func=lambda c: _labels[c],
                                       key=f"manual_pick_{st.session_state.manual_rev}")
                _over = len(_pick) > _short
                if _over:
                    st.warning(f"Pick at most {_short} case(s): the batch is short by {_short}.")
                if st.button("➕ Add to Prebatch", type="primary", key="manual_add_btn",
                             disabled=(not _pick) or _over):
                    _apply_manual(list(_added_ids) + list(_pick))
                    st.rerun()
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
            _pct_txt = f" (% of {dist_report.get('total')})" if dist_report.get("mode") == "percentage" else ""
            confirm_label = f"{profile_name}{_pct_txt} · {batch_label}"
            if dist_report.get("manual_added"):
                confirm_label += f" · +{len(dist_report['manual_added'])} added manually"
        else:
            confirm_label = "Full Prebatch (no distribution applied)"

        st.caption(
            f"**{len(result_df)} cases** will be confirmed · "
            f"Profile: **{confirm_label}** · Region: **{rp}**"
        )

        _gh_problem = github_config_problem()
        if _gh_problem:
            st.error(
                f"🚫 {_gh_problem}\n\n"
                "Your Prebatch file is not affected: download it above. Once the secrets are fixed "
                "and the app is rebooted, register it with **Confirm from Existing Prebatch File**."
            )

        if st.button("✅ Confirm Batch Delivery", type="primary",
                     use_container_width=True, key="confirm_delivery_btn",
                     disabled=(is_duplicate and not overwrite_confirmed) or bool(_gh_problem)):
            batch_entry = {
                "batch_number": int(batch_number),
                "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                "region": rp, "profile": confirm_label,
                "total_cases": len(result_df),
                "cases": [[row["Case ID"], row.get("Entity Name", "")]
                           for _, row in result_df.iterrows()],
            }
            _prev_history = copy.deepcopy(st.session_state.delivery_history)
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
                st.session_state.delivery_history = _prev_history   # nothing was saved: keep no phantom batch
                st.error(f"❌ Failed to save to GitHub: {err}")
                st.info("Nothing was saved, so this batch is NOT in the delivery history yet. "
                        "Your Prebatch file is unaffected. Fix the connection and press Confirm again, "
                        "or use Confirm from Existing Prebatch File.")
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
