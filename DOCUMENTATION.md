# Prebatch / Precheck File Generator — Documentation

**Tool Version:** 1.0  
**Maintained by:** Ruvixx — Case Investigation Operations  
**Regions Supported:** MCC (México Central Caribe) · CS (Cono Sur)

---

## 1. Purpose

The Prebatch Generator automates the creation of the **Prebatch/Precheck file** — the final structured spreadsheet uploaded to the Master Sheet for Trimble SketchUp License Compliance operations.

Previously, this file was assembled manually by cross-referencing three separate data sources, copying columns between spreadsheets, and reconciling grouped entity cases by hand. This tool replaces that workflow with a single upload-and-generate step.

---

## 2. Overview of the Process

```
┌─────────────────────┐
│  QS Delivery ID     │──┐
│  (Entity grouping)  │  │
└─────────────────────┘  │
                         │    ┌───────────────────────┐
┌─────────────────────┐  ├───▶│   Prebatch Generator  │───▶  Prebatch.xlsx
│  PL Batch File      │──┤    │   (Streamlit App)     │      (Final Output)
│  (Pleteo CRM export)│  │    └───────────────────────┘
└─────────────────────┘  │
                         │
┌─────────────────────┐  │
│  Pull Conflict Check│──┘
│  (Investigation data)│
└─────────────────────┘
```

Three input files are uploaded into the app. The tool joins them on the **Case ID** field (e.g., `1026414#1`), maps each column to the correct output position based on the selected region (MCC or CS), and produces a downloadable `.xlsx` file matching the Master Sheet structure.

---

## 3. Input Files — Detailed Breakdown

### 3.1 QS Delivery ID File

**Role:** The master list and entity grouping authority. This file defines which cases are included in the batch and how multi-case entities are grouped.

**Key columns consumed by the tool:**

| QS Column | Maps To (Output) | Notes |
|---|---|---|
| `Case ID` | `Case ID` | The **join key** across all files. May contain multiple IDs separated by commas for grouped entities (e.g., `4392588#1,1859189#1`). |
| `Company Name` | `Entity Name` | The QS "Company Name" becomes the output's "Entity Name" — the legal/formal entity name used for the Master Sheet. |
| `Case Tier` | `Case Tier` | Tier classification (1, 2, or 3). |
| `[Cfa]-Category` | `Case Category` | Numeric category value. |
| `[Cfa]-ActionableCategory` | `Actionable Category` | Numeric actionable classification. |
| `Total Machines` | `# All Time Machines` | Aggregated total machine count across all cases in a group. |
| `Actionable Machines` | `# Actionable Machines` | Count of machines meeting actionable criteria. |
| `[CFa]-Difference` | `# Difference` | Difference between total and actionable machines. |
| `Approved Machines` | `Actionable Machine IDs` | Comma-separated list of approved machine IDs. For grouped cases, this is the combined list. |
| `First Event` | `First Event` | Earliest event date across all cases in the group. |
| `Last Event` | `Last Event` | Most recent event date across all cases in the group. |
| `Actionable Domains` | `Actionable Domains` | Primary source for domain list. Falls back to Pull Conflict if empty. |
| `Websites` | `Website` | Primary source for website URL. Falls back to Pull Conflict if empty. |
| `case_tags` | *(internal use)* | Used to detect "Multinational Organization" flag (reserved for future use). |

**Why QS is authoritative for machine counts and dates:** For grouped entities (multiple Case IDs in one row), the QS file contains the pre-aggregated totals across all constituent cases. The Pull Conflict file only has per-case data. Using QS ensures the output reflects the correct combined numbers.

---

### 3.2 PL Batch File (Pleteo CRM Export)

**Role:** Provides the CRM timestamp metadata. Its primary contribution is the `Updated` field, which populates the `Last Updated At` column in the MCC output.

**Key columns consumed by the tool:**

| PL Batch Column | Maps To (Output) | Notes |
|---|---|---|
| `External Case ID` | *(join key)* | Used to match rows to the QS Case ID. This is the Pleteo-external identifier (e.g., `1026414#1`). |
| `Updated` | `Last Updated At` | **MCC only.** The most recent Pleteo update timestamp. For grouped cases, the tool selects the latest `Updated` value across all matching PL Batch rows. |

**Other PL Batch columns not currently used but available:** `Case ID` (internal Pleteo ID), `Data Score`, `Investigation Status`, `Automation Status`, `NNS License Potential`, `Created`, `Investigation Status Last Updated At`.

---

### 3.3 Pull Conflict Check File

**Role:** The primary source for investigation content — detailed notes, machine overviews, company information, and geographic/technical attribution data.

**Key columns consumed by the tool:**

