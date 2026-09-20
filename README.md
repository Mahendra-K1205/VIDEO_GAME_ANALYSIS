# 🎮 Video Game Sales Analysis Dashboard

An interactive Streamlit dashboard for exploring global video game sales data — covering genres, platforms, publishers, regional trends, and data-driven business insights.

---

## What It Does

The app loads the [Kaggle Video Game Sales dataset](https://www.kaggle.com/datasets/gregorut/videogamesales) (`vgsales.csv`), cleans it, engineers a derived sales metric, and presents everything through an interactive multi-tab dashboard with sidebar filters.

### Six tabs

| Tab | What's inside |
|-----|---------------|
| **📋 Data Overview** | Raw vs cleaned row counts, data quality report, column descriptions, sample data |
| **📊 Summary Statistics** | KPIs + grouped aggregations by genre, platform, publisher, and year |
| **📈 Sales Charts** | Area chart, bar/pie charts, treemap, bubble chart, release-count bar chart |
| **🗺️ Regional Breakdown** | NA / EU / JP / Rest-of-World split — pie, stacked bar, trend lines, per-region top-N tables |
| **🏆 Rankings** | Top-N best-selling games, most prolific publishers, most efficient publishers, platform combo chart |
| **💡 Business Insights** | Six insight cards + a decision matrix + a regional correlation heatmap |

### Sidebar filters (global — affect all tabs)
- Release year range (slider)
- Genre multi-select
- Platform multi-select
- Top N value for rankings

---

## Project Structure

```
├── app.py                    # Entire application — single-file architecture
├── vgsales.csv               # Dataset (Kaggle — ~16,500 rows)
├── requirements.txt          # Python dependencies
├── PROJECT_DOCUMENTATION.md  # Full technical write-up
└── README.md                 # This file
```

---

## Quick Start

### 1. Prerequisites
- Python 3.10+

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

> **Note:** `vgsales.csv` must be in the same directory as `app.py`. The app will show an error and stop if it can't find the file.

---

## Dependencies

| Package | Version |
|---------|---------|
| streamlit | ≥ 1.32.0 |
| pandas | ≥ 2.0.0 |
| plotly | ≥ 5.18.0 |
| numpy | ≥ 1.26.0 |

---

## Data Pipeline (brief)

1. **Load** — `vgsales.csv` read into a DataFrame via `@st.cache_data` (loaded once, reused on re-renders).
2. **Clean** — Missing `Year` values filled with the median; missing `Publisher` filled with `"Unknown"`; rows with no game name dropped; negative sales coerced to absolute values.
3. **Engineer** — A `Calculated_Total_Sales` column is derived as `NA_Sales + EU_Sales + JP_Sales + Other_Sales`. This is used as the primary metric throughout the app.
4. **Filter** — Sidebar selections are applied *after* caching so the ETL cost is paid only once.
5. **Aggregate** — Grouped summaries by genre, platform, publisher, and year using named `.agg()` calls.
6. **Visualise** — All charts are built with Plotly (Express + Graph Objects); no Matplotlib.

---

## Dataset

- **Source:** [Kaggle — Video Game Sales](https://www.kaggle.com/datasets/gregorut/videogamesales)
- **Rows:** ~16,500 (after cleaning)
- **Sales unit:** millions of units sold
- **Columns:** `Rank`, `Name`, `Platform`, `Year`, `Genre`, `Publisher`, `NA_Sales`, `EU_Sales`, `JP_Sales`, `Other_Sales`, `Global_Sales`

---

## Full Documentation

See [`PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md) for the complete technical write-up — architecture decisions, skill demonstrations, resume bullet points, and possible extensions.
