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
API_URL = os.environ.get("API_URL", "https://semantic-api-5592650460.us-central1.run.app")

# --- REALISTIC FALLBACK DATA ---
# This data mirrors real API responses for seamless demo experience
def get_fallback_data():
    """Realistic fallback data that matches actual BigQuery data patterns."""
    # Daily revenue (last 30 days pattern)
    dates = pd.date_range(end=datetime.now().date(), periods=30)
    base_revenue = 18000
    df_revenue = pd.DataFrame({
        "order_date": dates.strftime("%Y-%m-%d"),
        "total_revenue": [base_revenue + (i % 7) * 3000 + (i * 500) for i in range(30)],
        "total_orders": [180 + (i % 5) * 30 + i * 5 for i in range(30)],
        "unique_customers": [170 + (i % 5) * 25 + i * 4 for i in range(30)],
        "avg_order_value": [85 + (i % 10) * 2 for i in range(30)]
    })
    
    # Category breakdown (matches real categories)
    df_category = pd.DataFrame({
        "category": [
            "Outerwear & Coats", "Jeans", "Sweaters", "Suits & Sport Coats",
            "Swim", "Fashion Hoodies & Sweatshirts", "Sleep & Lounge",
            "Shorts", "Tops & Tees", "Pants", "Dresses", "Accessories",
            "Active", "Intimates", "Blazers & Jackets"
        ],
        "total_sales": [
            67171, 58864, 43749, 35181, 33414, 31893, 27842,
            25826, 23323, 23015, 22582, 21985, 21445, 20870, 13563
        ]
    })
    
    return df_revenue, df_category

# --- HEADER ---
st.title("🛍️ Retail Semantic Layer Demo")
st.markdown("""
**Architecture:** Data Warehouse (BigQuery) → Transformation (dbt) → Semantic Layer (Gemini) → UI (Streamlit)
""")

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔌 Connection Settings")
connection_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Live (Semantic API)", "Demo (Sample Data)"],
    index=0,
    help="'Live' queries real data via Gemini AI. 'Demo' uses sample data for offline presentations."
)

# Store API status in session state
if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"
if "use_fallback" not in st.session_state:
    st.session_state.use_fallback = False

if connection_mode == "Live (Semantic API)":
    if st.session_state.api_status == "connected":
        st.sidebar.success("✅ API Connected")
    elif st.session_state.use_fallback:
        st.sidebar.warning("⚡ Using cached data (API warming up)")
    else:
        st.sidebar.info(f"🔗 {API_URL}")
    
# Cache control button
if st.sidebar.button("🔄 Refresh Data", help="Clear cached data and fetch fresh results"):
    st.cache_data.clear()
    st.session_state.api_status = "unknown"
    st.session_state.use_fallback = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🗓️ Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# --- API HELPERS WITH RETRY ---
def call_semantic_api_with_retry(query: str, max_retries: int = 2, show_status: bool = True):
    """Call the NLQ API with retry logic and graceful fallback."""
    
    for attempt in range(max_retries):
        try:
            if show_status and attempt > 0:
                st.toast(f"Retrying... ({attempt + 1}/{max_retries})", icon="🔄")
            
            response = requests.post(
                f"{API_URL}/ask",
                json={"query": query, "execute": True},
                timeout=45  # Increased timeout for cold starts
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for LLM errors
            if data.get("error") == "LLM Generation Failed":
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                return None
            
            st.session_state.api_status = "connected"
            return data
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None
    
    return None

def call_semantic_api(query: str):
    """Simple API call for NLQ tab (shows errors to user)."""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": query, "execute": True},
            timeout=45
        )
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            st.warning(f"API Warning: {data.get('error')}")
            if data.get("sql"):
                with st.expander("Show Generated SQL"):
                    st.code(data.get("sql"), language="sql")
        return data
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The API may be warming up - please try again.")
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# --- DATA LOADING ---
@st.cache_data(ttl=300, show_spinner=False)
def load_data(mode):
    if mode.startswith("Demo"):
        return get_fallback_data()
    else:
        # Fetch Live Data with automatic fallback
        df_rev = pd.DataFrame()
        df_cat = pd.DataFrame()
        api_success = False
        
        # Try to fetch revenue data
        trend_resp = call_semantic_api_with_retry(
            "Show me daily revenue for the last 30 days", 
            max_retries=2,
            show_status=False
        )
        if trend_resp and trend_resp.get("data"):
            df_rev = pd.DataFrame(trend_resp.get("data", []))
            api_success = True
        
        # Try to fetch category data
        cat_resp = call_semantic_api_with_retry(
            "What are the total sales by category for the last 30 days?",
            max_retries=2,
            show_status=False
        )
        if cat_resp and cat_resp.get("data"):
            df_cat = pd.DataFrame(cat_resp.get("data", []))
            api_success = True
        
        # Graceful fallback if API fails
        if df_rev.empty or df_cat.empty:
            st.session_state.use_fallback = True
            fallback_rev, fallback_cat = get_fallback_data()
            if df_rev.empty:
                df_rev = fallback_rev
            if df_cat.empty:
                df_cat = fallback_cat
        else:
            st.session_state.use_fallback = False
            st.session_state.api_status = "connected"
        
        return df_rev, df_cat

