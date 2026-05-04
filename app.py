import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime
import re

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Prebatch Generator — Ruvixx",
    page_icon="🔶",
    layout="wide",
)

# ──────────────────────────────────────────────
# Load logo as base64
# ──────────────────────────────────────────────
LOGO_B64 = ""
logo_path = Path(__file__).parent / "logo.png"
if logo_path.exists():
    LOGO_B64 = base64.b64encode(logo_path.read_bytes()).decode()

# ──────────────────────────────────────────────
# Ruvixx Branding
# ──────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --rx-orange: #F47920;
        --rx-orange-dark: #D4611A;
        --rx-black: #1A1A1A;
        --rx-dark-gray: #2D2D2D;
        --rx-mid-gray: #4A4A4A;
    }

    header[data-testid="stHeader"] {
        background-color: var(--rx-black) !important;
        border-bottom: 3px solid var(--rx-orange) !important;
    }

    /* ── Hide toolbar items ── */
    [data-testid="stActionButton"],
    [data-testid="stToolbarActionButton"][aria-label="Edit source"],
    header a[href*="github"],
    [data-testid="stAppDeployButton"],
    [data-testid="stSourceButton"] { display: none !important; }
    header button[title="Favorite"], header button[title="Star"],
    header button[title="Edit"], header button[title="Edit source"],
    header button[title="Fork this app"],
    header a[title*="GitHub"], header a[title*="github"],
    header a[title="View app source"] { display: none !important; }

    /* ── Buttons ── */
    button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background-color: var(--rx-orange) !important;
        border-color: var(--rx-orange) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
        background-color: var(--rx-orange-dark) !important;
        border-color: var(--rx-orange-dark) !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] { background-color: var(--rx-black) !important; }
    section[data-testid="stSidebar"] * { color: #D0D0D0 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 { color: var(--rx-orange) !important; }
    section[data-testid="stSidebar"] a { color: var(--rx-orange) !important; }
    section[data-testid="stSidebar"] hr { border-color: #3A3A3A !important; }
    section[data-testid="stSidebar"] code {
        background-color: var(--rx-dark-gray) !important;
        color: var(--rx-orange) !important;
    }

    /* ── Title bar ── */
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

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background-color: #FAFAFA; border: 1px solid #E0E0E0;
        border-top: 3px solid var(--rx-orange); padding: 0.8rem 1rem; border-radius: 8px;
    }
    [data-testid="stMetricLabel"] p { font-weight: 600 !important; color: var(--rx-mid-gray) !important; }
    [data-testid="stMetricValue"] { color: var(--rx-black) !important; }

    /* ── Sidebar doc button ── */
    section[data-testid="stSidebar"] .rx-doc-btn {
        display: block !important; text-align: center !important;
        padding: 0.5rem 1rem !important; background-color: #F47920 !important;
        border: 2px solid #F47920 !important; border-radius: 6px !important;
        text-decoration: none !important; margin: 0 !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn:hover {
        background-color: #D4611A !important; border-color: #D4611A !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn .rx-doc-btn-text {
        color: #FFFFFF !important; font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 600 !important; font-size: 0.82rem !important; letter-spacing: 0.3px !important;
    }

    /* ── Validation badges ── */
    .val-ok   { color: #2E7D32; font-weight: 600; }
    .val-warn { color: #E65100; font-weight: 600; }
    .val-err  { color: #B71C1C; font-weight: 600; }

    /* ── History entries ── */
    .hist-entry {
        background: #FAFAFA; border: 1px solid #E8E8E8;
        border-left: 4px solid var(--rx-orange);
        padding: 0.6rem 0.8rem; border-radius: 6px; margin-bottom: 0.5rem;
    }

    /* ── Footer ── */
    .rx-footer { margin-top: 3rem; padding: 1rem 0; border-top: 2px solid var(--rx-orange); text-align: center; }
    .rx-footer p { color: var(--rx-mid-gray) !important; font-size: 0.8rem !important; margin: 0.15rem 0 !important; }
    .rx-footer .rx-conf {
        font-weight: 700; color: var(--rx-orange) !important; text-transform: uppercase;
        letter-spacing: 0.5px; font-size: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Title Bar
# ──────────────────────────────────────────────
logo_html = ""
if LOGO_B64:
    logo_html = f'<div class="rx-logo"><img src="data:image/png;base64,{LOGO_B64}" alt="Ruvixx"></div>'

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
# Session State Initialization
# ──────────────────────────────────────────────
if "result_df" not in st.session_state:
    st.session_state.result_df = None
    st.session_state.unmatched = []
    st.session_state.grouped = []
    st.session_state.duplicates = []
    st.session_state.region_processed = None
    st.session_state.generation_log = []   # list of log entry dicts


# ──────────────────────────────────────────────
# Sidebar — Logo + Docs + History
# ──────────────────────────────────────────────
DOC_B64 = ""
doc_pdf_path = Path(__file__).parent / "DOCUMENTATION.pdf"
if doc_pdf_path.exists():
    DOC_B64 = base64.b64encode(doc_pdf_path.read_bytes()).decode()

with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f'<div style="text-align:center;padding:1.2rem 0 0.6rem 0;">'
            f'<img src="data:image/png;base64,{LOGO_B64}" style="height:36px;width:auto;"></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="margin:0.4rem 0 1.2rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    if DOC_B64:
        pdf_data_uri = f"data:application/pdf;base64,{DOC_B64}"
        st.markdown(
            '<p style="color:#B0B0B0 !important;font-size:0.82rem;margin:0 0 0.5rem 0;'
            'font-weight:600;letter-spacing:0.2px;">See Documentation</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<a href="{pdf_data_uri}" target="_blank" rel="noopener noreferrer" class="rx-doc-btn">'
            f'<span class="rx-doc-btn-text">Open Reference Guide</span></a>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("DOCUMENTATION.pdf not found in repo root.")

    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)

    # ── Generation History ──
    st.markdown("### Generation History")
    log = st.session_state.generation_log

    if not log:
        st.caption("No generations yet this session.")
    else:
        for entry in reversed(log):
            with st.expander(
                f"{'🟠' if entry['region'] == 'MCC' else '🔵'} "
                f"{entry['region']} · {entry['timestamp']} · {entry['total']} cases",
                expanded=False,
            ):
                st.caption(f"Region: **{entry['region']}**")
                st.caption(f"Generated: {entry['timestamp']}")
                st.caption(f"Total cases: {entry['total']} | Grouped: {entry['grouped']} | Unmatched: {entry['unmatched']} | Duplicates: {entry['duplicates']}")
                if entry["cases"]:
                    case_df = pd.DataFrame(entry["cases"], columns=["Case ID", "Entity Name"])
                    st.dataframe(case_df, use_container_width=True, hide_index=True, height=200)

        if st.button("Clear History", use_container_width=True):
            st.session_state.generation_log = []
            st.rerun()

    st.markdown('<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;font-size:0.72rem;color:#666 !important;margin:0;">'
        'Prebatch Generator v1.1 &middot; May 2026</p>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# Region Toggle
# ──────────────────────────────────────────────
region = st.radio(
    "Select Region",
    options=["MCC (México Central Caribe)", "CS (Cono Sur)"],
    horizontal=True,
    help="MCC: Mexico, Central America, Caribbean  —  CS: South America (Argentina, Chile, Peru, Colombia, Bolivia, Ecuador)",
)
region_code = "MCC" if "MCC" in region else "CS"

st.divider()

# ──────────────────────────────────────────────
# File Uploaders
# ──────────────────────────────────────────────
st.subheader("Upload Source Files")
col1, col2, col3 = st.columns(3)

with col1:
    qs_file = st.file_uploader(
        "QS Delivery ID File",
        type=["csv", "xlsx", "xls"],
        help="Contains grouped Case IDs, entity names, aggregated machine counts, and event dates.",
    )

with col2:
    pl_file = st.file_uploader(
        "PL Batch File (Pleteo Export)",
        type=["csv", "xlsx", "xls"],
        help="CRM export providing the 'Updated' timestamp for Last Updated At (MCC).",
    )

with col3:
    pc_file = st.file_uploader(
        "Conflict Check File",
        type=["csv", "xlsx", "xls"],
        help="Investigation data: machine overviews, notes, entity details, and case attribution.",
    )


# ──────────────────────────────────────────────
# File Signature Definitions
# ──────────────────────────────────────────────
QS_REQUIRED   = {"Case ID", "Case Tier", "Total Machines", "Actionable Machines", "Approved Machines", "First Event", "Last Event"}
PL_REQUIRED   = {"External Case ID", "Updated"}
CC_REQUIRED   = {"Case ID", "Machine Overview", "Investigation Notes", "Pleteo Entity Name", "Company Name", "Actionable Domains"}


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def read_file(uploaded_file):
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
    else:
        return pd.read_excel(uploaded_file, dtype=str, keep_default_na=False)


def clean_df(df):
    df.columns = [str(c).strip() for c in df.columns]
    df = df.replace("", pd.NA)
    df = df.dropna(how="all")
    df = df.fillna("")
    return df


def validate_file(df, required_cols, label):
    """Return (is_valid, missing_cols, extra_warning) for a file."""
    actual = set(df.columns)
    missing = required_cols - actual
    return len(missing) == 0, missing


def normalize_date(value: str) -> str:
    """
    Parse a date/datetime string and return it in YYYY-MM-DD HH:MM:SS format.
    Returns the original string unchanged if parsing fails.
    """
    if not value or value.strip() == "":
        return value
    v = value.strip()

    # Already correct format
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", v):
        return v

    # Try common patterns
    formats = [
        "%m/%d/%Y %H:%M",       # 5/14/2019 0:00
        "%m/%d/%Y %H:%M:%S",    # 5/14/2019 0:00:00
        "%Y-%m-%dT%H:%M:%S",    # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(v, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # Fallback: let pandas try
    try:
        dt = pd.to_datetime(v)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return value  # return unchanged if all parsing fails


def safe_get(source, col, default=""):
    if isinstance(source, pd.Series) and col in source.index:
        val = source[col]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return str(val).strip()
    return default


def build_lookup(df, key_col):
    lookup = {}
    for _, row in df.iterrows():
        key = str(row.get(key_col, "")).strip()
        if key and key.lower() != "nan":
            lookup[key] = row
    return lookup


def get_latest_updated(pl_lookup, case_ids):
    latest = ""
    for cid in case_ids:
        row = pl_lookup.get(cid)
        if row is not None:
            updated = safe_get(row, "Updated")
            if updated and updated > latest:
                latest = updated
    return latest


def combine_machine_overviews(cc_lookup, case_ids):
    overviews = []
    for cid in case_ids:
        row = cc_lookup.get(cid)
        if row is not None:
            mo = safe_get(row, "Machine Overview")
            if mo:
                overviews.append(mo)
    if not overviews:
        return ""
    seen, unique = set(), []
    for o in overviews:
        if o not in seen:
            seen.add(o)
            unique.append(o)
    return ", ".join(unique)


def combine_investigation_notes(cc_lookup, case_ids):
    notes = []
    for cid in case_ids:
        row = cc_lookup.get(cid)
        if row is not None:
            note = safe_get(row, "Investigation Notes")
            if note:
                notes.append(note)
    if not notes:
        return ""
    return notes[0] if len(notes) == 1 else "\n\n---\n\n".join(notes)


# ──────────────────────────────────────────────
# Output Column Definitions
# ──────────────────────────────────────────────
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

DATE_COLUMNS = {"First Event", "Last Event", "Last Updated At"}


# ──────────────────────────────────────────────
# Core Processing
# ──────────────────────────────────────────────

def process_data(qs_df, pl_df, cc_df, region_code):
    qs_df = clean_df(qs_df)
    pl_df = clean_df(pl_df)
    cc_df = clean_df(cc_df)

    cc_lookup = build_lookup(cc_df, "Case ID")
    pl_lookup = build_lookup(pl_df, "External Case ID")

    output_rows = []
    unmatched_cases = []
    grouped_cases = []
    seen_case_ids = {}      # case_id_raw → first index it appeared
    duplicate_cases = []

    for idx, (_, qs_row) in enumerate(qs_df.iterrows()):
        case_id_raw = str(qs_row.get("Case ID", "")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue

        # ── Deduplication check ──
        if case_id_raw in seen_case_ids:
            duplicate_cases.append(case_id_raw)
            continue   # skip duplicate rows; first occurrence wins
        seen_case_ids[case_id_raw] = idx

        case_ids = [cid.strip() for cid in case_id_raw.split(",") if cid.strip()]
        if not case_ids:
            continue

        is_grouped = len(case_ids) > 1
        if is_grouped:
            grouped_cases.append(case_id_raw)

        cc_row = None
        for cid in case_ids:
            if cid in cc_lookup:
                cc_row = cc_lookup[cid]
                break
        if cc_row is None:
            unmatched_cases.append(case_id_raw)
            cc_row = pd.Series(dtype=str)

        if is_grouped:
            machine_overview = combine_machine_overviews(cc_lookup, case_ids)
            investigation_notes = combine_investigation_notes(cc_lookup, case_ids)
        else:
            machine_overview = safe_get(cc_row, "Machine Overview")
            investigation_notes = safe_get(cc_row, "Investigation Notes")

        actionable_domains = safe_get(cc_row, "Actionable Domains") or safe_get(qs_row, "Actionable Domains")
        website = safe_get(cc_row, "Website") or safe_get(qs_row, "Websites")

        entity_name = safe_get(cc_row, "Pleteo Entity Name") or safe_get(qs_row, "Company Name")

        # ── Date normalization ──
        first_event   = normalize_date(safe_get(qs_row, "First Event"))
        last_event    = normalize_date(safe_get(qs_row, "Last Event"))

        if region_code == "MCC":
            last_updated_raw = get_latest_updated(pl_lookup, case_ids)
            last_updated = normalize_date(last_updated_raw)
            row_data = {
                "Date Added to This Sheet": "",
                "Is Multi-National": safe_get(cc_row, "Is Multi National"),
                "Machine Overview": machine_overview,
                "Investigation Notes": investigation_notes,
                "Case ID": case_id_raw,
                "Company Name": safe_get(cc_row, "Company Name"),
                "Entity Name": entity_name,
                "Cylynt Organization Name": safe_get(cc_row, "Cylynt Organization Name"),
                "Industry": safe_get(cc_row, "Industry"),
                "Address": safe_get(cc_row, "Address"),
                "Countries": safe_get(cc_row, "Countries"),
                "Estimated Case Value": "",
                "Case Tier": safe_get(qs_row, "Case Tier"),
                "Case Category": safe_get(qs_row, "[Cfa]-Category"),
                "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
                "# All Time Machines": safe_get(qs_row, "Total Machines"),
                "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
                "# Difference": safe_get(qs_row, "[CFa]-Difference"),
                "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
                "First Event": first_event,
                "Last Event": last_event,
                "Time Span": safe_get(cc_row, "Time Span"),
                "Generic Email Address": safe_get(cc_row, "Generic Email Addresses"),
                "Actionable Domains": actionable_domains,
                "Website": website,
                "Last Updated At": last_updated,
                "NNS License Count": "",
            }
        else:  # CS
            row_data = {
                "Date Added to This Sheet": "",
                "Is Multi-National": safe_get(cc_row, "Is Multi National"),
                "Machine Overview": machine_overview,
                "Investigation Notes": investigation_notes,
                "Case ID": case_id_raw,
                "Company Name": safe_get(cc_row, "Company Name"),
                "Entity Name": entity_name,
                "Cylynt Organization Name": safe_get(cc_row, "Cylynt Organization Name"),
                "Industry": safe_get(cc_row, "Industry"),
                "Addresses": safe_get(cc_row, "Address"),
                "Country": safe_get(cc_row, "Countries"),
                "Case Tier": safe_get(qs_row, "Case Tier"),
                "Case Category": safe_get(qs_row, "[Cfa]-Category"),
                "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
                "# All Time Machines": safe_get(qs_row, "Total Machines"),
                "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
                "# Difference": safe_get(qs_row, "[CFa]-Difference"),
                "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
                "First Event": first_event,
                "Last Event": last_event,
                "Time Span": safe_get(cc_row, "Time Span"),
                "Generic Email Address": safe_get(cc_row, "Generic Email Addresses"),
                "Actionable Domains": actionable_domains,
                "Website": website,
            }

        output_rows.append(row_data)

    target_cols = MCC_COLUMNS if region_code == "MCC" else CS_COLUMNS
    result_df = pd.DataFrame(output_rows, columns=target_cols)
    return result_df, unmatched_cases, grouped_cases, duplicate_cases


def to_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Prebatch")
        ws = writer.sheets["Prebatch"]
        for i, col in enumerate(df.columns, 1):
            max_len = max(len(str(col)), 12)
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(max_len + 2, 40)
    return buf.getvalue()


# ──────────────────────────────────────────────
# Pre-validation Panel
# ──────────────────────────────────────────────
def show_validation(uploaded_file, required_cols, label):
    """Read the file and render a compact validation result. Returns (df, is_valid)."""
    if uploaded_file is None:
        return None, False
    try:
        df = read_file(uploaded_file)
        df_clean = clean_df(df)
        is_valid, missing = validate_file(df_clean, required_cols, label)
        if is_valid:
            st.markdown(f'<span class="val-ok">✔ {label}</span> — {len(df_clean)} rows, {len(df_clean.columns)} columns', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="val-err">✘ {label}</span> — missing columns: `{"`, `".join(sorted(missing))}`', unsafe_allow_html=True)
        return df_clean, is_valid
    except Exception as e:
        st.markdown(f'<span class="val-err">✘ {label}</span> — could not read file: {e}', unsafe_allow_html=True)
        return None, False


# ──────────────────────────────────────────────
# Main Processing Area
# ──────────────────────────────────────────────
st.divider()

all_uploaded = qs_file and pl_file and pc_file

# Show validation status as soon as files are uploaded
if any([qs_file, pl_file, pc_file]):
    with st.expander("File Validation", expanded=True):
        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            qs_df_validated, qs_ok = show_validation(qs_file, QS_REQUIRED, "QS Delivery ID")
        with vc2:
            pl_df_validated, pl_ok = show_validation(pl_file, PL_REQUIRED, "PL Batch")
        with vc3:
            cc_df_validated, cc_ok = show_validation(pc_file, CC_REQUIRED, "Conflict Check")

    all_valid = all_uploaded and qs_ok and pl_ok and cc_ok
else:
    all_valid = False
    qs_df_validated = pl_df_validated = cc_df_validated = None

# Generate button
if all_uploaded:
    if not all_valid:
        st.warning("One or more files failed validation. Review the column errors above before generating.")

    if st.button("Generate Prebatch File", type="primary", use_container_width=True, disabled=not all_valid):
        with st.spinner("Processing files..."):
            try:
                result_df, unmatched, grouped, duplicates = process_data(
                    qs_df_validated, pl_df_validated, cc_df_validated, region_code
                )
                st.session_state.result_df = result_df
                st.session_state.unmatched = unmatched
                st.session_state.grouped = grouped
                st.session_state.duplicates = duplicates
                st.session_state.region_processed = region_code

                # ── Append to generation log ──
                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "region": region_code,
                    "total": len(result_df),
                    "grouped": len(grouped),
                    "unmatched": len(unmatched),
                    "duplicates": len(duplicates),
                    "cases": [
                        (row["Case ID"], row.get("Entity Name", ""))
                        for _, row in result_df.iterrows()
                    ],
                }
                st.session_state.generation_log.append(log_entry)

            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                st.exception(e)

else:
    missing = []
    if not qs_file: missing.append("QS Delivery ID")
    if not pl_file: missing.append("PL Batch")
    if not pc_file: missing.append("Conflict Check")
    st.info(f"Upload the remaining file(s) to proceed: **{', '.join(missing)}**")


# ──────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────
if st.session_state.result_df is not None:
    result_df = st.session_state.result_df
    unmatched  = st.session_state.unmatched
    grouped    = st.session_state.grouped
    duplicates = st.session_state.duplicates
    rp         = st.session_state.region_processed

    st.divider()

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases",      len(result_df))
    m2.metric("Grouped Entities", len(grouped))
    m3.metric("Unmatched",        len(unmatched))
    m4.metric("Duplicates Removed", len(duplicates))

    # Diagnostic expanders
    diag_cols = st.columns(3)
    with diag_cols[0]:
        if unmatched:
            with st.expander(f"⚠ Unmatched Cases ({len(unmatched)})"):
                st.caption("QS Case IDs with no Conflict Check match. These rows are included with blank CC fields.")
                for c in unmatched:
                    st.code(c)
    with diag_cols[1]:
        if grouped:
            with st.expander(f"ℹ Grouped Entries ({len(grouped)})"):
                st.caption("Multi-Case IDs — Machine Overview and Notes were combined.")
                for c in grouped:
                    st.code(c)
    with diag_cols[2]:
        if duplicates:
            with st.expander(f"🚫 Duplicates Removed ({len(duplicates)})"):
                st.caption("These Case IDs appeared more than once in the QS file. Only the first occurrence was kept.")
                for c in duplicates:
                    st.code(c)

    # Preview
    st.subheader("Output Preview")
    st.dataframe(result_df, use_container_width=True, height=420)

    # Download
    excel_bytes = to_excel(result_df)
    st.download_button(
        label=f"Download Prebatch_{rp}.xlsx",
        data=excel_bytes,
        file_name=f"Prebatch_{rp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
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
