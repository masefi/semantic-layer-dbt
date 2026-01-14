import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# Page Config
st.set_page_config(
    page_title="Retail Semantic Layer Demo",
    page_icon="🛍️",
    layout="wide"
)

# --- HEADER ---
st.title("🛍️ Retail Semantic Layer Demo")
st.markdown("""
**Architecture:** Data Warehouse (BigQuery) → Transformation (dbt) → Semantic Layer (Cube) → UI (Streamlit)
""")

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔌 Connection Settings")
connection_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Mock (Demo)", "Live (Cube API)"],
    index=0,
    help="Select 'Mock' to simulate Cube responses for demo purposes without running a local Cube server."
)

if connection_mode == "Live (Cube API)":
    cube_url = st.sidebar.text_input("Cube API URL", "http://localhost:4000/cubejs-api/v1")
    cube_token = st.sidebar.text_input("Security Token", type="password")

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
        st.error("Live connection not implemented yet. Please switch to Mock mode.")
        return pd.DataFrame(), pd.DataFrame()

# Load Data
df_revenue, df_category = load_data(connection_mode)

# --- KPI METRICS ---
if not df_revenue.empty:
    total_revenue = df_revenue["daily_revenue"].sum()
    total_orders = df_revenue["order_count"].sum()
    avg_order_val = total_revenue / total_orders if total_orders > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}", "+12%")
    c2.metric("Total Orders", f"{total_orders:,.0f}", "+5%")
    c3.metric("Avg Order Value", f"${avg_order_val:,.2f}", "-2%")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Overview", "Revenue Trends", "Natural Language Query"])

with tab1:
    st.subheader("Sales Overview")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not df_revenue.empty:
            fig = px.line(df_revenue, x="order_date", y="daily_revenue", 
                         title="Daily Revenue Trend", markers=True,
                         line_shape="spline")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        if not df_category.empty:
            fig2 = px.pie(df_category, values="sales", names="category", 
                         title="Sales by Category", hole=0.4)
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Detailed Revenue Analysis")
    st.markdown("*(More detailed pivots and breakdown dimensions would go here powered by Cube)*")
    if not df_revenue.empty:
        st.dataframe(df_revenue, use_container_width=True)

with tab3:
    st.subheader("💬 Ask a Question (NLQ)")
    st.info("Ask questions like: 'What was the revenue last week?'")
    user_query = st.text_input("Your Question:")
    
    if st.button("Ask Semantic Layer"):
        with st.spinner("Translating natural language to Cube query..."):
            time.sleep(1.5) # Simulate processing
            
            # Simulated Response
            st.markdown(f"**Interpreted Query:** `Orders.totalRevenue` filtered by date")
            
            st.code("""
{
  "measures": ["Orders.totalRevenue"],
  "timeDimensions": [{
    "dimension": "Orders.orderDate",
    "dateRange": "Last 7 days"
  }]
}
            """, language="json")
            
            st.success("Result: $42,500")
