"""
Video Game Sales Analysis — Streamlit Dashboard
================================================
Dataset  : vgsales.csv  (columns: Rank, Name, Platform, Year, Genre,
           Publisher, NA_Sales, EU_Sales, JP_Sales, Other_Sales, Global_Sales)
All sales figures are in millions of units.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎮 Video Game Sales Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Main title */
        .main-title {
            font-size: 2.4rem;
            font-weight: 700;
            color: #1f2328;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 1rem;
            color: #57606a;
            margin-bottom: 1.5rem;
        }
        /* Metric cards */
        div[data-testid="metric-container"] {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 16px 20px;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.78rem !important;
            color: #57606a !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.7rem !important;
            font-weight: 700 !important;
            color: #1f2328 !important;
        }
        /* Section headers */
        .section-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1f2328;
            border-left: 4px solid #3b82d4;
            padding-left: 10px;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        /* Data quality badge */
        .badge-ok   { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:20px; font-size:0.82rem; font-weight:600; }
        .badge-warn { background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:20px; font-size:0.82rem; font-weight:600; }
        .badge-err  { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.82rem; font-weight:600; }
        /* Insight box */
        .insight-box {
            background: #f0f6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 14px 18px;
            margin-top: 0.5rem;
            font-size: 0.93rem;
            color: #1e3a5f;
        }
        .insight-box b { color: #1d4ed8; }
        hr { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str = "vgsales.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@st.cache_data
def clean_and_engineer(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    STEP 2 — Data cleaning / quality check.
    STEP 3 — Derived sales column (sum of regional sales = calculated total).
    Returns cleaned dataframe + a quality-report dict.
    """
    raw_rows = len(df)
    quality: dict = {"raw_rows": raw_rows, "issues": []}

    # --- Identify missing values ---
    missing = df.isnull().sum()
    missing_dict = missing[missing > 0].to_dict()
    if missing_dict:
        quality["issues"].append(
            f"Missing values detected: {missing_dict}"
        )

    # --- Year column: coerce non-numeric, fill median ---
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    year_missing_before = df["Year"].isnull().sum()
    if year_missing_before > 0:
        median_year = int(df["Year"].dropna().median())
        df["Year"] = df["Year"].fillna(median_year)
        quality["issues"].append(
            f"Year: {year_missing_before} missing/invalid values filled with median ({median_year})."
        )
    df["Year"] = df["Year"].astype(int)

    # --- Publisher: fill missing with 'Unknown' ---
    pub_missing = df["Publisher"].isnull().sum()
    if pub_missing > 0:
        df["Publisher"] = df["Publisher"].fillna("Unknown")
        quality["issues"].append(
            f"Publisher: {pub_missing} missing values filled with 'Unknown'."
        )

    # --- Drop rows where Name is null ---
    name_null = df["Name"].isnull().sum()
    if name_null > 0:
        df.dropna(subset=["Name"], inplace=True)
        quality["issues"].append(f"Dropped {name_null} rows with missing Name.")

    # --- Ensure numeric sales columns ---
    sales_cols = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
    for col in sales_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # --- Negative sales guard ---
    neg_mask = (df[sales_cols] < 0).any(axis=1)
    if neg_mask.sum() > 0:
        df.loc[neg_mask, sales_cols] = df.loc[neg_mask, sales_cols].abs()
        quality["issues"].append(
            f"{neg_mask.sum()} rows had negative sales values — converted to absolute."
        )

    # STEP 3 — Calculated Total Sales = sum of regional columns (like qty × price)
    df["Calculated_Total_Sales"] = (
        df["NA_Sales"] + df["EU_Sales"] + df["JP_Sales"] + df["Other_Sales"]
    )

    # Discrepancy flag: if Global_Sales differs from calculated by > 0.05
    df["Sales_Discrepancy"] = (
        df["Global_Sales"] - df["Calculated_Total_Sales"]
    ).abs()
    disc_count = (df["Sales_Discrepancy"] > 0.05).sum()
    if disc_count > 0:
        quality["issues"].append(
            f"{disc_count} rows have a small rounding discrepancy between "
            "Global_Sales and regional sum — using Calculated_Total_Sales as the primary metric."
        )

    quality["clean_rows"] = len(df)
    quality["dropped_rows"] = raw_rows - len(df)
    quality["missing_dict"] = missing_dict

    return df, quality