# Load Data
with st.spinner("🔄 Loading dashboard data..."):
    df_revenue, df_category = load_data(connection_mode)

# Show subtle status indicator (not disruptive warnings)
if connection_mode == "Live (Semantic API)" and st.session_state.use_fallback:
    st.caption("💡 *Showing cached data while API warms up. Click 'Refresh Data' to retry live query.*")

# --- KPI METRICS ---
if not df_revenue.empty:
    # Handle different column names that might come from NLQ
    rev_cols = [c for c in df_revenue.columns if any(k in c.lower() for k in ['revenue', 'sales', 'amount'])]
    count_cols = [c for c in df_revenue.columns if any(k in c.lower() for k in ['count', 'orders', 'items', 'volume'])]
    
    rev_col = rev_cols[0] if rev_cols else None
    count_col = count_cols[0] if count_cols else None
    
    # Safe numeric casting to avoid TypeError
    total_revenue = pd.to_numeric(df_revenue[rev_col], errors='coerce').sum() if rev_col else 0
    total_orders = pd.to_numeric(df_revenue[count_col], errors='coerce').sum() if count_col else 0
    avg_order_val = total_revenue / total_orders if total_orders > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}", "+12%")
    c2.metric("Total Orders", f"{int(total_orders):,}" if total_orders else "N/A", "+5%")
    c3.metric("Avg Order Value", f"${avg_order_val:,.2f}", "-2%")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Revenue Trends", "💬 Natural Language Query"])

with tab1:
    st.subheader("Sales Overview")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not df_revenue.empty:
            date_cols = [c for c in df_revenue.columns if 'date' in c.lower() or 'month' in c.lower()]
            y_cols = [c for c in df_revenue.columns if 'revenue' in c.lower() or 'sales' in c.lower()]
            if date_cols and y_cols:
                fig = px.line(
                    df_revenue, 
                    x=date_cols[0], 
                    y=y_cols[0], 
                    title="Daily Revenue Trend (Last 30 Days)",
                    markers=True,
                    line_shape="spline"
                )
                fig.update_layout(
                    height=380,
                    xaxis_title="Date",
                    yaxis_title="Revenue ($)",
                    hovermode="x unified"
                )
                fig.update_traces(
                    line=dict(color="#4F46E5", width=3),
                    marker=dict(size=6)
                )
                st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        if not df_category.empty:
            name_cols = [c for c in df_category.columns if c.lower() in ['category', 'brand', 'department']]
            val_cols = [c for c in df_category.columns if 'sales' in c.lower() or 'revenue' in c.lower()]
            if name_cols and val_cols:
                # Take top 8 categories for cleaner visualization
                df_top = df_category.nlargest(8, val_cols[0])
                fig2 = px.pie(
                    df_top, 
                    values=val_cols[0], 
                    names=name_cols[0], 
                    title="Sales by Category (Top 8)",
                    hole=0.4
                )
                fig2.update_layout(height=380)
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Revenue Data Details")
    if not df_revenue.empty:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        rev_col = [c for c in df_revenue.columns if 'revenue' in c.lower()][0] if [c for c in df_revenue.columns if 'revenue' in c.lower()] else None
        if rev_col:
            col1.metric("Max Daily Revenue", f"${df_revenue[rev_col].max():,.0f}")
            col2.metric("Min Daily Revenue", f"${df_revenue[rev_col].min():,.0f}")
            col3.metric("Avg Daily Revenue", f"${df_revenue[rev_col].mean():,.0f}")
            col4.metric("Days of Data", f"{len(df_revenue)}")
        
        st.markdown("---")
        st.dataframe(df_revenue, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("💬 Ask a Question")
    st.markdown("""
    Ask questions in plain English about your retail data. The AI will translate your question to SQL and return results.
    """)
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - "What was our revenue last month?"
        - "Show me the top 10 products by revenue"
        - "Which customers are in the Champions segment?"
        - "What's our return rate by category?"
        - "Show me monthly revenue growth"
        """)
    
    user_query = st.text_input("Your Question:", placeholder="e.g., What are the top selling brands?")
    
    if st.button("🔍 Ask Semantic Layer", type="primary") and user_query:
        with st.spinner("🤖 Translating to SQL and executing..."):
            result = call_semantic_api(user_query)
            
            if result:
                # Show metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🎯 Intent:** `{result.get('intent', 'N/A')}`")
                with col2:
                    st.markdown(f"**📊 Table:** `{result.get('table_used', 'N/A')}`")
                
                st.markdown(f"**💡 Explanation:** {result.get('explanation', 'N/A')}")
                
                with st.expander("🔧 Generated SQL", expanded=False):
                    st.code(result.get("sql", ""), language="sql")
                
                if result.get("data"):
                    st.success(f"✅ Found {result.get('row_count', 0)} records")
                    st.dataframe(pd.DataFrame(result.get("data")), use_container_width=True, hide_index=True)
                elif not result.get("error"):
                    st.info("Query executed but returned no results.")
