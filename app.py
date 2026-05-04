import streamlit as st
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
from datetime import datetime

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

def _gh_file_url():
    repo  = st.secrets.get("GITHUB_REPO", "")          # "owner/repo"
    path  = st.secrets.get("HISTORY_FILE_PATH", HISTORY_FILE)
    return f"https://api.github.com/repos/{repo}/contents/{path}", path

def load_history_from_github():
    """Fetch batch_history.json from GitHub. Returns (history_dict, sha, error_msg)."""
    url, _ = _gh_file_url()
    try:
        req = urllib.request.Request(url, headers=_gh_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content), data["sha"], None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"MCC": [], "CS": []}, None, None   # file doesn't exist yet, fresh start
        return None, None, f"GitHub HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, None, str(e)

def save_history_to_github(history_dict, sha):
    """Push updated batch_history.json to GitHub. Returns (ok, error_msg)."""
    url, path = _gh_file_url()
    content_b64 = base64.b64encode(
        json.dumps(history_dict, indent=2, ensure_ascii=False).encode("utf-8")
    ).decode()
    payload = {
        "message": f"Update batch history — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": content_b64,
        "path": path,
    }
    if sha:
        payload["sha"] = sha
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
        return False, f"GitHub HTTP {e.code}: {body}", sha
    except Exception as e:
        return False, str(e), sha


# ──────────────────────────────────────────────
# Session State + History Bootstrap
# ──────────────────────────────────────────────
def _init_state():
    defaults = {
        "result_df": None,
        "unmatched": [], "grouped": [], "duplicates": [],
        "region_processed": None,
        "generation_log": [],
        # Batch distribution
        "dist_profiles": {
            "MCC": [copy.deepcopy(DEFAULT_MCC_DIST)],
            "CS":  [copy.deepcopy(DEFAULT_CS_DIST)],
        },
        "dist_defaults": {"MCC": "Standard MCC", "CS": "Standard CS"},
        "batch_result_df": None, "batch_report": None, "batch_warnings": [],
        "editor_profile": None,
        # Delivery history (persistent via GitHub)
        "delivery_history": {"MCC": [], "CS": []},
        "history_sha": None,
        "history_loaded": False,
        "history_load_msg": "",
        "history_load_ok": False,
        # Validation gate
        "batch_validated": False,
        "validation_warnings": [],
        "validation_clean": False,
        # Confirm delivery state
        "prebatch_ready_to_confirm": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# Load delivery history from GitHub once per session
if not st.session_state.history_loaded:
    history, sha, err = load_history_from_github()
    if err:
        st.session_state.history_load_ok = False
        st.session_state.history_load_msg = f"⚠️ Could not load batch history from GitHub: {err}"
    else:
        st.session_state.delivery_history = history or {"MCC": [], "CS": []}
        st.session_state.history_sha = sha
        st.session_state.history_load_ok = True
        total = len(st.session_state.delivery_history.get("MCC", [])) + \
                len(st.session_state.delivery_history.get("CS", []))
        st.session_state.history_load_msg = (
            f"✅ Batch history loaded — "
            f"MCC: {len(st.session_state.delivery_history.get('MCC', []))} batch(es) · "
            f"CS: {len(st.session_state.delivery_history.get('CS', []))} batch(es)"
        )
    st.session_state.history_loaded = True


# ──────────────────────────────────────────────
# History Load Status Banner
# ──────────────────────────────────────────────
if st.session_state.history_load_ok:
    st.success(st.session_state.history_load_msg)
else:
    st.warning(st.session_state.history_load_msg)


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
            '<p style="color:#B0B0B0 !important;font-size:0.82rem;margin:0 0 0.5rem 0;'
            'font-weight:600;letter-spacing:0.2px;">See Documentation</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<a href="data:application/pdf;base64,{DOC_B64}" target="_blank" rel="noopener noreferrer" class="rx-doc-btn">'
            f'<span class="rx-doc-btn-text">Open Reference Guide</span></a>',
            unsafe_allow_html=True,
        )
    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    # ── Delivery History (persistent) ──
    st.markdown("### Delivery History")
    for reg in ["MCC", "CS"]:
        batches = st.session_state.delivery_history.get(reg, [])
        if batches:
            st.markdown(f"**{reg}** — {len(batches)} batch(es)")
            for b in reversed(batches[-5:]):   # last 5 per region
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
        else:
            st.caption(f"{reg}: No deliveries confirmed yet.")
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
# Region + File Uploaders
# ──────────────────────────────────────────────
region = st.radio("Select Region",
    options=["MCC (México Central Caribe)", "CS (Cono Sur)"], horizontal=True,
    help="MCC: Mexico, Central America, Caribbean  —  CS: South America")
