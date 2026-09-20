# Video Game Sales Analysis — Full Project Documentation

> **Purpose of this document:** Complete technical and analytical reference for the Video Game Sales Analysis project. Intended for agent extraction, resume bullet generation, portfolio write-ups, LinkedIn summaries, and interview preparation.

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Tech Stack](#3-tech-stack)
4. [Dataset](#4-dataset)
5. [Project Structure](#5-project-structure)
6. [Data Pipeline & Workflow](#6-data-pipeline--workflow)
   - Step 1 — Data Collection & Loading
   - Step 2 — Data Cleaning & Quality Check
   - Step 3 — Feature Engineering (Derived Sales Metric)
   - Step 4 — Grouping, Aggregation & Summary Statistics
   - Step 5 — Data Visualisation
   - Step 6 — Business Insights & Decision Making
7. [Frontend Architecture (Streamlit)](#7-frontend-architecture-streamlit)
8. [All Charts & Visualisations](#8-all-charts--visualisations)
9. [Business Insights Generated](#9-business-insights-generated)
10. [Key Technical Decisions & Design Choices](#10-key-technical-decisions--design-choices)
11. [Skills Demonstrated](#11-skills-demonstrated)
12. [Resume Bullet Points](#12-resume-bullet-points)
13. [Possible Extensions & Future Work](#13-possible-extensions--future-work)

---

## 1. Project Summary

**Project Name:** Video Game Sales Analysis Dashboard  
**Type:** End-to-end Data Analysis + Interactive Web Application  
**Domain:** Gaming Industry / Business Intelligence  
**Dataset Size:** ~16,600 records spanning 1980–2020  
**Output:** A fully interactive, multi-tab Streamlit dashboard with real-time filtering, 10+ charts, aggregation tables, and data-driven business recommendations.

This project takes raw video game sales data, cleans and validates it, engineers a derived sales metric, performs multi-dimensional grouping and aggregation, generates interactive visualisations, and produces actionable business intelligence — all served through a polished Streamlit frontend.

---

## 2. Problem Statement & Objectives

### Problem
The global video game industry generates billions in revenue across diverse platforms, genres, publishers, and geographic regions. Raw sales data is messy, incomplete, and difficult to interpret without structured analysis. Decision-makers (publishers, investors, analysts) need clear answers to questions like:
- Which genres and platforms dominate global sales?
- Which regions drive the most revenue?
- Which publishers are most efficient per title released?
- How has the market evolved year-over-year?
- Where should a new publisher focus their launch strategy?

### Objectives
| # | Objective | Deliverable |
|---|-----------|-------------|
| 1 | Collect and load the dataset | `pd.read_csv` with caching |
| 2 | Detect and fix data quality issues | Data quality report with badge indicators |
| 3 | Compute a derived total sales metric | `Calculated_Total_Sales` feature |
| 4 | Group and summarize by genre, platform, publisher, year | Aggregation tables (sum, count, mean) |
| 5 | Create comparison charts | 10+ Plotly interactive charts |
| 6 | Translate results into business decisions | Decision matrix + 6 insight cards |

---

## 3. Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.12+ | Core development language |
| Data Manipulation | Pandas | ≥ 2.0.0 | DataFrame operations, groupby, aggregation |
| Numerical Computing | NumPy | ≥ 1.26.0 | Numerical operations and array handling |
| Visualisation | Plotly Express | ≥ 5.18.0 | Interactive charts (bar, pie, treemap, area, scatter) |
| Visualisation | Plotly Graph Objects | ≥ 5.18.0 | Custom dual-axis combo charts, stacked bars |
| Visualisation | Plotly Subplots | ≥ 5.18.0 | Multi-axis chart layouts |
| Frontend / UI | Streamlit | ≥ 1.32.0 | Web application framework, widgets, layout |
| Styling | Custom CSS (injected) | — | Metric cards, section headers, insight boxes, badges |
| Data Source | CSV (Kaggle) | — | `vgsales.csv` — Video Game Sales dataset |

---

## 4. Dataset

**Source:** Kaggle — [Video Game Sales Dataset](https://www.kaggle.com/datasets/gregorut/videogamesales)  
**File:** `vgsales.csv`  
**Rows:** ~16,598 (raw)  
**Units:** All sales figures in **millions of units sold**

### Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `Rank` | int | Global sales rank |
| `Name` | str | Game title |
| `Platform` | str | Gaming console / platform (e.g. PS2, Wii, X360) |
| `Year` | float → int | Year of release (contains missing/non-numeric values) |
| `Genre` | str | Game genre (Action, Sports, Shooter, etc.) |
| `Publisher` | str | Game publisher (contains nulls) |
| `NA_Sales` | float | North America sales (millions) |
| `EU_Sales` | float | Europe sales (millions) |
| `JP_Sales` | float | Japan sales (millions) |
| `Other_Sales` | float | Rest-of-world sales (millions) |
| `Global_Sales` | float | Publisher-reported global total (millions) |
| `Calculated_Total_Sales` | float | **Engineered** — sum of 4 regional columns |
| `Sales_Discrepancy` | float | **Engineered** — abs difference between Global and Calculated |

### Dataset Statistics (full unfiltered)
- **16,598** total game records
- **31** unique platforms
- **12** unique genres
- **578** unique publishers
- **Year range:** 1980 – 2020
- **Top genre by volume:** Action (1,750M+ total sales)
- **Top publisher:** Nintendo

---

## 5. Project Structure

```
DATA_AN/
├── app.py                    # Main Streamlit application (single-file architecture)
├── vgsales.csv               # Raw dataset (Kaggle)
├── requirements.txt          # Python dependency pins
└── PROJECT_DOCUMENTATION.md  # This file
```

### Architecture Pattern
**Single-file Streamlit app** — all logic (data loading, cleaning, feature engineering, aggregation, visualisation, UI layout) is contained in `app.py`. This is intentional for simplicity and portability.

---

## 6. Data Pipeline & Workflow

The application follows a **linear 6-step ETL + Analysis pipeline**, executed on every session load and cached for performance.

```
CSV File
   │
   ▼
[Step 1] Load Data          ← pd.read_csv + @st.cache_data
   │
   ▼
[Step 2] Clean & Validate   ← null handling, type coercion, negative value guard
   │
   ▼
[Step 3] Feature Engineer   ← Calculated_Total_Sales = NA + EU + JP + Other
   │
   ▼
[Step 4] Aggregate & Group  ← groupby Genre / Platform / Publisher / Year
   │
   ▼
[Step 5] Visualise          ← 10+ Plotly charts across 3 tabs
   │
   ▼
[Step 6] Business Insights  ← 6 insight cards + decision matrix + correlation heatmap
```

---

### Step 1 — Data Collection & Loading

```python
@st.cache_data
def load_data(path: str = "vgsales.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df
```

- Uses `pandas.read_csv()` to ingest the CSV dataset.
- Wrapped in `@st.cache_data` — data is loaded **once** and cached in memory across Streamlit reruns, preventing redundant I/O on every widget interaction.
- Graceful error handling: if the file is missing, a user-friendly error message is shown and the app stops cleanly via `st.stop()`.

---

### Step 2 — Data Cleaning & Quality Check

Implemented inside `clean_and_engineer()`, which returns both the cleaned DataFrame and a **quality report dictionary** surfaced in the UI.

| Issue | Detection Method | Fix Applied |
|-------|-----------------|-------------|
| Missing values (any column) | `df.isnull().sum()` | Logged in quality report |
| Invalid / non-numeric `Year` | `pd.to_numeric(errors='coerce')` | Filled with column median |
| Missing `Publisher` | `.isnull().sum()` | Filled with string `"Unknown"` |
| Null `Name` rows | `.isnull().sum()` | Row dropped entirely |
| Non-numeric sales values | `pd.to_numeric(errors='coerce')` | Coerced, NaN → 0.0 |
| Negative sales values | `(df[cols] < 0).any(axis=1)` | Converted to absolute value |
| Global_Sales rounding discrepancy | `abs(Global - Calculated) > 0.05` | Flagged, Calculated used as primary |

**Quality Report UI:** Each issue is displayed as a colour-coded badge (`⚠ Fixed` / `✔ Clean`) in Tab 1 of the dashboard, making data provenance fully transparent.

---

### Step 3 — Feature Engineering (Derived Sales Metric)

```python
df["Calculated_Total_Sales"] = (
    df["NA_Sales"] + df["EU_Sales"] + df["JP_Sales"] + df["Other_Sales"]
)
```

**Business logic mapping:**  
The dataset provides pre-aggregated sales in millions (no raw quantity × unit price columns). The `Calculated_Total_Sales` column mirrors the concept of **Sales = Quantity × Unit Price** by summing all regional revenue components into a single derived total — exactly how total revenue is computed from line-item components in a transactional system.

This derived metric is used as the **primary KPI** throughout the dashboard because:
1. It is internally consistent (computed from the same source columns).
2. Minor rounding discrepancies exist between `Global_Sales` (publisher-reported) and the regional sum — the calculated version eliminates this inconsistency.

---

### Step 4 — Grouping, Aggregation & Summary Statistics

All aggregations use **pandas `groupby` + named aggregation** (`agg()` with keyword syntax):

```python
genre_summary = (
    fdf.groupby("Genre")
    .agg(
        Total_Sales=("Calculated_Total_Sales", "sum"),
        Game_Count=("Name", "count"),
        Avg_Sales=("Calculated_Total_Sales", "mean"),
    )
    .reset_index()
    .sort_values("Total_Sales", ascending=False)
    .round(2)
)
```

**Aggregation dimensions and metrics:**

| Dimension | Total Sales | Game Count | Avg Sales/Game |
|-----------|------------|------------|----------------|
| Genre | ✅ | ✅ | ✅ |
| Platform | ✅ | ✅ | ✅ |
| Publisher | ✅ | ✅ | ✅ |
| Year (YoY) | ✅ | ✅ | ✅ |
| Region (NA/EU/JP/Other) | ✅ | — | — |

**Additional derived aggregations:**
- Publisher efficiency = Total_Sales / Game_Count (filtered to publishers with ≥ 5 games to avoid small-sample bias)
- Regional share % = region_total / global_total × 100
- Peak year = `argmax` of YoY Total_Sales
- Correlation matrix across all regional + total sales columns

---

### Step 5 — Data Visualisation

10 interactive Plotly charts rendered inside a 6-tab Streamlit layout. All charts respond to sidebar filter state in real time.

*(See Section 8 for full chart inventory)*

---

### Step 6 — Business Insights & Decision Making

Six data-driven insight cards are dynamically generated from the computed aggregations. Values in all insight text are **live-computed** from the filtered dataset — they update automatically when the user changes sidebar filters.

A **Decision Matrix** table (6 rows × 4 columns: Decision Area, Recommendation, Priority, Confidence) provides a structured output suitable for direct use in strategy documents or presentations.

*(See Section 9 for full insight details)*

---

## 7. Frontend Architecture (Streamlit)

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR                    MAIN CONTENT AREA               │
│  ─────────                  ─────────────────               │
│  🎮 Filters                 [Title + Subtitle]              │
│  • Year range slider        ┌──────────────────────────┐   │
│  • Genre multiselect        │ Tab1 │ Tab2 │ Tab3 │ ... │   │
│  • Platform multiselect     └──────────────────────────┘   │
│  • Top N slider             [Tab content area]              │
└─────────────────────────────────────────────────────────────┘
```

### Tab Structure

| Tab | Name | Content |
|-----|------|---------|
| 1 | 📋 Data Overview | Dataset metrics, quality report, sample table, column descriptions |
| 2 | 📊 Summary Statistics | KPI cards, grouped tables by genre/platform/publisher/year |
| 3 | 📈 Sales Charts | 7 interactive Plotly charts for visual comparison |
| 4 | 🗺️ Regional Breakdown | Regional KPIs, pie, stacked bar, trend lines, top-N by region |
| 5 | 🏆 Rankings | Top games, publishers by count, publishers by efficiency, platform combo |
| 6 | 💡 Business Insights | 6 insight cards, decision matrix, correlation heatmap |

### Sidebar Filters (Global — affect all tabs)
| Filter | Widget | Effect |
|--------|--------|--------|
| Release Year | `st.slider` (range) | Filters all data to selected year window |
| Genre | `st.multiselect` | Include/exclude specific genres |
| Platform | `st.multiselect` | Include/exclude specific platforms |
| Top N | `st.slider` (5–30) | Controls number of rows in all ranking views |

### Custom CSS (injected via `st.markdown`)
- **Metric cards** — custom background, border-radius, uppercase label, large value font
- **Section headers** — left blue border accent, bold text
- **Insight boxes** — light blue background, border, constrained font size
- **Data quality badges** — `badge-ok` (green), `badge-warn` (yellow), `badge-err` (red)

### Performance Optimisation
- `@st.cache_data` on both `load_data()` and `clean_and_engineer()` — ensures CSV is read and cleaned only once per session regardless of widget interaction frequency.
- Filtering (sidebar → `fdf`) is applied after caching, so the heavy operations are never repeated.

---

## 8. All Charts & Visualisations

| # | Chart | Type | Library | Tab | Key Insight |
|---|-------|------|---------|-----|-------------|
| 1 | Total Sales Over Time | Area chart | Plotly Express | Charts | Market growth and decline cycles |
| 2 | Total Sales by Genre | Horizontal bar | Plotly Express | Charts | Dominant genre by revenue |
| 3 | Market Share by Genre | Donut pie | Plotly Express | Charts | Relative genre proportions |
| 4 | Sales by Platform | Treemap | Plotly Express | Charts | Platform size at a glance |
| 5 | Top N Publishers | Horizontal bar | Plotly Express | Charts | Publisher revenue ranking |
| 6 | Game Count vs Avg Sales (Bubble) | Scatter/bubble | Plotly Express | Charts | Volume vs efficiency per genre |
| 7 | Games Released Per Year | Column bar | Plotly Express | Charts | Industry output over time |
| 8 | Regional Share | Donut pie | Plotly Express | Regional | NA/EU/JP/Other proportions |
| 9 | Regional Sales by Genre | Stacked bar | Plotly Graph Objects | Regional | Genre preference per region |
| 10 | Regional Sales Trend | Multi-line | Plotly Graph Objects | Regional | Regional trajectory over time |
| 11 | Top N Games (ranked) | Horizontal bar | Plotly Express | Rankings | Best-selling titles |
| 12 | Platform Sales vs Game Count | Dual-axis combo | Plotly Subplots | Rankings | Sales efficiency per platform |
| 13 | Sales Correlation Heatmap | Heatmap (imshow) | Plotly Express | Insights | Cross-regional sales correlation |

---

## 9. Business Insights Generated

All insight values are dynamically computed from the filtered dataset.

### Insight 1 — Best Genre to Invest In
- Identifies the highest **total revenue** genre (volume play) vs. the highest **average sales per game** genre (efficiency play).
- **Business decision:** New publishers should target the high-average genre for premium releases to maximise per-title ROI.

### Insight 2 — Publisher Benchmarking
- Surfaces the #1 publisher by total sales and frames it as a strategic benchmark.
- **Business decision:** Study top publisher's catalogue strategy, platform partnerships, and franchise sequels model.

### Insight 3 — Platform Strategy
- Identifies the dominant platform by total sales.
- **Business decision:** Prioritise the top platform for launch, then expand to secondary platforms after establishing market position.

### Insight 4 — Regional Marketing Priority
- Computes each region's share of total global sales and identifies the dominant region.
- **Business decision:** Allocate the majority of marketing budget to North America (historically ~49% of total sales); Japan requires separate localisation due to distinct genre preferences.

### Insight 5 — Peak Market Period
- Identifies the year with the highest total sales.
- **Business decision:** Understand industry cyclicality; releases during market upswings correlate with higher sell-through rates.

### Insight 6 — Sales Metric Validation
- Explains the `Calculated_Total_Sales` derivation and compares it against `Global_Sales`.
- **Business decision:** Use internally computed totals for consistent cross-dataset comparisons; publisher-reported figures may include rounding.

### Decision Matrix (6 Rows)
| Decision Area | Recommendation | Priority | Confidence |
|---|---|---|---|
| Genre Selection | High-volume genre for scale; high-avg genre for premium | High | Strong |
| Platform Choice | Lead with #1 platform; secondary for incremental reach | High | Strong |
| Regional Focus | ≥50% marketing budget to dominant region | High | Strong |
| Publisher Strategy | Partner with / benchmark against top publisher | Medium | Moderate |
| Launch Timing | Target industry upswing years | Medium | Moderate |
| Portfolio Mix | Balance franchise sequels with new IP | Medium | Moderate |

### Correlation Heatmap Insight
- High Pearson correlation between NA and EU sales (~0.9) → Western markets move together.
- Japan shows much lower correlation with Western regions → distinct consumer preferences.
- **Business implication:** A game successful in NA is highly likely to succeed in EU with minimal adaptation; Japan requires a dedicated localisation strategy.

---

## 10. Key Technical Decisions & Design Choices

### 1. Single-file architecture
All code lives in `app.py`. Chosen for portability and simplicity — no package imports, no multi-module complexity. Appropriate for a self-contained analytical dashboard.

### 2. `@st.cache_data` for ETL functions
Prevents re-running CSV I/O and cleaning logic on every Streamlit widget interaction. The expensive operations (file read + full clean) run once; all subsequent reruns use the cached result.

### 3. Named aggregation syntax (`agg()` with keywords)
```python
.agg(Total_Sales=("col", "sum"), Game_Count=("col", "count"))
```
Used instead of `{"col": ["sum", "count"]}` to produce clean, named output columns directly — avoids multi-level column index flattening.

### 4. Pandas Copy-on-Write compatibility
All `fillna` operations use assignment form (`df["col"] = df["col"].fillna(val)`) instead of `inplace=True` to comply with pandas ≥ 2.0 Copy-on-Write semantics and avoid `ChainedAssignmentError`.

### 5. Plotly over Matplotlib/Seaborn
All charts use Plotly for **interactivity** (hover tooltips, zoom, pan, export). This is essential for a dashboard where users explore data rather than just view static images.

### 6. Filter applied post-cache
The sidebar filters produce `fdf` (filtered dataframe) from the cached cleaned `df`. This means: cache stores the full dataset; filters operate at render time, keeping the UI responsive.

### 7. Derived metric over Global_Sales
`Calculated_Total_Sales` is used as the primary metric rather than the raw `Global_Sales` column because it is computed from the same source columns, making it internally consistent and free of publisher-reported rounding discrepancies.

### 8. Publisher efficiency filter (≥5 games)
The "Most Efficient Publishers" ranking filters to publishers with at least 5 games before computing average sales. This prevents single-blockbuster publishers from dominating the metric due to small-sample noise.

---

## 11. Skills Demonstrated

### Data Engineering
- CSV ingestion with pandas
- Missing value detection and treatment (median imputation, categorical fill, row drop)
- Type coercion (`pd.to_numeric` with `errors='coerce'`)
- Data validation and integrity checks (negative value guard, discrepancy detection)
- Feature engineering (derived aggregated column)
- Pandas GroupBy with named multi-metric aggregation
- Copy-on-Write compliant pandas operations

### Data Analysis
- Descriptive statistics (sum, count, mean across multiple dimensions)
- Multi-dimensional segmentation (genre × platform × publisher × year × region)
- Year-over-year trend analysis
- Market share computation (percentage of total)
- Publisher efficiency analysis (sales per title, minimum sample filter)
- Cross-regional correlation analysis (Pearson correlation matrix)
- KPI identification and benchmarking

### Data Visualisation
- Plotly Express: bar, horizontal bar, pie, donut, area, scatter, bubble, treemap, column, heatmap
- Plotly Graph Objects: stacked bar, multi-line, dual Y-axis combo chart
- Plotly Subplots: make_subplots with secondary_y
- Chart formatting: annotations, text labels, colour scales, templates, margins, legends
- 13 distinct chart types across the dashboard

### Frontend / Web App Development
- Streamlit app architecture (page config, layout, tabs, sidebar)
- Streamlit widgets: slider (single + range), multiselect, metric, dataframe, tabs, columns
- Custom CSS injection for styled components (badges, cards, insight boxes, headers)
- Session state-driven real-time filtering
- Performance optimisation with `@st.cache_data`
- Responsive multi-column layouts

### Business Intelligence
- Translating raw data findings into actionable recommendations
- Decision matrix construction
- Regional market analysis
- Competitive benchmarking (publisher comparison)
- Market timing analysis (peak year detection)

---

## 12. Resume Bullet Points

> The following bullets are ready to copy directly into a resume or LinkedIn profile. Choose the ones most relevant to the role you're applying for.

### Data Analyst / Data Scientist Role
- Built an end-to-end video game sales analysis pipeline in Python (Pandas, NumPy) on a 16,600-record dataset; automated data cleaning covering null imputation, type coercion, and negative value handling with a live quality report UI.
- Engineered a derived `Calculated_Total_Sales` metric by summing 4 regional sales columns, replacing inconsistent publisher-reported figures and ensuring cross-dimensional aggregation integrity.
- Performed multi-dimensional GroupBy aggregation (genre, platform, publisher, year) computing totals, counts, and averages; surfaced insights including publisher efficiency rankings (filtered to ≥5 titles to eliminate small-sample bias).
- Conducted Pearson correlation analysis across regional sales columns, discovering near-perfect NA–EU market co-movement (r ≈ 0.9) vs. low Japan correlation — directly informing a region-specific localisation strategy recommendation.
- Produced a 6-point business decision framework including genre investment strategy, platform launch sequencing, and regional budget allocation from structured data analysis.

### Python Developer / Software Engineer Role
- Developed a production-quality single-file Streamlit web application (~520 LOC) with custom CSS styling, multi-tab layout, global sidebar filters, and real-time reactive data updates.
- Applied `@st.cache_data` memoisation to ETL functions, decoupling expensive I/O and transformation from UI rendering — eliminating redundant computation on all widget interactions.
- Implemented pandas ≥ 2.0 compatible data transformations using Copy-on-Write safe assignment patterns, ensuring forward compatibility with modern pandas releases.
- Built 13 interactive Plotly charts (Plotly Express + Graph Objects + Subplots) including dual-axis combo charts, treemaps, bubble charts, stacked bars, and correlation heatmaps.

### Business Analyst / BI Developer Role
- Designed and delivered an interactive BI dashboard for video game market analysis covering 16,600 titles across 31 platforms, 12 genres, and 578 publishers (1980–2020).
- Generated 6 data-driven business insights and a prioritised decision matrix covering genre selection, platform strategy, regional marketing allocation, publisher benchmarking, and launch timing.
- Analysed regional market dynamics — identified North America as the dominant market (~49% of total sales) and Japan as a distinct segment requiring separate content strategy, directly supporting go-to-market planning.
- Created year-over-year trend visualisation revealing market peak years and industry cyclicality patterns, enabling data-backed launch timing recommendations.

### Short Summary (LinkedIn / Portfolio Description)
> Designed and built a full-stack data analysis dashboard for video game sales (16,600 records, 1980–2020) using Python, Pandas, Plotly, and Streamlit. The project covers the complete analytics lifecycle: data ingestion, automated cleaning and validation, feature engineering, multi-dimensional aggregation (GroupBy with totals/counts/averages), 13 interactive visualisations, and business intelligence outputs including a decision matrix and correlation analysis — all served through a real-time interactive web application with global filters.

---

## 13. Possible Extensions & Future Work

| Extension | Description | Tech |
|-----------|-------------|------|
| Machine Learning | Predict global sales from genre, platform, publisher, year | Scikit-learn (regression / gradient boosting) |
| Time Series Forecasting | Forecast market sales for upcoming years | Prophet / ARIMA |
| NLP on Game Names | Extract franchise/sequel patterns from titles | spaCy / regex |
| Database Backend | Replace CSV with SQL database for larger datasets | SQLite / PostgreSQL + SQLAlchemy |
| Export Reports | Download filtered data and charts as PDF/Excel | xlsxwriter / reportlab |
| User Authentication | Multi-user dashboard with saved filter profiles | Streamlit-Authenticator |
| API Integration | Pull live sales data from external gaming APIs | requests / FastAPI |
| Dockerisation | Package app as a Docker container for deployment | Docker + docker-compose |
| Cloud Deployment | Host on Streamlit Cloud / AWS / GCP | Streamlit Community Cloud |
| A/B Genre Comparison | Side-by-side comparison of any two selected genres | Streamlit session state |

---

## Appendix — Running the Project

### Prerequisites
- Python 3.10 or higher
- `vgsales.csv` in the same directory as `app.py`

### Installation
```bash
pip install -r requirements.txt
```

### Launch
```bash
streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

### Dependencies (`requirements.txt`)
```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
numpy>=1.26.0
```

---

*Document generated for: Video Game Sales Analysis Dashboard project.*  
*All metrics, chart types, and code references reflect the current state of `app.py`.*
