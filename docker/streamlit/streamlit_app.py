from datetime import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os

# ---------------------------------------------------------------------------
# Initialize empty DataFrames
# ---------------------------------------------------------------------------
df_company = pd.DataFrame()
df_headcount = pd.DataFrame()
df_date = pd.DataFrame()
df_revenue = pd.DataFrame()

# ---------------------------------------------------------------------------
# Base URL for FastAPI
# ---------------------------------------------------------------------------
# Try to get FASTAPI_URL from environment
FASTAPI_BASE_URL = os.getenv("FASTAPI_URL")

# Fallbacks based on environment
if FASTAPI_BASE_URL is None:
    if os.getenv("RENDER"):  # If running on Render
        FASTAPI_BASE_URL = "https://your-fastapi-app.onrender.com"
    else:
        FASTAPI_BASE_URL = "http://fastapi_app:8000"  # Docker Compose default
# ---------------------------------------------------------------------------
# Load data from FastAPI endpoints
# ---------------------------------------------------------------------------
api_endpoints = {
    "company": f"{FASTAPI_BASE_URL}/company/",
    "headcount": f"{FASTAPI_BASE_URL}/headcount/",
    "date": f"{FASTAPI_BASE_URL}/date/",
    "revenue": f"{FASTAPI_BASE_URL}/revenue/"
}

for endpoint, url in api_endpoints.items():
    df_name = f"df_{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        globals()[df_name] = pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching {endpoint} data from API: {e}")

# ---------------------------------------------------------------------------
# Merge data if all DataFrames are not empty
# ---------------------------------------------------------------------------
df_merged = pd.DataFrame()
if not (df_company.empty or df_headcount.empty or df_revenue.empty or df_date.empty):
    df_merged = (
        df_revenue
        .merge(df_company, on='company_id')
        .merge(df_headcount, on=['company_id', 'month'])
        .merge(df_date, on='month')
    )

    # Drop unwanted columns and rename
    columns_to_drop = [col for col in df_merged.columns if col.endswith(('_x', '_y')) or col == 'month_id']
    df_merged.drop(columns=columns_to_drop, inplace=True)
    df_merged.rename(columns={'revenue_eur': 'monthly_revenue_eur'}, inplace=True)

    # Reorder columns
    cols_order = ['month', 'company_id', 'company_name', 'location', 'industry'] + \
                 [col for col in df_merged.columns if col not in ['month', 'company_id', 'company_name', 'location', 'industry']]
    df_merged = df_merged[cols_order]

    # Calculate revenue per employee
    df_merged['revenue_per_employee'] = df_merged['monthly_revenue_eur'] / df_merged['employee_count']

    # Convert month to datetime, extract year, filter to today
    df_merged['month'] = pd.to_datetime(df_merged['month'])
    df_merged['year'] = df_merged['month'].dt.year

    # Monat als Zahl hinzufügen (für KPI-Filters)
    df_merged['month_num'] = df_merged['month'].dt.month

    # Filter auf heutiges Datum
    today = pd.Timestamp.today()
    df_merged = df_merged[df_merged['month'] <= today]

# ---------------------------------------------------------------------------
# Sidebar: Table of Contents + Single Year Filter
# ---------------------------------------------------------------------------
st.sidebar.title("Table of Contents")
pages = ["Arsipa's Facts and Dimensions", "Master Data & KPIs", "Management Board", "Finance Use Case"]
page = st.sidebar.radio("Go to", pages)

# Single Year Filter (2024 or 2025)
if not df_merged.empty:
    allowed_years = [2024, 2025]
    years_in_data = sorted(df_merged['year'].unique())
    filter_years = [y for y in allowed_years if y in years_in_data]

    selected_year = st.sidebar.selectbox(
        "Select Year",
        options=filter_years,
        index=0
    )

    df_merged_filtered = df_merged[df_merged['year'] == selected_year]
else:
    df_merged_filtered = df_merged