region_code = "MCC" if "MCC" in region else "CS"

# Reset validation when region changes
if st.session_state.get("_last_region") != region_code:
    st.session_state.batch_validated = False
    st.session_state.validation_warnings = []
    st.session_state.validation_clean = False
    st.session_state.prebatch_ready_to_confirm = False
    st.session_state._last_region = region_code

st.divider()
st.subheader("Upload Source Files")
col1, col2, col3 = st.columns(3)
with col1:
    qs_file = st.file_uploader("QS Delivery ID File", type=["csv","xlsx","xls"],
        help="Contains grouped Case IDs, entity names, aggregated machine counts, and event dates.")
with col2:
    pl_file = st.file_uploader("PL Batch File (Pleteo Export)", type=["csv","xlsx","xls"],
        help="CRM export providing the 'Updated' timestamp for Last Updated At (MCC).")
with col3:
    pc_file = st.file_uploader("Conflict Check File", type=["csv","xlsx","xls"],
        help="Investigation data: machine overviews, notes, entity details, and case attribution.")


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def read_file(f):
    f.seek(0)
    name = f.name.lower()
    return (pd.read_csv(f, dtype=str, keep_default_na=False)
            if name.endswith(".csv")
            else pd.read_excel(f, dtype=str, keep_default_na=False))

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

def validate_against_history(case_ids: list, region: str):
    """
    Check whether any of the given Case IDs were previously delivered.
    Returns (warnings list, is_clean bool).
    Warnings — not a blocking error, just informational.
    """
    delivered_ids = {}
    for batch in st.session_state.delivery_history.get(region, []):
        batch_num = batch.get("batch_number", "?")
        batch_date = batch.get("delivery_date", "?")
        for case in batch.get("cases", []):
            cid = case[0] if isinstance(case, (list, tuple)) else case.get("case_id", "")
            delivered_ids[cid] = (batch_num, batch_date)

    warnings = []
    for cid in case_ids:
        # For grouped IDs (comma-separated) check each sub-ID
        sub_ids = [c.strip() for c in cid.split(",") if c.strip()]
        for sub in sub_ids:
            if sub in delivered_ids:
                b_num, b_date = delivered_ids[sub]
                warnings.append(
                    f"**{sub}** was previously delivered in Batch **#{b_num}** on {b_date}."
                )

    return warnings, len(warnings) == 0


# ──────────────────────────────────────────────
# Core Processing
# ──────────────────────────────────────────────