# ──────────────────────────────────────────────────────────────────────────────
# LOAD & CLEAN
# ──────────────────────────────────────────────────────────────────────────────
try:
    raw_df = load_data()
except FileNotFoundError:
    st.error("❌ `vgsales.csv` not found. Place it in the same folder as `app.py`.")
    st.stop()

df, quality = clean_and_engineer(raw_df.copy())

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTERS
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Filters")

    year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
    year_range = st.slider(
        "Release Year", year_min, year_max, (year_min, year_max)
    )

    all_genres = sorted(df["Genre"].dropna().unique().tolist())
    selected_genres = st.multiselect(
        "Genre", options=all_genres, default=all_genres
    )

    all_platforms = sorted(df["Platform"].dropna().unique().tolist())
    selected_platforms = st.multiselect(
        "Platform", options=all_platforms, default=all_platforms
    )

    top_n = st.slider("Top N (for rankings)", 5, 30, 10)

    st.markdown("---")
    st.caption("Data: Kaggle — Video Game Sales  \nAll sales in **millions of units**.")

# ──────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────────────────────
fdf = df[
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["Genre"].isin(selected_genres))
    & (df["Platform"].isin(selected_platforms))
].copy()

if fdf.empty:
    st.warning("⚠️ No data matches the selected filters. Adjust the sidebar filters.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="main-title">🎮 Video Game Sales Analysis Dashboard</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Interactive exploration of global video game sales data — '
    "genres, platforms, publishers, regional trends, and business insights.</p>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Data Overview",
    "📊 Summary Statistics",
    "📈 Sales Charts",
    "🗺️ Regional Breakdown",
    "🏆 Rankings",
    "💡 Business Insights",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA OVERVIEW (Steps 1 & 2)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">Step 1 · Dataset Overview</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{quality['raw_rows']:,}")
    c2.metric("After Cleaning", f"{quality['clean_rows']:,}")
    c3.metric("Rows Dropped", f"{quality['dropped_rows']:,}")
    c4.metric("Columns", str(len(df.columns)))

    st.markdown('<p class="section-header">Step 2 · Data Quality Report</p>', unsafe_allow_html=True)

    if quality["issues"]:
        for issue in quality["issues"]:
            st.markdown(f'<span class="badge-warn">⚠ Fixed</span> &nbsp; {issue}', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-ok">✔ Clean</span> &nbsp; No data quality issues found.', unsafe_allow_html=True)

    # Missing value heatmap summary
    if quality["missing_dict"]:
        st.markdown("**Missing values per column (raw data):**")
        miss_df = pd.DataFrame.from_dict(
            quality["missing_dict"], orient="index", columns=["Missing Count"]
        )
        miss_df["% of Total"] = (miss_df["Missing Count"] / quality["raw_rows"] * 100).round(2)
        st.dataframe(miss_df, use_container_width=True)
    else:
        st.info("✅ No missing values detected in the raw dataset.")

    st.markdown("**Calculated Total Sales (Step 3):**")
    st.markdown(
        """
        > **Formula:** `Calculated_Total_Sales = NA_Sales + EU_Sales + JP_Sales + Other_Sales`  
        > This mirrors the business logic of **Sales = Quantity × Unit Price**, deriving
        > total revenue from individual regional components.
        """,
    )

    st.markdown('<p class="section-header">Sample Data (filtered)</p>', unsafe_allow_html=True)
    st.dataframe(
        fdf[["Rank", "Name", "Platform", "Year", "Genre", "Publisher",
             "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales",
             "Calculated_Total_Sales", "Global_Sales"]].head(50),
        use_container_width=True,
        height=400,
    )

    st.markdown("**Column Descriptions**")
    col_desc = pd.DataFrame({
        "Column": ["Rank", "Name", "Platform", "Year", "Genre", "Publisher",
                   "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales",
                   "Global_Sales", "Calculated_Total_Sales"],
        "Description": [
            "Sales rank by global units sold",
            "Game title",
            "Gaming platform / console",
            "Year of release",
            "Game genre",
            "Publisher name",
            "North America sales (millions)",
            "Europe sales (millions)",
            "Japan sales (millions)",
            "Rest-of-world sales (millions)",
            "Publisher-reported global sales (millions)",
            "Sum of regional sales — our derived metric (millions)",
        ],
    })
    st.dataframe(col_desc, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SUMMARY STATISTICS (Step 4)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">Step 4 · Group & Summarize — Totals, Counts & Averages</p>', unsafe_allow_html=True)

    # ── KPI metrics ──────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Sales (M)", f"{fdf['Calculated_Total_Sales'].sum():,.2f}")
    k2.metric("Total Games", f"{fdf['Name'].nunique():,}")
    k3.metric("Avg Sales / Game (M)", f"{fdf['Calculated_Total_Sales'].mean():.2f}")
    k4.metric("Genres", str(fdf["Genre"].nunique()))
    k5.metric("Publishers", f"{fdf['Publisher'].nunique():,}")

    st.markdown("---")

    # ── By Genre ─────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Sales by Genre**")
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
        st.dataframe(genre_summary, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("**Sales by Platform**")
        platform_summary = (
            fdf.groupby("Platform")
            .agg(
                Total_Sales=("Calculated_Total_Sales", "sum"),
                Game_Count=("Name", "count"),
                Avg_Sales=("Calculated_Total_Sales", "mean"),
            )
            .reset_index()
            .sort_values("Total_Sales", ascending=False)
            .round(2)
        )
        st.dataframe(platform_summary, use_container_width=True, hide_index=True, height=350)

    st.markdown("---")

    # ── By Publisher ─────────────────────────────────────────────────────────
    st.markdown(f"**Top {top_n} Publishers by Total Sales**")
    pub_summary = (
        fdf.groupby("Publisher")
        .agg(
            Total_Sales=("Calculated_Total_Sales", "sum"),
            Game_Count=("Name", "count"),
            Avg_Sales=("Calculated_Total_Sales", "mean"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
        .head(top_n)
        .round(2)
    )
    st.dataframe(pub_summary, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Year-over-Year ────────────────────────────────────────────────────────
    st.markdown("**Year-over-Year Sales Summary**")
    yoy = (
        fdf.groupby("Year")
        .agg(
            Total_Sales=("Calculated_Total_Sales", "sum"),
            Game_Count=("Name", "count"),
            Avg_Sales=("Calculated_Total_Sales", "mean"),
        )
        .reset_index()
        .sort_values("Year")
        .round(2)
    )
    st.dataframe(yoy, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHARTS (Step 5)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">Step 5 · Charts — Comparing Sales Results</p>', unsafe_allow_html=True)

    # ── Chart 1: Sales over time ──────────────────────────────────────────────
    st.markdown("#### 📅 Total Sales Over Time (by Year)")
    fig_yoy = px.area(
        yoy,
        x="Year",
        y="Total_Sales",
        labels={"Total_Sales": "Total Sales (M)", "Year": "Release Year"},
        color_discrete_sequence=["#3b82d4"],
        template="plotly_white",
    )
    fig_yoy.update_traces(line_width=2, fillcolor="rgba(59,130,212,0.15)")
    fig_yoy.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_yoy, use_container_width=True)

    st.markdown("---")
    ch1, ch2 = st.columns(2)

    # ── Chart 2: Genre bar ────────────────────────────────────────────────────
    with ch1:
        st.markdown("#### 🎯 Total Sales by Genre")
        fig_genre = px.bar(
            genre_summary.sort_values("Total_Sales"),
            x="Total_Sales",
            y="Genre",
            orientation="h",
            color="Total_Sales",
            color_continuous_scale="Blues",
            labels={"Total_Sales": "Total Sales (M)"},
            template="plotly_white",
            text="Total_Sales",
        )
        fig_genre.update_traces(texttemplate="%{text:.1f}M", textposition="outside")
        fig_genre.update_layout(
            coloraxis_showscale=False,
            margin=dict(t=20, b=20, l=10, r=40),
            yaxis_title=None,
        )
        st.plotly_chart(fig_genre, use_container_width=True)

    # ── Chart 3: Genre pie ────────────────────────────────────────────────────
    with ch2:
        st.markdown("#### 🍕 Market Share by Genre")
        fig_pie = px.pie(
            genre_summary,
            names="Genre",
            values="Total_Sales",
            hole=0.4,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    ch3, ch4 = st.columns(2)

    # ── Chart 4: Platform treemap ─────────────────────────────────────────────
    with ch3:
        st.markdown("#### 🖥️ Sales by Platform (Treemap)")
        fig_tree = px.treemap(
            platform_summary,
            path=["Platform"],
            values="Total_Sales",
            color="Total_Sales",
            color_continuous_scale="Blues",
            template="plotly_white",
        )
        fig_tree.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_tree, use_container_width=True)

    # ── Chart 5: Top Publishers ───────────────────────────────────────────────
    with ch4:
        st.markdown(f"#### 🏢 Top {top_n} Publishers by Total Sales")
        fig_pub = px.bar(
            pub_summary.sort_values("Total_Sales"),
            x="Total_Sales",
            y="Publisher",
            orientation="h",
            color="Total_Sales",
            color_continuous_scale="Purples",
            labels={"Total_Sales": "Total Sales (M)"},
            template="plotly_white",
            text="Total_Sales",
        )
        fig_pub.update_traces(texttemplate="%{text:.1f}M", textposition="outside")
        fig_pub.update_layout(
            coloraxis_showscale=False,
            margin=dict(t=20, b=20, l=10, r=40),
            yaxis_title=None,
        )
        st.plotly_chart(fig_pub, use_container_width=True)

    st.markdown("---")

    # ── Chart 6: Avg sales scatter ───────────────────────────────────────────
    st.markdown("#### 🔵 Game Count vs Avg Sales per Genre (Bubble Chart)")
    bubble_df = genre_summary.copy()
    fig_bubble = px.scatter(
        bubble_df,
        x="Game_Count",
        y="Avg_Sales",
        size="Total_Sales",
        color="Genre",
        hover_name="Genre",
        labels={"Game_Count": "Number of Games", "Avg_Sales": "Avg Sales per Game (M)"},
        template="plotly_white",
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_bubble.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    # ── Chart 7: Year-over-Year game count ───────────────────────────────────
    st.markdown("#### 📦 Number of Games Released Per Year")
    fig_count = px.bar(
        yoy,
        x="Year",
        y="Game_Count",
        labels={"Game_Count": "Games Released", "Year": "Year"},
        color="Game_Count",
        color_continuous_scale="Teal",
        template="plotly_white",
    )
    fig_count.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig_count, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — REGIONAL BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">Regional Sales Breakdown</p>', unsafe_allow_html=True)

    region_totals = {
        "North America": fdf["NA_Sales"].sum(),
        "Europe": fdf["EU_Sales"].sum(),
        "Japan": fdf["JP_Sales"].sum(),
        "Rest of World": fdf["Other_Sales"].sum(),
    }

    r1, r2, r3, r4 = st.columns(4)
    for col, (region, val) in zip([r1, r2, r3, r4], region_totals.items()):
        col.metric(region, f"{val:,.2f} M")

    st.markdown("---")
    reg1, reg2 = st.columns(2)

    with reg1:
        st.markdown("#### 🌍 Regional Share (Pie)")
        reg_pie = px.pie(
            names=list(region_totals.keys()),
            values=list(region_totals.values()),
            hole=0.4,
            template="plotly_white",
            color_discrete_sequence=["#3b82d4", "#7c5cd8", "#f59e0b", "#10b981"],
        )
        reg_pie.update_traces(textposition="outside", textinfo="percent+label")
        reg_pie.update_layout(margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(reg_pie, use_container_width=True)

    with reg2:
        st.markdown("#### 📊 Regional Sales by Genre (Stacked Bar)")
        region_genre = (
            fdf.groupby("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]
            .sum()
            .reset_index()
            .sort_values("NA_Sales", ascending=False)
        )
        rg_fig = go.Figure()
        for col_name, label, colour in [
            ("NA_Sales", "North America", "#3b82d4"),
            ("EU_Sales", "Europe", "#7c5cd8"),
            ("JP_Sales", "Japan", "#f59e0b"),
            ("Other_Sales", "Rest of World", "#10b981"),
        ]:
            rg_fig.add_bar(
                x=region_genre["Genre"],
                y=region_genre[col_name],
                name=label,
                marker_color=colour,
            )
        rg_fig.update_layout(
            barmode="stack",
            template="plotly_white",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(t=20, b=60),
            yaxis_title="Sales (M)",
            xaxis_title=None,
        )
        st.plotly_chart(rg_fig, use_container_width=True)

    st.markdown("---")

    st.markdown("#### 📅 Regional Sales Trend Over Time")
    reg_year = (
        fdf.groupby("Year")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]
        .sum()
        .reset_index()
    )
    fig_reg_trend = go.Figure()
    for col_name, label, colour in [
        ("NA_Sales", "North America", "#3b82d4"),
        ("EU_Sales", "Europe", "#7c5cd8"),
        ("JP_Sales", "Japan", "#f59e0b"),
        ("Other_Sales", "Rest of World", "#10b981"),
    ]:
        fig_reg_trend.add_scatter(
            x=reg_year["Year"],
            y=reg_year[col_name],
            mode="lines",
            name=label,
            line=dict(color=colour, width=2),
        )
    fig_reg_trend.update_layout(
        template="plotly_white",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20, b=60),
        yaxis_title="Sales (M)",
        xaxis_title="Release Year",
    )
    st.plotly_chart(fig_reg_trend, use_container_width=True)

    st.markdown("---")

    st.markdown(f"#### 🗾 Top {top_n} Games in Each Region")
    region_map = {
        "North America": "NA_Sales",
        "Europe": "EU_Sales",
        "Japan": "JP_Sales",
        "Rest of World": "Other_Sales",
    }
    reg_sel = st.selectbox("Select Region", list(region_map.keys()))
    top_reg = (
        fdf[["Name", "Platform", "Genre", region_map[reg_sel]]]
        .sort_values(region_map[reg_sel], ascending=False)
        .head(top_n)
        .rename(columns={region_map[reg_sel]: "Sales (M)"})
        .reset_index(drop=True)
    )
    top_reg.index += 1
    st.dataframe(top_reg, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">🏆 Top Rankings</p>', unsafe_allow_html=True)

    rk1, rk2 = st.columns(2)

    with rk1:
        st.markdown(f"**Top {top_n} Best-Selling Games**")
        top_games = (
            fdf[["Name", "Platform", "Year", "Genre", "Publisher", "Calculated_Total_Sales"]]
            .sort_values("Calculated_Total_Sales", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        top_games.index += 1
        top_games.rename(columns={"Calculated_Total_Sales": "Total Sales (M)"}, inplace=True)
        st.dataframe(top_games, use_container_width=True)

    with rk2:
        st.markdown(f"**Top {top_n} Games — Bar Chart**")
        fig_topgames = px.bar(
            top_games.sort_values("Total Sales (M)"),
            x="Total Sales (M)",
            y="Name",
            orientation="h",
            color="Genre",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text="Total Sales (M)",
        )
        fig_topgames.update_traces(texttemplate="%{text:.2f}M", textposition="outside")
        fig_topgames.update_layout(
            margin=dict(t=10, b=10, l=10, r=50),
            yaxis_title=None,
            legend_title="Genre",
        )
        st.plotly_chart(fig_topgames, use_container_width=True)

    st.markdown("---")
    rk3, rk4 = st.columns(2)

    with rk3:
        st.markdown(f"**Top {top_n} Most Prolific Publishers (by game count)**")
        top_pub_count = (
            fdf.groupby("Publisher")["Name"]
            .count()
            .reset_index()
            .rename(columns={"Name": "Games Published"})
            .sort_values("Games Published", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        top_pub_count.index += 1
        st.dataframe(top_pub_count, use_container_width=True)

    with rk4:
        st.markdown(f"**Top {top_n} Most Efficient Publishers (avg sales/game)**")
        top_efficient = (
            fdf.groupby("Publisher")
            .agg(
                Total_Sales=("Calculated_Total_Sales", "sum"),
                Game_Count=("Name", "count"),
            )
            .query("Game_Count >= 5")
            .assign(Avg_Sales=lambda x: (x["Total_Sales"] / x["Game_Count"]).round(3))
            .reset_index()
            .sort_values("Avg_Sales", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        top_efficient.index += 1
        st.dataframe(top_efficient, use_container_width=True)

    st.markdown("---")
    st.markdown(f"**Top {top_n} Platforms — Sales vs Game Count**")
    fig_platform_combo = make_subplots(specs=[[{"secondary_y": True}]])
    plat_top = platform_summary.head(top_n).sort_values("Total_Sales", ascending=False)
    fig_platform_combo.add_bar(
        x=plat_top["Platform"],
        y=plat_top["Total_Sales"],
        name="Total Sales (M)",
        marker_color="#3b82d4",
        secondary_y=False,
    )
    fig_platform_combo.add_scatter(
        x=plat_top["Platform"],
        y=plat_top["Game_Count"],
        name="Game Count",
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2),
        secondary_y=True,
    )
    fig_platform_combo.update_layout(
        template="plotly_white",
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", y=-0.2),
    )
    fig_platform_combo.update_yaxes(title_text="Total Sales (M)", secondary_y=False)
    fig_platform_combo.update_yaxes(title_text="Game Count", secondary_y=True)
    st.plotly_chart(fig_platform_combo, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — BUSINESS INSIGHTS (Step 6)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="section-header">Step 6 · Data-Driven Business Decisions</p>', unsafe_allow_html=True)

    # ── Compute insight values ────────────────────────────────────────────────
    best_genre = genre_summary.iloc[0]["Genre"]
    best_genre_sales = genre_summary.iloc[0]["Total_Sales"]
    highest_avg_genre = genre_summary.sort_values("Avg_Sales", ascending=False).iloc[0]
    top_publisher = pub_summary.iloc[0]["Publisher"]
    top_publisher_sales = pub_summary.iloc[0]["Total_Sales"]
    top_platform = platform_summary.iloc[0]["Platform"]
    top_platform_sales = platform_summary.iloc[0]["Total_Sales"]
    best_region = max(region_totals, key=region_totals.get)
    best_region_val = region_totals[best_region]
    total_sales_all = fdf["Calculated_Total_Sales"].sum()
    na_share = region_totals["North America"] / total_sales_all * 100

    peak_year_row = yoy.sort_values("Total_Sales", ascending=False).iloc[0]
    peak_year = int(peak_year_row["Year"])
    peak_year_sales = peak_year_row["Total_Sales"]

    # ── Insight cards ─────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="insight-box">
            <b>🎯 Insight 1 — Best Genre to Invest In:</b><br>
            <b>{best_genre}</b> is the highest-grossing genre with
            <b>{best_genre_sales:,.2f}M</b> total sales.
            However, <b>{highest_avg_genre['Genre']}</b> has the highest
            average sales per game (<b>{highest_avg_genre['Avg_Sales']:.2f}M</b>),
            suggesting fewer releases generate outsized revenue — a lower-risk,
            higher-reward genre for new titles.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-box" style="margin-top:0.75rem;">
            <b>🏢 Insight 2 — Publisher Benchmarking:</b><br>
            <b>{top_publisher}</b> leads all publishers with
            <b>{top_publisher_sales:,.2f}M</b> in total sales.
            New entrants should study their catalogue strategy,
            platform partnerships, and franchise model to compete effectively.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-box" style="margin-top:0.75rem;">
            <b>🖥️ Insight 3 — Platform Strategy:</b><br>
            <b>{top_platform}</b> dominates with
            <b>{top_platform_sales:,.2f}M</b> in sales.
            Publishers targeting maximum reach should prioritise this platform
            for launch, then expand to secondary platforms post-launch.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-box" style="margin-top:0.75rem;">
            <b>🌍 Insight 4 — Regional Marketing Priority:</b><br>
            <b>{best_region}</b> is the dominant sales region, accounting for
            <b>{na_share:.1f}%</b> of total global sales.
            Marketing budgets and localisation efforts should be weighted
            towards this region, while Japan-specific titles require a
            distinct content strategy given different genre preferences.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-box" style="margin-top:0.75rem;">
            <b>📅 Insight 5 — Peak Market Period:</b><br>
            The video game market peaked in <b>{peak_year}</b> with
            <b>{peak_year_sales:,.2f}M</b> in total sales.
            Releases in peak-industry years outperform; understanding
            market saturation cycles is key for timing new launches.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="insight-box" style="margin-top:0.75rem;">
            <b>💰 Insight 6 — Sales = Regional Sum (Calculated):</b><br>
            Our <b>Calculated_Total_Sales</b> metric (NA + EU + JP + Other)
            mirrors the concept of <i>Sales = Quantity × Unit Price</i> at a
            regional level. Discrepancies with the publisher-reported
            <b>Global_Sales</b> column are minor (rounding) and validate
            data integrity. Use the calculated metric for internally
            consistent aggregations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Recommendation matrix ─────────────────────────────────────────────────
    st.markdown("#### 📋 Decision Matrix — Actionable Recommendations")
    decisions = pd.DataFrame({
        "Decision Area": [
            "Genre Selection",
            "Platform Choice",
            "Regional Focus",
            "Publisher Strategy",
            "Launch Timing",
            "Portfolio Mix",
        ],
        "Recommendation": [
            f"Prioritise {best_genre} for volume; {highest_avg_genre['Genre']} for premium titles",
            f"Lead with {top_platform}; secondary platforms for incremental reach",
            f"Allocate ≥50% of marketing budget to {best_region}",
            f"Partner with or benchmark against {top_publisher}",
            f"Target industry upswing years (historically around {peak_year})",
            "Balance franchise sequels (proven demand) with new IP (long-term brand building)",
        ],
        "Priority": ["High", "High", "High", "Medium", "Medium", "Medium"],
        "Confidence": ["Strong", "Strong", "Strong", "Moderate", "Moderate", "Moderate"],
    })
    st.dataframe(decisions, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Correlation heatmap ───────────────────────────────────────────────────
    st.markdown("#### 🔗 Sales Correlation Across Regions")
    corr_df = fdf[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Calculated_Total_Sales"]].corr().round(2)
    fig_corr = px.imshow(
        corr_df,
        text_auto=True,
        color_continuous_scale="Blues",
        template="plotly_white",
        title="Pearson Correlation — Regional & Total Sales",
        aspect="auto",
    )
    fig_corr.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown(
        """
        <div class="insight-box" style="margin-top:0.5rem;">
            <b>📌 Correlation Insight:</b>
            High correlation between NA and EU sales suggests Western markets
            move together — a hit in North America is very likely to succeed in
            Europe. Japan shows lower correlation with Western regions, confirming
            it requires a separate localisation strategy.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#57606a; font-size:0.82rem;'>"
    "🎮 Video Game Sales Analysis Dashboard &nbsp;|&nbsp; "
    "Data: Kaggle vgsales.csv &nbsp;|&nbsp; Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)