# ---------------------------------------------------------------------------
# PAGE 1: Facts and Dimensions
# ---------------------------------------------------------------------------
if page == pages[0]:
    st.title("Tabellen Beispiele für Arsipa's Firmen Daten")
    st.write('### Exploring Schemas')

    st.write('##### Company Dimension')
    st.dataframe(df_company.head(10), use_container_width=True)
    st.write('Dataset size =', df_company.shape)

    st.write('##### Headcount Fact')
    if not df_headcount.empty:
        st.dataframe(df_headcount, use_container_width=True, height=400)
        st.write('Dataset size =', df_headcount.shape)

    st.write('##### Revenue Fact')
    st.dataframe(df_revenue.head(10), use_container_width=True)
    st.write('Dataset size =', df_revenue.shape)

    st.write('##### Date Dimension')
    if not df_date.empty:
        st.dataframe(df_date, use_container_width=True, height=400)
        st.write('Dataset size =', df_date.shape)

# ---------------------------------------------------------------------------
# PAGE 2: Master Data & KPIs
# ---------------------------------------------------------------------------
if page == pages[1]:
    st.title("Masterdaten und KPIs der Arsipa-Unternehmensdaten")

    st.write('##### Umsatz- und Headcount-Masterdaten')
    st.dataframe(df_merged_filtered, use_container_width=True, height=400)

    # KPIs
    total_revenue = df_merged_filtered['monthly_revenue_eur'].sum()
    avg_headcount = df_merged_filtered['employee_count'].mean()
    avg_revenue_per_employee = df_merged_filtered['revenue_per_employee'].mean()

    # Revenue Trend
    fig1 = px.line(
        df_merged_filtered,
        x="month",
        y="monthly_revenue_eur",
        color="company_name",
        markers=True,
        title="Umsatzentwicklung pro Monat und Tochtergesellschaft"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Revenue per Employee by Industry
    df_avg_industry = df_merged_filtered.groupby(['month', 'industry'], as_index=False)['revenue_per_employee'].mean()
    fig2 = px.line(
        df_avg_industry,
        x="month",
        y="revenue_per_employee",
        color="industry",
        markers=True,
        title="Durchschnittlicher Umsatz pro Mitarbeiter nach Branche"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 3: Management Board Dashboard
# ---------------------------------------------------------------------------
if page == pages[2]:
    st.title("Management-Dashboard Arsipa")
    if not df_merged_filtered.empty:
        # Aktueller Monat
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        
        # Vormonat berechnen
        if current_month == 1:
            prev_year = current_year - 1
            prev_month = 12
        else:
            prev_year = current_year
            prev_month = current_month - 1
        
        # Filter für Vormonat
        df_prev_month = df_merged_filtered[
            (df_merged_filtered['year'] == prev_year) &
            (df_merged_filtered['month_num'] == prev_month)
        ]
        
        # Filter für aktuellen Monat
        df_current_month = df_merged_filtered[
            (df_merged_filtered['year'] == current_year) &
            (df_merged_filtered['month_num'] == current_month)
        ]
        
        # --- KPIs Vormonat ---
        total_revenue_prev = df_prev_month['monthly_revenue_eur'].sum()
        total_headcount_prev = df_prev_month['employee_count'].sum()
        revenue_per_employee_prev = df_prev_month['revenue_per_employee'].mean()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Gesamtumsatz (Vormonat)", f"{total_revenue_prev:,.0f} €")
        kpi2.metric("Gesamt-Headcount (Vormonat)", f"{total_headcount_prev}")
        kpi3.metric("Umsatz pro Mitarbeiter (Vormonat)", f"{revenue_per_employee_prev:,.2f} €")
        
        st.markdown("---")  # Trenner
        
        # --- KPIs aktueller Monat ---
        total_revenue_current = df_current_month['monthly_revenue_eur'].sum()
        total_headcount_current = df_current_month['employee_count'].sum()
        revenue_per_employee_current = df_current_month['revenue_per_employee'].mean()
        
        kpi4, kpi5, kpi6 = st.columns(3)
        kpi4.metric("Gesamtumsatz (aktuell)", f"{total_revenue_current:,.0f} €")
        kpi5.metric("Gesamt-Headcount (aktuell)", f"{total_headcount_current}")
        kpi6.metric("Umsatz pro Mitarbeiter (aktuell)", f"{revenue_per_employee_current:,.2f} €")

    # Umsatzentwicklung pro Tochtergesellschaft
    st.subheader("Umsatzentwicklung pro Tochtergesellschaft")
    selected_company = st.multiselect(
        "Wähle Tochtergesellschaften",
        options=df_merged_filtered['company_name'].unique(),
        default=df_merged_filtered['company_name'].unique()
    )
    df_company_filtered = df_merged_filtered[df_merged_filtered['company_name'].isin(selected_company)]

    fig_revenue = px.line(
        df_company_filtered,
        x='month',
        y='monthly_revenue_eur',
        color='company_name',
        markers=True,
        title="Umsatz pro Monat und Tochtergesellschaft"
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

    # Umsatz pro Mitarbeiter nach Branche
    st.subheader("Umsatz pro Mitarbeiter nach Branche")
    df_industry_avg = df_merged_filtered.groupby(['month', 'industry'], as_index=False)['revenue_per_employee'].mean()
    fig_efficiency = px.line(
        df_industry_avg,
        x='month',
        y='revenue_per_employee',
        color='industry',
        markers=True,
        title="Durchschnittlicher Umsatz pro Mitarbeiter nach Branche"
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)

    # Vergleich Branchen - aktueller Monat
    st.subheader("Vergleich Branchen - aktueller Monat")
    latest_month = df_merged_filtered['month'].max()
    df_latest = df_merged_filtered[df_merged_filtered['month'] == latest_month]
    fig_industry_bar = px.bar(
        df_latest.groupby('industry', as_index=False)['revenue_per_employee'].mean(),
        x='industry',
        y='revenue_per_employee',
        title=f"Durchschnittlicher Umsatz pro Mitarbeiter - {latest_month.strftime('%Y-%m')}"
    )
    st.plotly_chart(fig_industry_bar, use_container_width=True)

    # Umsatzanteil pro Tochtergesellschaft
    st.subheader("Umsatzanteil pro Tochtergesellschaft")
    df_stack = df_merged_filtered.groupby(['month','company_name'], as_index=False)['monthly_revenue_eur'].sum()
    fig_stack = px.bar(
        df_stack,
        x='month',
        y='monthly_revenue_eur',
        color='company_name',
        title="Stacked Bar: Umsatzanteil pro Tochtergesellschaft"
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # Umsatz nach Standort/Branche
    st.subheader("Umsatz nach Standort/Branche")
    df_pie = df_merged_filtered.groupby('location', as_index=False)['monthly_revenue_eur'].sum()
    fig_pie = px.pie(
        df_pie,
        names='location',
        values='monthly_revenue_eur',
        title="Umsatz nach Standort"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Headcount vs Umsatz
    st.subheader("Headcount vs Umsatz (Skalierung)")
    fig_scatter = px.scatter(
        df_merged_filtered,
        x='employee_count',
        y='monthly_revenue_eur',
        color='industry',
        size='monthly_revenue_eur',
        hover_data=['company_name'],
        title="Headcount vs Umsatz pro Tochtergesellschaft"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Headcount-Entwicklung vs Umsatz-Entwicklung
    df_dual = df_merged_filtered.groupby('month', as_index=False)[['monthly_revenue_eur','employee_count']].sum()
    # Headcount prozentual zur Anfangsperiode
    df_dual['employee_count_pct'] = 100 * df_dual['employee_count'] / df_dual['employee_count'].iloc[0]

    # Dual-Axis Plot
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])

    # Umsatzlinie (primäre y-Achse)
    fig_dual.add_trace(
        go.Scatter(x=df_dual['month'], y=df_dual['monthly_revenue_eur'], name='Gesamtumsatz (€)', mode='lines+markers'),
        secondary_y=False
    )

    # Headcountlinie (sekundäre y-Achse)
    fig_dual.add_trace(
        go.Scatter(x=df_dual['month'], y=df_dual['employee_count_pct'], name='Headcount (% vom Start)', mode='lines+markers', line=dict(dash='dot')),
        secondary_y=True
    )

    # Achsentitel
    fig_dual.update_xaxes(title_text="Monat")
    fig_dual.update_yaxes(title_text="Gesamtumsatz (€)", secondary_y=False)
    fig_dual.update_yaxes(title_text="Headcount (% vom Start)", secondary_y=True)

    # Layout
    fig_dual.update_layout(
        title_text="Umsatz und Headcount über die Zeit (Headcount relativ)",
        legend=dict(x=0.01, y=0.99)
    )

    st.plotly_chart(fig_dual, use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE 4: Finance Use Case - Umsatz pro Mitarbeiter Analyse
# ---------------------------------------------------------------------------
if page == "Finance Use Case":
    st.title("Umsatz pro Mitarbeiter - Gesellschaftsübersicht")

    if df_merged_filtered.empty:
        st.warning("Keine Daten für das ausgewählte Jahr verfügbar.")
    else:
        # 1️⃣ Filter: letzte 6 Monate
        six_months_ago = today - pd.DateOffset(months=6)
        df_recent = df_merged_filtered[df_merged_filtered['month'] > six_months_ago]

        if df_recent.empty:
            st.warning("Keine Daten für die letzten 6 Monate vorhanden.")
        else:
            # 2️⃣ Durchschnitt pro Gesellschaft
            df_avg = df_recent.groupby('company_name', as_index=False)['revenue_per_employee'].mean()

            # 3️⃣ Gesamt-Durchschnitt
            overall_avg = df_avg['revenue_per_employee'].mean()
            st.metric("Gesamt-Durchschnitt Umsatz pro Mitarbeiter (EUR)", f"{overall_avg:,.2f}")

            # 4️⃣ Unterdurchschnittliche Gesellschaften
            df_underperformers = df_avg[df_avg['revenue_per_employee'] < overall_avg]
            st.subheader("Unterdurchschnittliche Gesellschaften")
            st.dataframe(df_underperformers.sort_values('revenue_per_employee'), use_container_width=True)

            # 5️⃣ Heatmap der Performance
            st.subheader("Umsatz pro Mitarbeiter Heatmap")
            heatmap_data = df_avg.copy()
            heatmap_data['color'] = np.where(
                heatmap_data['revenue_per_employee'] >= overall_avg, "green",
                np.where(heatmap_data['revenue_per_employee'] >= 0.9*overall_avg, "yellow", "red")
            )
            fig = px.bar(
                heatmap_data,
                x='company_name',
                y='revenue_per_employee',
                color='color',
                color_discrete_map={"green": "green", "yellow": "yellow", "red": "red"},
                title="Umsatz pro Mitarbeiter nach Gesellschaft"
            )
            st.plotly_chart(fig, use_container_width=True)

            # 6️⃣ Zeitreihe pro Gesellschaft
            st.subheader("Entwicklung der letzten 6 Monate")
            fig_trend = px.line(
                df_recent,
                x='month',
                y='revenue_per_employee',
                color='company_name',
                markers=True,
                title="Umsatz pro Mitarbeiter (letzte 6 Monate)"
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # 7️⃣ Optional: Filter nach Branche
            industry_list = df_recent['industry'].unique()
            selected_industry = st.selectbox("Branche auswählen", industry_list)

            if selected_industry:
                df_industry = df_recent[df_recent['industry'] == selected_industry]
                if df_industry.empty:
                    st.warning(f"Keine Daten für Branche {selected_industry} in den letzten 6 Monaten.")
                else:
                    fig_industry = px.line(
                        df_industry,
                        x='month',
                        y='revenue_per_employee',
                        color='company_name',
                        markers=True,
                        title=f"Umsatz pro Mitarbeiter - Branche: {selected_industry}"
                    )
                    st.plotly_chart(fig_industry, use_container_width=True)

