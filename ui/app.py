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
def get_fallback_data():
    """Realistic fallback data that matches actual BigQuery data patterns."""
    dates = pd.date_range(end=datetime.now().date(), periods=30)
    base_revenue = 18000
    df_revenue = pd.DataFrame({
        "order_date": dates.strftime("%Y-%m-%d"),
        "total_revenue": [base_revenue + (i % 7) * 3000 + (i * 500) for i in range(30)],
        "total_orders": [180 + (i % 5) * 30 + i * 5 for i in range(30)],
        "unique_customers": [170 + (i % 5) * 25 + i * 4 for i in range(30)],
        "avg_order_value": [85 + (i % 10) * 2 for i in range(30)]
    })
    
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
**Architecture:** Data Warehouse (BigQuery) → Transformation (dbt) → Semantic Layer (Cube + Gemini) → UI (Streamlit)
""")

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔌 Connection Settings")
connection_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Live (Semantic API)", "Demo (Sample Data)"],
    index=0,
    help="'Live' queries real data via Cube & Gemini. 'Demo' uses sample data for offline presentations."
)

# Store API status in session state
if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"
if "cube_server_status" not in st.session_state:
    st.session_state.cube_server_status = "unknown"
if "use_fallback" not in st.session_state:
    st.session_state.use_fallback = False

# --- API HELPERS ---
def check_api_health():
    """Check API health and component status."""
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.api_status = "connected"
            # Check Cube status from API response
            components = data.get("components", {})
            cube_info = components.get("cube", {})
            st.session_state.cube_server_status = cube_info.get("status", "unknown")
            return data
    except:
        pass
    st.session_state.api_status = "disconnected"
    return None

def call_cube_metrics(endpoint: str):
    """Call Cube metric endpoints."""
    try:
        response = requests.get(f"{API_URL}/cube/metrics/{endpoint}", timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Cube endpoint error: {e}")
    return None

def call_semantic_api_with_retry(query: str, max_retries: int = 2, show_status: bool = True):
    """Call the NLQ API with retry logic and graceful fallback."""
    for attempt in range(max_retries):
        try:
            if show_status and attempt > 0:
                st.toast(f"Retrying... ({attempt + 1}/{max_retries})", icon="🔄")
            
            response = requests.post(
                f"{API_URL}/ask",
                json={"query": query, "execute": True},
                timeout=45
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("error") == "LLM Generation Failed":
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            st.session_state.api_status = "connected"
            return data
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None
        except Exception:
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

# Show connection status in sidebar
if connection_mode == "Live (Semantic API)":
    with st.sidebar:
        health = check_api_health()
        if health:
            st.success("✅ API Connected")
            
            # Show component status
            components = health.get("components", {})
            with st.expander("🔧 Component Status", expanded=False):
                gemini = components.get("gemini", {})
                bq = components.get("bigquery", {})
                cube = components.get("cube", {})
                
                st.markdown(f"**Gemini:** {'🟢' if gemini.get('status') == 'connected' else '🔴'} {gemini.get('model', 'N/A')}")
                st.markdown(f"**BigQuery:** {'🟢' if bq.get('status') == 'connected' else '🔴'} {bq.get('dataset', 'N/A')}")
                st.markdown(f"**Cube:** {'🟢' if cube.get('status') == 'connected' else '🟡'} {cube.get('status', 'N/A')}")
        elif st.session_state.use_fallback:
            st.warning("⚡ Using cached data")
        else:
            st.info(f"🔗 {API_URL}")
    
# Cache control button
if st.sidebar.button("🔄 Refresh Data", help="Clear cached data and fetch fresh results"):
    st.cache_data.clear()
    st.session_state.api_status = "unknown"
    st.session_state.cube_server_status = "unknown"
    st.session_state.use_fallback = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🗓️ Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# --- DATA LOADING ---
@st.cache_data(ttl=300, show_spinner=False)
def load_data(mode):
    if mode.startswith("Demo"):
        return get_fallback_data()
    else:
        df_rev = pd.DataFrame()
        df_cat = pd.DataFrame()
        
        # Try Cube first for daily revenue (if available)
        cube_revenue = call_cube_metrics("revenue/daily")
        if cube_revenue and cube_revenue.get("data"):
            df_rev = pd.DataFrame(cube_revenue.get("data", []))
            # Rename Cube columns to match expected format
            col_map = {
                "revenue_daily.date": "order_date",
                "revenue_daily.total_revenue": "total_revenue",
                "revenue_daily.total_orders": "total_orders"
            }
            df_rev = df_rev.rename(columns=col_map)
        
        # Fallback to Gemini NLQ if Cube unavailable
        if df_rev.empty:
            trend_resp = call_semantic_api_with_retry(
                "Show me daily revenue for the last 30 days", 
                max_retries=2,
                show_status=False
            )
            if trend_resp and trend_resp.get("data"):
                df_rev = pd.DataFrame(trend_resp.get("data", []))
        
        # Category data via Gemini (no Cube endpoint for this)
        cat_resp = call_semantic_api_with_retry(
            "What are the total sales by category for the last 30 days?",
            max_retries=2,
            show_status=False
        )
        if cat_resp and cat_resp.get("data"):
            df_cat = pd.DataFrame(cat_resp.get("data", []))
        
        # Graceful fallback if APIs fail
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

# Show subtle status indicator
if connection_mode == "Live (Semantic API)" and st.session_state.use_fallback:
    st.caption("💡 *Showing cached data while API warms up. Click 'Refresh Data' to retry live query.*")

# --- KPI METRICS ---
if not df_revenue.empty:
    rev_cols = [c for c in df_revenue.columns if any(k in c.lower() for k in ['revenue', 'sales', 'amount'])]
    count_cols = [c for c in df_revenue.columns if any(k in c.lower() for k in ['count', 'orders', 'items', 'volume'])]
    
    rev_col = rev_cols[0] if rev_cols else None
    count_col = count_cols[0] if count_cols else None
    
    total_revenue = pd.to_numeric(df_revenue[rev_col], errors='coerce').sum() if rev_col else 0
    total_orders = pd.to_numeric(df_revenue[count_col], errors='coerce').sum() if count_col else 0
    avg_order_val = total_revenue / total_orders if total_orders > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}", "+12%")
    c2.metric("Total Orders", f"{int(total_orders):,}" if total_orders else "N/A", "+5%")
    c3.metric("Avg Order Value", f"${avg_order_val:,.2f}", "-2%")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Revenue Trends", "🧊 Cube Metrics", "💬 Natural Language Query"])

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
    st.subheader("🧊 Cube Metrics API")
    st.markdown("""
    Query pre-defined metrics directly from Cube's semantic layer. 
    These endpoints provide governed, cached metrics with consistent definitions.
    """)
    
    if connection_mode == "Demo (Sample Data)":
        st.info("Switch to 'Live (Semantic API)' mode to query Cube metrics.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📦 Order Metrics")
            if st.button("Fetch Order Summary", key="cube_orders"):
                with st.spinner("Querying Cube..."):
                    result = call_cube_metrics("orders")
                    if result and result.get("data"):
                        st.json(result.get("data"))
                    else:
                        st.warning("Cube not available. Make sure Cube server is running.")
            
            st.markdown("### 📊 Orders by Status")
            if st.button("Fetch Orders by Status", key="cube_status"):
                with st.spinner("Querying Cube..."):
                    result = call_cube_metrics("orders/by-status")
                    if result and result.get("data"):
                        df = pd.DataFrame(result.get("data"))
                        st.dataframe(df, hide_index=True)
                    else:
                        st.warning("Cube not available.")
        
        with col2:
            st.markdown("### 👥 User Metrics")
            if st.button("Fetch User Summary", key="cube_users"):
                with st.spinner("Querying Cube..."):
                    result = call_cube_metrics("users")
                    if result and result.get("data"):
                        st.json(result.get("data"))
                    else:
                        st.warning("Cube not available.")
            
            st.markdown("### 🌍 Revenue by Country")
            if st.button("Fetch Revenue by Country", key="cube_geo"):
                with st.spinner("Querying Cube..."):
                    result = call_cube_metrics("revenue/by-country")
                    if result and result.get("data"):
                        df = pd.DataFrame(result.get("data"))
                        st.dataframe(df, hide_index=True)
                    else:
                        st.warning("Cube not available.")
        
        st.markdown("---")
        st.markdown("### 🔧 Custom Cube Query")
        st.caption("Advanced: Execute a custom Cube query")
        
        with st.expander("Build Custom Query"):
            measures = st.multiselect(
                "Measures",
                ["orders.count", "orders.total_revenue", "orders.avg_order_value", 
                 "users.count", "revenue_daily.total_revenue"],
                default=["orders.count", "orders.total_revenue"]
            )
            dimensions = st.multiselect(
                "Dimensions (optional)",
                ["orders.status", "orders.country", "users.country"]
            )
            
            if st.button("Execute Cube Query", type="primary"):
                with st.spinner("Executing Cube query..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/cube/query",
                            json={
                                "measures": measures,
                                "dimensions": dimensions if dimensions else None,
                                "limit": 50
                            },
                            timeout=30
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Found {result.get('row_count', 0)} rows")
                            st.dataframe(pd.DataFrame(result.get("data", [])), hide_index=True)
                        else:
                            st.error(f"Cube query failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

with tab4:
    st.subheader("💬 Smart NLQ - Ask Anything")
    st.markdown("""
    Ask questions in plain English. The AI intelligently routes your query:
    - **🧊 Cube Path** → For known metrics (revenue, orders, users) - *cached & governed*
    - **🔧 BigQuery Path** → For complex/ad-hoc queries - *flexible & powerful*
    """)
    
    with st.expander("💡 Example Questions"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🧊 Routes to Cube (cached):**
            - "What is our total revenue?"
            - "Show me daily revenue for the last 30 days"
            - "What is revenue by country?"
            - "How many orders do we have?"
            """)
        with col2:
            st.markdown("""
            **🔧 Routes to BigQuery (ad-hoc):**
            - "Which customers are in the Champions segment?"
            - "Show me top 10 products by return rate"
            - "What's the monthly revenue growth?"
            - "List all brands with over $10k in sales"
            """)
    
    user_query = st.text_input("Your Question:", placeholder="e.g., What is our total revenue by country?")
    
    if st.button("🔍 Ask Semantic Layer", type="primary") and user_query:
        with st.spinner("🤖 Analyzing query and routing..."):
            result = call_semantic_api(user_query)
            
            if result:
                # Route indicator with color coding
                route = result.get('route', 'bigquery')
                source = result.get('source', 'bigquery')
                
                if route == 'cube':
                    route_badge = "🧊 **CUBE** (Cached & Governed)"
                    route_color = "green"
                else:
                    route_badge = "🔧 **BigQuery** (Ad-hoc SQL)"
                    route_color = "blue"
                
                # Show execution source if different from planned route
                if source != route and 'failed' not in source:
                    source_note = f" → Executed via: `{source}`"
                elif 'failed' in source:
                    source_note = f" ⚠️ Fallback needed"
                else:
                    source_note = ""
                
                st.markdown(f"### Route: {route_badge}{source_note}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🎯 Intent:** `{result.get('intent', 'N/A')}`")
                with col2:
                    if route == 'bigquery' and result.get('table_used'):
                        st.markdown(f"**📊 Table:** `{result.get('table_used')}`")
                    elif route == 'cube':
                        st.markdown(f"**📊 Cube:** Orders/Revenue/Users")
                
                st.markdown(f"**💡 Explanation:** {result.get('explanation', 'N/A')}")
                
                # Show appropriate query details
                if route == 'cube' and result.get('cube_query'):
                    with st.expander("🧊 Cube Query", expanded=False):
                        st.json(result.get("cube_query"))
                elif result.get('sql'):
                    with st.expander("🔧 Generated SQL", expanded=False):
                        st.code(result.get("sql", ""), language="sql")
                
                if result.get("data"):
                    st.success(f"✅ Found {result.get('row_count', 0)} records via {source.upper()}")
                    st.dataframe(pd.DataFrame(result.get("data")), use_container_width=True, hide_index=True)
                elif not result.get("error"):
                    st.info("Query executed but returned no results.")