def process_data(qs_df, pl_df, cc_df, region_code):
    qs_df, pl_df, cc_df = clean_df(qs_df), clean_df(pl_df), clean_df(cc_df)
    cc_lookup = build_lookup(cc_df, "Case ID")
    pl_lookup = build_lookup(pl_df, "External Case ID")

    output_rows, unmatched_cases, grouped_cases = [], [], []
    seen_case_ids, duplicate_cases = {}, []

    for idx, (_, qs_row) in enumerate(qs_df.iterrows()):
        case_id_raw = str(qs_row.get("Case ID","")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue
        if case_id_raw in seen_case_ids:
            duplicate_cases.append(case_id_raw)
            continue
        seen_case_ids[case_id_raw] = idx

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
    return result_df, unmatched_cases, grouped_cases, duplicate_cases


# ──────────────────────────────────────────────
# Batch Distribution — Core Algorithm
# ──────────────────────────────────────────────

def case_matches_group(country_val: str, group_countries: list) -> bool:
    cv = str(country_val).lower()
    return any(gc.lower() in cv for gc in group_countries)

def apply_batch_distribution(df, distribution, region_code, priority_machines=True):
    country_col = "Countries" if region_code == "MCC" else "Country"
    df_work = df.copy().reset_index(drop=True)
    df_work["_m"] = pd.to_numeric(df_work["# All Time Machines"], errors="coerce").fillna(0)
    if priority_machines:
        df_work["_p"] = (df_work["_m"] >= 3).astype(int)
        df_work = df_work.sort_values(["_p", "_m"], ascending=[False, False])
    else:
        df_work = df_work.sort_values("_m", ascending=False)
    df_work = df_work.reset_index(drop=True)

    group_pools = []
    assigned = set()
    for group in distribution["groups"]:
        pool_idx = df_work.index[
            df_work[country_col].apply(lambda v: case_matches_group(v, group["countries"]))
            & ~df_work.index.isin(assigned)
        ].tolist()
        group_pools.append(pool_idx)
        assigned.update(pool_idx)

    group_selections = []
    group_reports = []
    used = set()

    for group, pool in zip(distribution["groups"], group_pools):
        quota = group["quota"]
        available = [i for i in pool if i not in used]
        selected = available[:quota]
        used.update(selected)
        shortfall = quota - len(selected)
        group_selections.append(selected)
        group_reports.append({
            "group": group["name"], "quota": quota,
            "filled": len(selected), "shortfall": shortfall,
            "overflow_from": [],
        })

    warnings = []
    for i, (group, report) in enumerate(zip(distribution["groups"], group_reports)):
        if report["shortfall"] <= 0: continue
        still_needed = report["shortfall"]
        for j, (other_group, other_pool) in enumerate(zip(distribution["groups"], group_pools)):
            if j == i or still_needed <= 0: continue
            overflow_available = [idx for idx in other_pool if idx not in used]
            if not overflow_available: continue
            take = overflow_available[:still_needed]
            group_selections[i].extend(take)
            used.update(take)
            report["filled"] += len(take)
            report["overflow_from"].append(f"**{other_group['name']}** ({len(take)} cases)")
            still_needed -= len(take)

        actual_shortfall = report["quota"] - report["filled"]
        if report["overflow_from"]:
            warnings.append(
                f"⚠️ Group **{group['name']}** quota of {group['quota']} was not fully met. "
                f"Completed with overflow from: {', '.join(report['overflow_from'])}."
            )
        if actual_shortfall > 0:
            warnings.append(
                f"🚨 Group **{group['name']}** is still short by **{actual_shortfall}** case(s) "
                f"after exhausting all available pools."
            )
        report["shortfall"] = actual_shortfall

    all_selected_idx = sorted(set(idx for sel in group_selections for idx in sel))
    drop_cols = [c for c in ["_m", "_p"] if c in df_work.columns]
    selected_df = df_work.loc[all_selected_idx].drop(columns=drop_cols).reset_index(drop=True)

    backlog_df = df_work[~df_work.index.isin(all_selected_idx)].copy()
    backlog_rows = []
    for _, row in backlog_df.iterrows():
        cv = str(row.get(country_col, "Unknown")).strip()
        countries_in_row = [c.strip() for c in re.split(r"[,|;\s/]+", cv) if c.strip()] or ["Unknown"]
        machines = row.get("_m", 0)
        for c in countries_in_row:
            backlog_rows.append({"Country": c, "machines": float(machines)})

    backlog_summary = {}
    for br in backlog_rows:
        c = br["Country"]
        if c not in backlog_summary:
            backlog_summary[c] = {"total": 0, "priority": 0, "standard": 0}
        backlog_summary[c]["total"] += 1
        if br["machines"] >= 3:
            backlog_summary[c]["priority"] += 1
        else:
            backlog_summary[c]["standard"] += 1

    backlog_table = pd.DataFrame([
        {"Country": c, "Total Backlog": v["total"],
         "3+ Machines (Priority)": v["priority"], "< 3 Machines": v["standard"]}
        for c, v in sorted(backlog_summary.items(), key=lambda x: -x[1]["total"])
    ])

    report = {
        "groups": group_reports, "total_selected": len(selected_df),
        "total_backlog": len(backlog_df), "backlog_table": backlog_table,
        "profile_name": distribution["name"],
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
            ids = [str(v).strip() for v in df_id[id_col]
                   if str(v).strip() and str(v).strip().lower() not in ("nan","none","")]
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
all_uploaded = bool(qs_file and pl_file and pc_file)
qs_df_v = pl_df_v = cc_df_v = None
all_valid = False

if any([qs_file, pl_file, pc_file]):
    with st.expander("File Validation", expanded=True):
        vc1, vc2, vc3 = st.columns(3)
        with vc1: qs_df_v, qs_ok = show_validation(qs_file, QS_REQUIRED, "QS Delivery ID")
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
            # Extract Case IDs from QS file to validate
            try:
                qs_temp = clean_df(read_file(qs_file))
                case_ids_to_validate = [
                    str(v).strip() for v in qs_temp.get("Case ID", qs_temp.iloc[:, 0])
                    if str(v).strip() and str(v).strip().lower() != "nan"
                ]
                warnings_hist, is_clean = validate_against_history(case_ids_to_validate, region_code)
                st.session_state.validation_warnings = warnings_hist
                st.session_state.validation_clean = is_clean
                st.session_state.batch_validated = True
                st.session_state.prebatch_ready_to_confirm = False
                st.session_state.result_df = None
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
                    result_df, unmatched, grouped, duplicates = process_data(
                        qs_df_v, pl_df_v, cc_df_v, region_code
                    )
                    st.session_state.result_df = result_df
                    st.session_state.unmatched = unmatched
                    st.session_state.grouped = grouped
                    st.session_state.duplicates = duplicates
                    st.session_state.region_processed = region_code
                    st.session_state.batch_result_df = None
                    st.session_state.batch_report = None
                    st.session_state.batch_warnings = []
                    st.session_state.prebatch_ready_to_confirm = True
                    st.session_state.generation_log.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "region": region_code, "total": len(result_df),
                        "grouped": len(grouped), "unmatched": len(unmatched),
                        "duplicates": len(duplicates), "confirmed": False,
                        "batch_number": None, "delivery_date": None,
                        "cases": [(r["Case ID"], r.get("Entity Name","")) for _, r in result_df.iterrows()],
                    })
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
                    st.exception(e)

    # ── Validation Result Display ──
    if st.session_state.batch_validated:
        if st.session_state.validation_clean:
            st.success(
                "✅ **Batch validated — No repeated Case IDs found.** "
                "All cases in this batch are new to the delivery history. "
                "You may now generate the Prebatch file."
            )
        else:
            st.warning(
                f"⚠️ **{len(st.session_state.validation_warnings)} previously delivered Case ID(s) detected.** "
                "This is a warning only — you can still generate the Prebatch file. "
                "These cases may be relaunches or recontacts."
            )
            with st.expander(f"View {len(st.session_state.validation_warnings)} repeated Case ID(s)", expanded=False):
                for w in st.session_state.validation_warnings:
                    st.markdown(f"- {w}")

