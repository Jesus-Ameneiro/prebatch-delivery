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

    /* ── Hide toolbar items: Star, Edit, GitHub (keep Share + 3-dots) ── */
    [data-testid="stActionButton"],
    [data-testid="stToolbarActionButton"][aria-label="Edit source"],
    header a[href*="github"],
    [data-testid="stAppDeployButton"],
    [data-testid="stSourceButton"] {
        display: none !important;
    }
    /* Fallback: hide star/edit/github by common Streamlit toolbar structure */
    header button[title="Favorite"],
    header button[title="Star"],
    header button[title="Edit"],
    header button[title="Edit source"],
    header button[title="Fork this app"],
    header a[title*="GitHub"],
    header a[title*="github"],
    header a[title="View app source"] {
        display: none !important;
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

    /* ── Sidebar doc button ── */
    section[data-testid="stSidebar"] .rx-doc-btn {
        display: block !important;
        text-align: center !important;
        padding: 0.5rem 1rem !important;
        background-color: #F47920 !important;
        border: 2px solid #F47920 !important;
        border-radius: 6px !important;
        text-decoration: none !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn:hover {
        background-color: #D4611A !important;
        border-color: #D4611A !important;
    }
    section[data-testid="stSidebar"] .rx-doc-btn .rx-doc-btn-text {
        color: #FFFFFF !important;
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.3px !important;
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
# Sidebar — Logo + Documentation Button
# ──────────────────────────────────────────────

# Load documentation PDF as base64
DOC_B64 = ""
doc_pdf_path = Path(__file__).parent / "DOCUMENTATION.pdf"
if doc_pdf_path.exists():
    DOC_B64 = base64.b64encode(doc_pdf_path.read_bytes()).decode()

with st.sidebar:
    # Sidebar logo — centered with padding
    if LOGO_B64:
        st.markdown(
            f'<div style="text-align:center;padding:1.2rem 0 0.6rem 0;">'
            f'<img src="data:image/png;base64,{LOGO_B64}" style="height:36px;width:auto;">'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<hr style="margin:0.4rem 0 1.2rem 0;border:none;border-top:1px solid #3A3A3A;">',
        unsafe_allow_html=True,
    )

    # Documentation button — opens PDF in new tab
    if DOC_B64:
        pdf_data_uri = f"data:application/pdf;base64,{DOC_B64}"
        st.markdown(
            '<p style="color:#B0B0B0 !important;font-size:0.82rem;margin:0 0 0.5rem 0;'
            'font-weight:600;letter-spacing:0.2px;">See Documentation</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<a href="{pdf_data_uri}" target="_blank" rel="noopener noreferrer"'
            f' class="rx-doc-btn">'
            f'<span class="rx-doc-btn-text">Open Reference Guide</span></a>',
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "DOCUMENTATION.pdf not found. Place it alongside app.py in the repo root."
        )

    st.markdown(
        '<hr style="margin:1.2rem 0 0.8rem 0;border:none;border-top:1px solid #3A3A3A;">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align:center;font-size:0.72rem;color:#666 !important;margin:0;">'
        'Prebatch Generator v1.0 &middot; April 2026</p>',
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
        help="Investigation data: machine overviews, notes, entity details, machine counts, and case attribution.",
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
    if len(overviews) == 1:
        return overviews[0]
    seen = set()
    unique = []
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

def process_data(qs_df, pl_df, cc_df, region_code):
    """Merge three source files into the Prebatch output format.

    Data-source mapping (updated for Conflict Check structure):
        Conflict Check →  Machine Overview, Investigation Notes, Company Name,
                           Pleteo Entity Name (→ Entity Name), Cylynt Org Name,
                           Industry, Address, Countries, Time Span, Is Multi National,
                           Generic Email Addresses, Actionable Domains, Website
        QS Delivery    →  Case ID (grouped), Case Tier, Categories, machine counts/IDs,
                           First/Last Event (aggregated for grouped entities)
        PL Batch       →  Last Updated At (MCC only)
    """
    qs_df = clean_df(qs_df)
    pl_df = clean_df(pl_df)
    cc_df = clean_df(cc_df)

    cc_lookup = build_lookup(cc_df, "Case ID")
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

        # Find Conflict Check row
        cc_row = None
        for cid in case_ids:
            if cid in cc_lookup:
                cc_row = cc_lookup[cid]
                break
        if cc_row is None:
            unmatched_cases.append(case_id_raw)
            cc_row = pd.Series(dtype=str)

        # Machine Overview & Investigation Notes (combine for grouped)
        if is_grouped:
            machine_overview = combine_machine_overviews(cc_lookup, case_ids)
            investigation_notes = combine_investigation_notes(cc_lookup, case_ids)
        else:
            machine_overview = safe_get(cc_row, "Machine Overview")
            investigation_notes = safe_get(cc_row, "Investigation Notes")

        # Actionable Domains — CC primary, QS fallback
        actionable_domains = safe_get(cc_row, "Actionable Domains")
        if not actionable_domains:
            actionable_domains = safe_get(qs_row, "Actionable Domains")

        # Website — CC primary, QS fallback
        website = safe_get(cc_row, "Website")
        if not website:
            website = safe_get(qs_row, "Websites")

        # Entity Name — CC primary, QS Company Name as fallback
        entity_name = safe_get(cc_row, "Pleteo Entity Name")
        if not entity_name:
            entity_name = safe_get(qs_row, "Company Name")

        # ── Build output row ──
        if region_code == "MCC":
            last_updated = get_latest_updated(pl_lookup, case_ids)
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
                "First Event": safe_get(qs_row, "First Event"),
                "Last Event": safe_get(qs_row, "Last Event"),
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
                "First Event": safe_get(qs_row, "First Event"),
                "Last Event": safe_get(qs_row, "Last Event"),
                "Time Span": safe_get(cc_row, "Time Span"),
                "Generic Email Address": safe_get(cc_row, "Generic Email Addresses"),
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
                cc_df = read_file(pc_file)
                result_df, unmatched, grouped = process_data(
                    qs_df, pl_df, cc_df, region_code
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
                        st.write("QS Case IDs with no Conflict Check match:")
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
        missing.append("Conflict Check")
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