| Pull Conflict Column | Maps To (Output) | Notes |
|---|---|---|
| `Case ID` | *(join key)* | Individual case ID used to match against the QS grouped IDs. |
| `Machine Overview` | `Machine Overview` | Summary of SketchUp products and counts (e.g., `SketchUp Pro 2022 (1x), SketchUp Pro 2023 (1x)`). For grouped cases, overviews from all matching entries are combined. |
| `Investigation Notes` | `Investigation Notes` | Full investigation narrative including data details, technical attribution, online presence, and QA notes. For grouped cases, notes from all entries are concatenated with a separator. |
| `Company Name` | `Company Name` | The Cylynt/case-level company name (may differ from Entity Name). |
| `Cylynt Organization Name` | `Cylynt Organization Name` | The organization identifier in the Cylynt platform. |
| `Industry` | `Industry` | Business sector classification. |
| `Address` | `Address` (MCC) / `Addresses` (CS) | Physical address(es). Multiple addresses separated by `\|`. Note the column name changes between regions. |
| `Countries` | `Countries` (MCC) / `Country` (CS) | Country name(s). Note the column name changes between regions. |
| `Time Span` | `Time Span` | Human-readable duration string (e.g., `5 years 6 months`). |
| `Actionable Domains` | `Actionable Domains` | Fallback source if QS Actionable Domains is empty. |
| `Website` | `Website` | Fallback source if QS Websites is empty. |

---

## 4. Output File — Column Structure

### 4.1 MCC Output (27 columns)

| # | Column | Source | Status |
|---|---|---|---|
| 1 | Date Added to This Sheet | — | **Blank** (manual entry) |
| 2 | Is Multi-National | — | **Blank** (future implementation) |
| 3 | Machine Overview | Pull Conflict | Automated |
| 4 | Investigation Notes | Pull Conflict | Automated |
| 5 | Case ID | QS Delivery ID | Automated |
| 6 | Company Name | Pull Conflict | Automated |
| 7 | Entity Name | QS Delivery ID (`Company Name`) | Automated |
| 8 | Cylynt Organization Name | Pull Conflict | Automated |
| 9 | Industry | Pull Conflict | Automated |
| 10 | Address | Pull Conflict | Automated |
| 11 | Countries | Pull Conflict | Automated |
| 12 | Estimated Case Value | — | **Blank** (manual entry) |
| 13 | Case Tier | QS Delivery ID | Automated |
| 14 | Case Category | QS Delivery ID (`[Cfa]-Category`) | Automated |
| 15 | Actionable Category | QS Delivery ID (`[Cfa]-ActionableCategory`) | Automated |
| 16 | # All Time Machines | QS Delivery ID (`Total Machines`) | Automated |
| 17 | # Actionable Machines | QS Delivery ID (`Actionable Machines`) | Automated |
| 18 | # Difference | QS Delivery ID (`[CFa]-Difference`) | Automated |
| 19 | Actionable Machine IDs | QS Delivery ID (`Approved Machines`) | Automated |
| 20 | First Event | QS Delivery ID | Automated |
| 21 | Last Event | QS Delivery ID | Automated |
| 22 | Time Span | Pull Conflict | Automated |
| 23 | Generic Email Address | — | **Blank** (manual entry) |
| 24 | Actionable Domains | QS Delivery ID (fallback: Pull Conflict) | Automated |
| 25 | Website | QS Delivery ID (fallback: Pull Conflict) | Automated |
| 26 | Last Updated At | PL Batch (`Updated`) | Automated |
| 27 | NNS License Count | — | **Blank** (manual entry) |

### 4.2 CS Output (24 columns)

| # | Column | Source | Status |
|---|---|---|---|
| 1 | Date Added to This Sheet | — | **Blank** (manual entry) |
| 2 | Is Multi-National | — | **Blank** (future implementation) |
| 3 | Machine Overview | Pull Conflict | Automated |
| 4 | Investigation Notes | Pull Conflict | Automated |
| 5 | Case ID | QS Delivery ID | Automated |
| 6 | Company Name | Pull Conflict | Automated |
| 7 | Entity Name | QS Delivery ID (`Company Name`) | Automated |
| 8 | Cylynt Organization Name | Pull Conflict | Automated |
| 9 | Industry | Pull Conflict | Automated |
| 10 | Addresses | Pull Conflict (`Address`) | Automated |
| 11 | Country | Pull Conflict (`Countries`) | Automated |
| 12 | Case Tier | QS Delivery ID | Automated |
| 13 | Case Category | QS Delivery ID (`[Cfa]-Category`) | Automated |
| 14 | Actionable Category | QS Delivery ID (`[Cfa]-ActionableCategory`) | Automated |
| 15 | # All Time Machines | QS Delivery ID (`Total Machines`) | Automated |
| 16 | # Actionable Machines | QS Delivery ID (`Actionable Machines`) | Automated |
| 17 | # Difference | QS Delivery ID (`[CFa]-Difference`) | Automated |
| 18 | Actionable Machine IDs | QS Delivery ID (`Approved Machines`) | Automated |
| 19 | First Event | QS Delivery ID | Automated |
| 20 | Last Event | QS Delivery ID | Automated |
| 21 | Time Span | Pull Conflict | Automated |
| 22 | Generic Email Address | — | **Blank** (manual entry) |
| 23 | Actionable Domains | QS Delivery ID (fallback: Pull Conflict) | Automated |
| 24 | Website | QS Delivery ID (fallback: Pull Conflict) | Automated |