else:
    missing = [n for f, n in [(qs_file,"QS Delivery ID"),(pl_file,"PL Batch"),(pc_file,"Conflict Check")] if not f]
    st.info(f"Upload the remaining file(s) to proceed: **{', '.join(missing)}**")


# ──────────────────────────────────────────────
# Results + Confirm Batch Delivery
# ──────────────────────────────────────────────
if st.session_state.result_df is not None:
    result_df = st.session_state.result_df
    rp = st.session_state.region_processed

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases",        len(result_df))
    m2.metric("Grouped Entities",   len(st.session_state.grouped))
    m3.metric("Unmatched",          len(st.session_state.unmatched))
    m4.metric("Duplicates Removed", len(st.session_state.duplicates))

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

    st.subheader("Output Preview")
    st.dataframe(result_df, use_container_width=True, height=380)
    st.download_button(
        label=f"⬇ Download Full Prebatch_{rp}.xlsx",
        data=to_excel(result_df), file_name=f"Prebatch_{rp}.xlsx",
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
            <p>Complete the delivery details below and confirm to register this batch permanently in the delivery history.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        suggested_batch = next_batch_number(rp)
        cf1, cf2 = st.columns(2)
        with cf1:
            delivery_date = st.date_input(
                "Delivery Date", value=datetime.today(),
                key="confirm_date",
                help="The date this batch is being delivered.",
            )
        with cf2:
            batch_number = st.number_input(
                "Batch Number",
                min_value=1, value=suggested_batch, step=1,
                key="confirm_batch_num",
                help=f"Sequential batch number. Suggested: {suggested_batch} (last confirmed + 1).",
            )

        # Check if this batch number already exists for this region
        existing_nums = [b.get("batch_number") for b in
                         st.session_state.delivery_history.get(rp, [])]
        if int(batch_number) in existing_nums:
            st.warning(f"⚠️ Batch **#{int(batch_number)}** already exists for {rp}. "
                       "Using a duplicate number will overwrite the historical entry.")

        # Determine which cases to confirm: batch result if applied, else full prebatch
        if st.session_state.batch_result_df is not None:
            confirm_df = st.session_state.batch_result_df
            profile_name = st.session_state.batch_report.get("profile_name", "—") if st.session_state.batch_report else "—"
        else:
            confirm_df = result_df
            profile_name = "Full Prebatch (no distribution applied)"

        st.caption(
            f"Cases to be confirmed: **{len(confirm_df)}** · "
            f"Profile: **{profile_name}** · "
            f"Region: **{rp}**"
        )

        if st.button("✅ Confirm Batch Delivery", type="primary", use_container_width=True,
                     key="confirm_delivery_btn"):
            batch_entry = {
                "batch_number": int(batch_number),
                "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                "region": rp,
                "profile": profile_name,
                "total_cases": len(confirm_df),
                "cases": [
                    [row["Case ID"], row.get("Entity Name", "")]
                    for _, row in confirm_df.iterrows()
                ],
            }

            # Update in-memory history
            region_batches = st.session_state.delivery_history.setdefault(rp, [])
            # Replace if same batch number exists, else append
            replaced = False
            for i, b in enumerate(region_batches):
                if b.get("batch_number") == int(batch_number):
                    region_batches[i] = batch_entry
                    replaced = True
                    break
            if not replaced:
                region_batches.append(batch_entry)

            # Sort by batch number
            st.session_state.delivery_history[rp] = sorted(
                region_batches, key=lambda b: b.get("batch_number", 0)
            )

            # Push to GitHub
            with st.spinner("Saving batch history to GitHub..."):
                ok, err, new_sha = save_history_to_github(
                    st.session_state.delivery_history, st.session_state.history_sha
                )

            if ok:
                st.session_state.history_sha = new_sha
                st.session_state.prebatch_ready_to_confirm = False
                # Mark session log entry as confirmed
                if st.session_state.generation_log:
                    last = st.session_state.generation_log[-1]
                    last["confirmed"] = True
                    last["batch_number"] = int(batch_number)
                    last["delivery_date"] = delivery_date.strftime("%Y-%m-%d")
                st.success(
                    f"🎉 Batch **#{int(batch_number)}** for **{rp}** confirmed and saved! "
                    f"Delivery date: **{delivery_date.strftime('%Y-%m-%d')}** · "
                    f"**{len(confirm_df)}** cases registered."
                )
                st.rerun()
            else:
                st.error(f"❌ Failed to save to GitHub: {err}")
                st.info("The batch was added to the in-memory history for this session, "
                        "but could not be persisted. Check your GitHub secrets and retry.")

    # ════════════════════════════════════════════
    # BATCH DISTRIBUTION SECTION
    # ════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div class="batch-section">
        <h3>📦 Batch Distribution</h3>
        <p>Selectively distribute the generated cases by country group and quota.
           Priority cases (3+ Total Machines) are placed first within each group.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    enable_batch = st.toggle("Enable Batch Distribution", value=False, key="batch_toggle")

    if enable_batch:
        region_profiles = get_profile_names(rp)
        default_name = st.session_state.dist_defaults.get(rp)
        default_idx = region_profiles.index(default_name) if default_name in region_profiles else 0

        ps_col, def_col, del_col = st.columns([3, 1.2, 1])
        with ps_col:
            selected_profile_name = st.selectbox("Distribution Profile", options=region_profiles,
                                                  index=default_idx, key="dist_select")
        with def_col:
            is_default = (st.session_state.dist_defaults.get(rp) == selected_profile_name)
            st.markdown("<br>", unsafe_allow_html=True)
            if is_default:
                st.success("Default ✓")
            else:
                if st.button("Set as Default", key="set_default_btn", use_container_width=True):
                    set_default(rp, selected_profile_name); st.rerun()
        with del_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if len(region_profiles) > 1:
                if st.button("🗑 Delete", key="del_profile_btn", use_container_width=True):
                    delete_profile(rp, selected_profile_name); st.rerun()
            else:
                st.button("🗑 Delete", disabled=True, use_container_width=True, key="del_profile_dis")

        selected_profile = get_profile(rp, selected_profile_name)
        if selected_profile is None:
            st.error("Profile not found. Please select another.")
            st.stop()

        if (st.session_state.editor_profile is None
                or st.session_state.editor_profile.get("_editing_name") != selected_profile_name):
            ep = copy.deepcopy(selected_profile)
            ep["_editing_name"] = selected_profile_name
            st.session_state.editor_profile = ep

        ep = st.session_state.editor_profile

        priority_on = st.toggle(
            "Prioritize cases with 3+ Total Machines", value=True, key="priority_toggle",
            help=(
                "ON — Within each group, cases with Total Machines ≥ 3 fill quota first, "
                "then <3 machine cases complete the remainder. "
                "OFF — Fill each group's quota by country availability only, no machine count ordering."
            ),
        )

        with st.expander("✏️ Edit Profile", expanded=False):
            new_name = st.text_input("Profile Name", value=ep["name"], key="ep_name")
            ep["name"] = new_name
            st.markdown("**Groups** — set countries and quota for each group.")
            country_list = MCC_COUNTRIES if rp == "MCC" else CS_COUNTRIES

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
            with save_col:
                if st.button("💾 Update Profile", type="primary", use_container_width=True, key="save_profile"):
                    profile_to_save = {k: v for k, v in ep.items() if not k.startswith("_")}
                    old_name = ep.get("_editing_name", "")
                    if old_name != profile_to_save["name"] and old_name:
                        delete_profile(rp, old_name)
                        if st.session_state.dist_defaults.get(rp) == old_name:
                            set_default(rp, profile_to_save["name"])
                    save_profile(rp, profile_to_save)
                    ep["_editing_name"] = profile_to_save["name"]
                    st.success(f"Profile **{profile_to_save['name']}** saved.")
                    st.rerun()
            with saveas_col:
                new_profile_name = st.text_input("Save as new profile name", key="saveas_name",
                                                  placeholder="New profile name…")
                if st.button("💾 Save as New", use_container_width=True, key="saveas_btn"):
                    if new_profile_name.strip():
                        new_p = {k: v for k, v in ep.items() if not k.startswith("_")}
                        new_p["name"] = new_profile_name.strip()
                        save_profile(rp, new_p)
                        st.success(f"New profile **{new_p['name']}** created.")
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

        st.markdown("")
        if st.button("▶ Apply Batch Distribution", type="primary", use_container_width=True, key="apply_batch"):
            profile_clean = {k: v for k, v in ep.items() if not k.startswith("_")}
            with st.spinner("Applying distribution..."):
                try:
                    batch_df, report, warnings = apply_batch_distribution(
                        result_df, profile_clean, rp, priority_machines=priority_on
                    )
                    st.session_state.batch_result_df = batch_df
                    st.session_state.batch_report = report
                    st.session_state.batch_warnings = warnings
                except Exception as e:
                    st.error(f"Error applying distribution: {e}")
                    st.exception(e)

        if st.session_state.batch_result_df is not None:
            batch_df = st.session_state.batch_result_df
            report    = st.session_state.batch_report
            warnings_list = st.session_state.batch_warnings

            st.markdown("---")
            st.subheader(f"Distribution Results — {report['profile_name']}")
            for w in warnings_list: st.warning(w)

            gr_cols = st.columns(len(report["groups"]))
            for col, grp in zip(gr_cols, report["groups"]):
                overflow_note = (f" (+{grp['filled'] - (grp['quota'] - grp['shortfall'])} overflow)"
                                 if grp["overflow_from"] else "")
                delta_val = "On target" if grp["shortfall"] == 0 else f"-{grp['shortfall']} short"
                col.metric(label=grp["group"], value=f"{grp['filled']} / {grp['quota']}",
                           delta=f"{delta_val}{overflow_note}",
                           delta_color="normal" if grp["shortfall"] == 0 else "inverse")

            t1, t2 = st.columns(2)
            t1.metric("Total Selected for Batch", report["total_selected"])
            t2.metric("Total Backlog (not selected)", report["total_backlog"])

            st.subheader("Batch Preview")
            st.dataframe(batch_df, use_container_width=True, height=350)
            st.download_button(
                label=f"⬇ Download Batch_{rp}_{report['profile_name'].replace(' ','_')}.xlsx",
                data=to_excel(batch_df, sheet_name="Batch"),
                file_name=f"Batch_{rp}_{report['profile_name'].replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary", use_container_width=True, key="dl_batch",
            )

            if not report["backlog_table"].empty:
                st.markdown("")
                st.markdown("""
                <div class="backlog-card">
                    <strong style="color:#F47920;">📋 Backlog Report — Available for Next Batch</strong><br>
                    <span style="font-size:0.85rem;color:#4A4A4A;">
                    Cases remaining after this batch distribution, broken down by country.
                    </span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
                st.dataframe(report["backlog_table"], use_container_width=True, hide_index=True,
                             height=min(35 * len(report["backlog_table"]) + 40, 400))
                st.download_button(
                    "⬇ Download Backlog Report",
                    data=to_excel(report["backlog_table"], sheet_name="Backlog"),
                    file_name=f"Backlog_{rp}_{report['profile_name'].replace(' ','_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_backlog",
                )


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
