import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
import os
from datetime import datetime, timedelta

# Page Config
st.set_page_config(
    page_title="Retail Semantic Layer Demo",
    page_icon="🛍️",
    layout="wide"
)

# API Configuration
# Actual service URL: https://semantic-api-wh4agku6ma-uc.a.run.app
API_URL = os.environ.get("API_URL", "https://semantic-api-wh4agku6ma-uc.a.run.app")

# --- HEADER ---
st.title("🛍️ Retail Semantic Layer Demo")
st.markdown("""
**Architecture:** Data Warehouse (BigQuery) → Transformation (dbt) → Semantic Layer (Gemini) → UI (Streamlit)
""")

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔌 Connection Settings")
connection_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Mock (Demo)", "Live (Semantic API)"],
    index=0,
    help="Select 'Mock' to simulate responses or 'Live' to query real data via Gemini NLQ API."
)

if connection_mode == "Live (Semantic API)":
    st.sidebar.success(f"Connected to: {API_URL}")

st.sidebar.markdown("---")
st.sidebar.header("🗓️ Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime(2023, 1, 1), datetime(2023, 1, 31))
)

status_filter = st.sidebar.multiselect(
    "Order Status",
    ["Complete", "Processing", "Shipped", "Returned", "Cancelled"],
    default=["Complete", "Processing", "Shipped"]
)

# --- API HELPERS ---
def call_semantic_api(query: str):
    """Call the NLQ API to get data."""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": query, "execute": True},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# --- MOCK DATA GENERATOR ---
def get_mock_data():
    # Simulate daily revenue
    dates = pd.date_range(start="2023-01-01", end="2023-01-31")
    df_revenue = pd.DataFrame({
        "order_date": dates,
        "daily_revenue": [x * 1000 + (x % 5) * 500 for x in range(len(dates))],
        "order_count": [x * 10 + (x % 3) * 5 for x in range(len(dates))]
    })
    
    # Simulate category breakdown
    df_category = pd.DataFrame({
        "category": ["Men", "Women", "Accessories", "Active", "Juniors"],
        "sales": [45000, 52000, 15000, 22000, 18000]
    })
    
    return df_revenue, df_category

# --- DATA LOADING ---
@st.cache_data
def load_data(mode):
    if mode.startswith("Mock"):
        time.sleep(0.5) # Simulate API latency
        return get_mock_data()
    else:
        # Fetch Live Data for Dashboards
        with st.spinner("Fetching live performance metrics..."):
            # 1. Trend Data
            trend_resp = call_semantic_api("Show me daily revenue for the last 30 days")
            df_rev = pd.DataFrame(trend_resp.get("data", [])) if trend_resp else pd.DataFrame()
            
            # 2. Category Data
            cat_resp = call_semantic_api("What are the total sales by category for the last 30 days?")
            df_cat = pd.DataFrame(cat_resp.get("data", [])) if cat_resp else pd.DataFrame()
            
            if df_rev.empty or df_cat.empty:
                st.warning("Could not fetch some live data. Falling back to empty tables.")
            
            return df_rev, df_cat

# Load Data
df_revenue, df_category = load_data(connection_mode)

# --- KPI METRICS ---
if not df_revenue.empty:
    # Handle different column names that might come from NLQ
    rev_col = [c for c in df_revenue.columns if 'revenue' in c.lower() or 'sales' in c.lower()][0]
    count_col = [c for c in df_revenue.columns if 'count' in c.lower() or 'orders' in c.lower()]
    count_col = count_col[0] if count_col else None

    total_revenue = df_revenue[rev_col].sum()
    total_orders = df_revenue[count_col].sum() if count_col else 0
    avg_order_val = total_revenue / total_orders if total_orders > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}", "+12%")
    c2.metric("Total Orders", f"{total_orders:,.0f}" if total_orders else "N/A", "+5%")
    c3.metric("Avg Order Value", f"${avg_order_val:,.2f}", "-2%")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Overview", "Revenue Trends", "Natural Language Query"])

with tab1:
    st.subheader("Sales Overview")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not df_revenue.empty:
            date_col = [c for c in df_revenue.columns if 'date' in c.lower() or 'month' in c.lower()][0]
            y_col = [c for c in df_revenue.columns if 'revenue' in c.lower() or 'sales' in c.lower()][0]
            fig = px.line(df_revenue, x=date_col, y=y_col, 
                         title="Daily Revenue Trend", markers=True,
                         line_shape="spline")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        if not df_category.empty:
            name_col = [c for c in df_category.columns if c.lower() in ['category', 'brand', 'department']][0]
            val_col = [c for c in df_category.columns if 'sales' in c.lower() or 'revenue' in c.lower()][0]
            fig2 = px.pie(df_category, values=val_col, names=name_col, 
                         title="Sales Breakdown", hole=0.4)
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Detailed Data View")
    if not df_revenue.empty:
        st.dataframe(df_revenue, use_container_width=True)

with tab3:
    st.subheader("💬 Ask a Question (NLQ)")
    st.info("Ask questions like: 'What was the revenue last week?' or 'Which brand sold the most?'")
    user_query = st.text_input("Your Question:")
    
    if st.button("Ask Semantic Layer") and user_query:
        with st.spinner("Translating natural language to SQL..."):
            result = call_semantic_api(user_query)
            
            if result:
                st.markdown(f"**Intent:** {result.get('intent')}")
                st.markdown(f"**Explanation:** {result.get('explanation')}")
                
                with st.expander("Show Generated SQL"):
                    st.code(result.get("sql"), language="sql")
                
                if result.get("data"):
                    st.success(f"Found {result.get('row_count')} records")
                    st.dataframe(pd.DataFrame(result.get("data")), use_container_width=True)
                else:
                    st.warning("No data returned for this query.")