### 4.3 Key Differences Between MCC and CS

| Aspect | MCC | CS |
|---|---|---|
| Total output columns | 27 | 24 |
| Address column name | `Address` | `Addresses` |
| Country column name | `Countries` | `Country` |
| `Estimated Case Value` | Present (blank) | Not included |
| `Last Updated At` | Present (from PL Batch) | Not included |
| `NNS License Count` | Present (blank) | Not included |
| Typical countries | Mexico, Costa Rica, Belize, Guatemala, Honduras, El Salvador, Nicaragua, Panama, Dominican Republic | Argentina, Chile, Peru, Colombia, Bolivia, Ecuador |

---

## 5. Columns Left Blank — Future Implementation

The following output columns are intentionally left empty. They require manual input or depend on data sources not yet integrated:

| Column | Applies To | Reason |
|---|---|---|
| **Date Added to This Sheet** | MCC + CS | Populated manually when the row is added to the Master Sheet. Represents the calendar date of the batch upload. |
| **Is Multi-National** | MCC + CS | Requires manual assessment. The QS `case_tags` field contains a "Multinational Organization" flag that could be used for future automation. |
| **Estimated Case Value** | MCC only | Determined by the region lead based on case tier, machine count, and market factors. Not available in any of the three source files. |
| **Generic Email Address** | MCC + CS | The generic contact email for the entity (e.g., `info@company.com`). Available in investigation notes but not in a structured column. Future versions could extract this from the QS `entity.generic_email` field. |
| **NNS License Count** | MCC only | The license count from the NNS report. Populated after the NNS Evidence Report is generated. The PL Batch file contains an `NNS License Potential` field that could be mapped in a future update. |

---

## 6. Grouped / Multi-Case Entities

Some entities span multiple Cylynt cases that have been merged. These appear in the QS file as a single row with comma-separated Case IDs (e.g., `4392588#1,1859189#1` for Antaestudio / Anta Estudio).

**How the tool handles grouped cases:**

- **Machine Overview:** Combined from all matching Pull Conflict entries. If both case IDs have Pull Conflict rows, their Machine Overviews are concatenated (deduplicated).
- **Investigation Notes:** Concatenated from all matching entries, separated by a horizontal rule (`---`).
- **Machine counts, IDs, dates:** Taken from the QS file, which already contains the aggregated values across all cases in the group.
- **Other fields (Address, Industry, etc.):** Taken from the first matching Pull Conflict entry.

The app flags grouped cases in the output diagnostics panel so users can review them if needed.

---

## 7. Join Logic

All three files are linked by the **Case ID** field (also called **External Case ID** in the PL Batch file). The format is a numeric ID followed by `#` and a sequence number (e.g., `1026414#1`, `769449#2`).

```
QS Delivery ID                 Pull Conflict Check           PL Batch File
──────────────                 ────────────────────          ──────────────
Case ID ──────────────────────▶ Case ID                      External Case ID
(may be grouped:               (individual per case)         (individual per case)
 "4392588#1,1859189#1")
```

**Join steps:**
1. Parse QS `Case ID` — split on commas to get individual IDs.
2. For each individual ID, look up the matching row in Pull Conflict.
3. For each individual ID, look up the matching row in PL Batch.
4. If multiple Pull Conflict rows match (grouped case), combine their content.
5. If multiple PL Batch rows match, take the latest `Updated` timestamp.

---

## 8. File Format Requirements

- **Accepted formats:** `.csv`, `.xlsx`, `.xls`
- **Encoding:** UTF-8 recommended for CSV files (Latin American characters: ñ, á, é, etc.)
- **Header row:** Must be the first row. Column names must match the expected names exactly (the tool strips leading/trailing whitespace).
- **Empty rows:** Automatically filtered out during processing.

---

## 9. Deployment

The tool runs on **Streamlit Community Cloud** and requires two files at the repository root:

| File | Purpose |
|---|---|
| `app.py` | Main application code |
| `requirements.txt` | Python dependencies (`streamlit`, `pandas`, `openpyxl`) |

No secrets, API keys, or environment variables are required. The tool processes all data client-side within the Streamlit session — no data is stored or transmitted externally.

---

## 10. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| "Unmatched Cases" warning | A Case ID from QS was not found in Pull Conflict | Verify the Pull Conflict file contains all cases from the current batch. The unmatched cases will still appear in the output but with blank Pull Conflict fields. |
| Empty Entity Name | QS `Company Name` column is empty for that row | Check the QS Delivery ID file for the missing entry. |
| Wrong column mapping | Source file has renamed or reordered columns | Ensure column headers match the expected names listed in Section 3. |
| File upload error | File is corrupted or uses unsupported encoding | Re-export the file as UTF-8 CSV or standard XLSX. |
| Machine Overview mismatch for grouped cases | Combined overview may not match manually merged totals | Review the grouped case flag in diagnostics and adjust manually if needed. |

---

*Last updated: April 2026*
