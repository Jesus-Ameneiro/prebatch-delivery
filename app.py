import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from pathlib import Path

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Prebatch Generator — Ruvixx",
    page_icon="🔶",
    layout="wide",
)

# ──────────────────────────────────────────────
# Load logo as base64 for HTML embedding
# ──────────────────────────────────────────────
LOGO_B64 = ""
logo_path = Path(__file__).parent / "logo.png"
if logo_path.exists():
    LOGO_B64 = base64.b64encode(logo_path.read_bytes()).decode()

# ──────────────────────────────────────────────
# Ruvixx Branding — Orange & Black Theme
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

    /* ── Top accent stripe ── */
    header[data-testid="stHeader"] {
        background-color: var(--rx-black) !important;
        border-bottom: 3px solid var(--rx-orange) !important;
    }

    /* ── Primary buttons ── */
    button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background-color: var(--rx-orange) !important;
        border-color: var(--rx-orange) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {
        background-color: var(--rx-orange-dark) !important;
        border-color: var(--rx-orange-dark) !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: var(--rx-black) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #D0D0D0 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: var(--rx-orange) !important;
    }
    section[data-testid="stSidebar"] a {
        color: var(--rx-orange) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--rx-mid-gray) !important;
    }
    section[data-testid="stSidebar"] code {
        background-color: var(--rx-dark-gray) !important;
        color: var(--rx-orange) !important;
    }
    section[data-testid="stSidebar"] table {
        font-size: 0.78rem !important;
    }
    section[data-testid="stSidebar"] th {
        background-color: var(--rx-dark-gray) !important;
        color: var(--rx-orange) !important;
        border-color: var(--rx-mid-gray) !important;
    }
    section[data-testid="stSidebar"] td {
        border-color: var(--rx-mid-gray) !important;
    }

    /* ── Title bar ── */
    .rx-title-bar {
        background: linear-gradient(135deg, var(--rx-black) 0%, var(--rx-dark-gray) 100%);
        padding: 1.2rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--rx-orange);
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .rx-title-bar .rx-logo {
        flex-shrink: 0;
    }
    .rx-title-bar .rx-logo img {
        height: 60px;
        width: auto;
    }
    .rx-title-bar .rx-text h1 {
        color: white !important;
        margin: 0 !important;
        font-size: 1.6rem !important;
        line-height: 1.3 !important;
    }
    .rx-title-bar .rx-text p {
        color: #B0B0B0 !important;
        margin: 0.2rem 0 0 0 !important;
        font-size: 0.9rem !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background-color: #FAFAFA;
        border: 1px solid #E0E0E0;
        border-top: 3px solid var(--rx-orange);
        padding: 0.8rem 1rem;
        border-radius: 8px;
    }
    [data-testid="stMetricLabel"] p {
        font-weight: 600 !important;
        color: var(--rx-mid-gray) !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--rx-black) !important;
    }

    /* ── Footer ── */
    .rx-footer {
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 2px solid var(--rx-orange);
        text-align: center;
    }
    .rx-footer p {
        color: var(--rx-mid-gray) !important;
        font-size: 0.8rem !important;
        margin: 0.15rem 0 !important;
    }
    .rx-footer .rx-conf {
        font-weight: 700;
        color: var(--rx-orange) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Title Bar with Logo
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
# Sidebar — Documentation Viewer
# ──────────────────────────────────────────────
with st.sidebar:
    # Sidebar logo
    if LOGO_B64:
        st.markdown(
            f'<div style="text-align:center;padding:0.5rem 0 0.8rem 0;">'
            f'<img src="data:image/png;base64,{LOGO_B64}" style="height:40px;width:auto;">'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### View Documentation")
    st.caption("Reference guide for input files, column mappings, and processing logic.")
    st.markdown("---")

    doc_path = Path(__file__).parent / "DOCUMENTATION.md"
    if doc_path.exists():
        doc_content = doc_path.read_text(encoding="utf-8")
        parts = doc_content.split("\n## ")
        title_block = parts[0]
        st.markdown(title_block, unsafe_allow_html=True)

        for part in parts[1:]:
            lines = part.strip().split("\n", 1)
            heading = lines[0].strip().lstrip("#").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            with st.expander(heading, expanded=False):
                st.markdown(f"## {heading}\n\n{body}", unsafe_allow_html=True)
    else:
        st.warning(
            "Documentation file not found. Ensure `DOCUMENTATION.md` is placed "
            "alongside `app.py` in the repository root."
        )

    st.markdown("---")
    st.caption("Prebatch Generator v1.0  ·  April 2026")


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
        "Pull Conflict Check File",
        type=["csv", "xlsx", "xls"],
        help="Investigation data: machine overviews, notes, company info, addresses, and time spans.",
    )


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


def combine_machine_overviews(pc_lookup, case_ids):
    overviews = []
    for cid in case_ids:
        row = pc_lookup.get(cid)
        if row is not None:
            mo = safe_get(row, "Machine Overview")
            if mo:
                overviews.append(mo)
    if not overviews:
        return ""
    if len(overviews) == 1:
        return overviews[0]
    seen = set()
    unique = []
    for o in overviews:
        if o not in seen:
            seen.add(o)
            unique.append(o)
    return ", ".join(unique)


def combine_investigation_notes(pc_lookup, case_ids):
    notes = []
    for cid in case_ids:
        row = pc_lookup.get(cid)
        if row is not None:
            note = safe_get(row, "Investigation Notes")
            if note:
                notes.append(note)
    if not notes:
        return ""
    if len(notes) == 1:
        return notes[0]
    return "\n\n---\n\n".join(notes)


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


# ──────────────────────────────────────────────
# Core Processing
# ──────────────────────────────────────────────

def process_data(qs_df, pl_df, pc_df, region_code):
    qs_df = clean_df(qs_df)
    pl_df = clean_df(pl_df)
    pc_df = clean_df(pc_df)

    pc_lookup = build_lookup(pc_df, "Case ID")
    pl_lookup = build_lookup(pl_df, "External Case ID")

    output_rows = []
    unmatched_cases = []
    grouped_cases = []

    for _, qs_row in qs_df.iterrows():
        case_id_raw = str(qs_row.get("Case ID", "")).strip()
        if not case_id_raw or case_id_raw.lower() == "nan":
            continue

        case_ids = [cid.strip() for cid in case_id_raw.split(",") if cid.strip()]
        if not case_ids:
            continue

        is_grouped = len(case_ids) > 1
        if is_grouped:
            grouped_cases.append(case_id_raw)

        pc_row = None
        for cid in case_ids:
            if cid in pc_lookup:
                pc_row = pc_lookup[cid]
                break
        if pc_row is None:
            unmatched_cases.append(case_id_raw)
            pc_row = pd.Series(dtype=str)

        if is_grouped:
            machine_overview = combine_machine_overviews(pc_lookup, case_ids)
            investigation_notes = combine_investigation_notes(pc_lookup, case_ids)
        else:
            machine_overview = safe_get(pc_row, "Machine Overview")
            investigation_notes = safe_get(pc_row, "Investigation Notes")

        actionable_domains = safe_get(qs_row, "Actionable Domains")
        if not actionable_domains:
            actionable_domains = safe_get(pc_row, "Actionable Domains")

        website = safe_get(qs_row, "Websites")
        if not website:
            website = safe_get(pc_row, "Website")

        if region_code == "MCC":
            last_updated = get_latest_updated(pl_lookup, case_ids)
            row_data = {
                "Date Added to This Sheet": "",
                "Is Multi-National": "",
                "Machine Overview": machine_overview,
                "Investigation Notes": investigation_notes,
                "Case ID": case_id_raw,
                "Company Name": safe_get(pc_row, "Company Name"),
                "Entity Name": safe_get(qs_row, "Company Name"),
                "Cylynt Organization Name": safe_get(pc_row, "Cylynt Organization Name"),
                "Industry": safe_get(pc_row, "Industry"),
                "Address": safe_get(pc_row, "Address"),
                "Countries": safe_get(pc_row, "Countries"),
                "Estimated Case Value": "",
                "Case Tier": safe_get(qs_row, "Case Tier"),
                "Case Category": safe_get(qs_row, "[Cfa]-Category"),
                "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
                "# All Time Machines": safe_get(qs_row, "Total Machines"),
                "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
                "# Difference": safe_get(qs_row, "[CFa]-Difference"),
                "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
                "First Event": safe_get(qs_row, "First Event"),
                "Last Event": safe_get(qs_row, "Last Event"),
                "Time Span": safe_get(pc_row, "Time Span"),
                "Generic Email Address": "",
                "Actionable Domains": actionable_domains,
                "Website": website,
                "Last Updated At": last_updated,
                "NNS License Count": "",
            }
        else:
            row_data = {
                "Date Added to This Sheet": "",
                "Is Multi-National": "",
                "Machine Overview": machine_overview,
                "Investigation Notes": investigation_notes,
                "Case ID": case_id_raw,
                "Company Name": safe_get(pc_row, "Company Name"),
                "Entity Name": safe_get(qs_row, "Company Name"),
                "Cylynt Organization Name": safe_get(pc_row, "Cylynt Organization Name"),
                "Industry": safe_get(pc_row, "Industry"),
                "Addresses": safe_get(pc_row, "Address"),
                "Country": safe_get(pc_row, "Countries"),
                "Case Tier": safe_get(qs_row, "Case Tier"),
                "Case Category": safe_get(qs_row, "[Cfa]-Category"),
                "Actionable Category": safe_get(qs_row, "[Cfa]-ActionableCategory"),
                "# All Time Machines": safe_get(qs_row, "Total Machines"),
                "# Actionable Machines": safe_get(qs_row, "Actionable Machines"),
                "# Difference": safe_get(qs_row, "[CFa]-Difference"),
                "Actionable Machine IDs": safe_get(qs_row, "Approved Machines"),
                "First Event": safe_get(qs_row, "First Event"),
                "Last Event": safe_get(qs_row, "Last Event"),
                "Time Span": safe_get(pc_row, "Time Span"),
                "Generic Email Address": "",
                "Actionable Domains": actionable_domains,
                "Website": website,
            }

        output_rows.append(row_data)

    target_cols = MCC_COLUMNS if region_code == "MCC" else CS_COLUMNS
    result_df = pd.DataFrame(output_rows, columns=target_cols)
    return result_df, unmatched_cases, grouped_cases


def to_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Prebatch")
        ws = writer.sheets["Prebatch"]
        for i, col in enumerate(df.columns, 1):
            max_len = max(len(str(col)), 12)
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(
                max_len + 2, 40
            )
    return buf.getvalue()


# ──────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────
if "result_df" not in st.session_state:
    st.session_state.result_df = None
    st.session_state.unmatched = []
    st.session_state.grouped = []
    st.session_state.region_processed = None

# ──────────────────────────────────────────────
# Process & Results
# ──────────────────────────────────────────────
st.divider()

if qs_file and pl_file and pc_file:
    if st.button("Generate Prebatch File", type="primary", use_container_width=True):
        with st.spinner("Processing files..."):
            try:
                qs_df = read_file(qs_file)
                pl_df = read_file(pl_file)
                pc_df = read_file(pc_file)
                result_df, unmatched, grouped = process_data(
                    qs_df, pl_df, pc_df, region_code
                )
                st.session_state.result_df = result_df
                st.session_state.unmatched = unmatched
                st.session_state.grouped = grouped
                st.session_state.region_processed = region_code
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                st.exception(e)

    if st.session_state.result_df is not None:
        result_df = st.session_state.result_df
        unmatched = st.session_state.unmatched
        grouped = st.session_state.grouped
        rp = st.session_state.region_processed

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Cases", len(result_df))
        m2.metric("Grouped Entities", len(grouped))
        m3.metric("Unmatched", len(unmatched))

        if unmatched or grouped:
            d1, d2 = st.columns(2)
            with d1:
                if unmatched:
                    with st.expander(f"Unmatched Cases ({len(unmatched)})"):
                        st.write("QS Case IDs with no Pull Conflict match:")
                        for c in unmatched:
                            st.code(c)
            with d2:
                if grouped:
                    with st.expander(f"Grouped Entries ({len(grouped)})"):
                        st.write("Multi-Case IDs — review Machine Overview if needed:")
                        for c in grouped:
                            st.code(c)

        st.subheader("Output Preview")
        st.dataframe(result_df, use_container_width=True, height=420)

        excel_bytes = to_excel(result_df)
        st.download_button(
            label=f"Download Prebatch_{rp}.xlsx",
            data=excel_bytes,
            file_name=f"Prebatch_{rp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

else:
    missing = []
    if not qs_file:
        missing.append("QS Delivery ID")
    if not pl_file:
        missing.append("PL Batch")
    if not pc_file:
        missing.append("Pull Conflict Check")
    st.info(f"Upload the remaining file(s) to proceed: **{', '.join(missing)}**")


# ──────────────────────────────────────────────
# Footer — Confidential Disclosure
# ──────────────────────────────────────────────
st.markdown("""
<div class="rx-footer">
    <p class="rx-conf">CONFIDENTIAL — FOR INTERNAL USE ONLY</p>
    <p>This tool and all data processed through it are the proprietary property of Ruvixx
    and its clients. Unauthorized access, distribution, or reproduction is strictly prohibited.</p>
    <p>&copy; 2026 Ruvixx &mdash; Case Investigation Operations &middot; Trimble SketchUp License Compliance</p>
</div>
""", unsafe_allow_html=True)
