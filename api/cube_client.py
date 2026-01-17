"""
Cube REST API Client for the Retail Semantic Layer.

This module provides a Python client for interacting with the Cube REST API,
enabling standardized metric queries with caching and governance.
"""

import os
import requests
import jwt
import time
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Cube API Configuration
CUBE_API_URL = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
CUBE_API_SECRET = os.environ.get("CUBEJS_API_SECRET", "retail-semantic-layer-secret-key-change-me")


def generate_cube_token(expiry_seconds: int = 3600) -> str:
    """Generate a JWT token for Cube API authentication."""
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + expiry_seconds
    }
    return jwt.encode(payload, CUBE_API_SECRET, algorithm="HS256")


def get_cube_headers() -> Dict[str, str]:
    """Get headers for Cube API requests."""
    return {
        "Authorization": generate_cube_token(),
        "Content-Type": "application/json"
    }


def check_cube_health() -> bool:
    """Check if Cube server is healthy."""
    try:
        response = requests.get(
            f"{CUBE_API_URL.replace('/cubejs-api/v1', '')}/readyz",
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Cube health check failed: {e}")
        return False


def get_cube_meta() -> Optional[Dict[str, Any]]:
    """Get Cube metadata (available cubes, measures, dimensions)."""
    try:
        response = requests.get(
            f"{CUBE_API_URL}/meta",
            headers=get_cube_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get Cube metadata: {e}")
        return None


def query_cube(
    measures: List[str],
    dimensions: Optional[List[str]] = None,
    filters: Optional[List[Dict]] = None,
    time_dimensions: Optional[List[Dict]] = None,
    order: Optional[Dict[str, str]] = None,
    limit: int = 100
) -> Optional[Dict[str, Any]]:
    """
    Execute a query against Cube REST API.
    
    Args:
        measures: List of measures like ["orders.count", "orders.total_revenue"]
        dimensions: List of dimensions like ["orders.status", "users.country"]
        filters: List of filter objects
        time_dimensions: List of time dimension objects for date filtering
        order: Dict of ordering like {"orders.total_revenue": "desc"}
        limit: Max rows to return
        
    Returns:
        Query result with data array or None on error
    """
    query = {
        "measures": measures,
        "limit": limit
    }
    
    if dimensions:
        query["dimensions"] = dimensions
    if filters:
        query["filters"] = filters
    if time_dimensions:
        query["timeDimensions"] = time_dimensions
    if order:
        query["order"] = order
    
    try:
        logger.info(f"Cube query: {query}")
        response = requests.post(
            f"{CUBE_API_URL}/load",
            headers=get_cube_headers(),
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Cube response: {len(result.get('data', []))} rows")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Cube query failed: {e}")
        return None


# Pre-defined queries for common metrics
def get_total_revenue_by_date(days: int = 30) -> Optional[Dict[str, Any]]:
    """Get daily revenue for the last N days using Cube."""
    return query_cube(
        measures=["revenue_daily.total_revenue", "revenue_daily.total_orders"],
        dimensions=[],
        time_dimensions=[{
            "dimension": "revenue_daily.date",
            "dateRange": f"last {days} days",
            "granularity": "day"
        }],
        order={"revenue_daily.date": "asc"}
    )


def get_revenue_by_country() -> Optional[Dict[str, Any]]:
    """Get total revenue grouped by country using Cube."""
    return query_cube(
        measures=["orders.total_revenue", "orders.count"],
        dimensions=["orders.country"],
        order={"orders.total_revenue": "desc"},
        limit=20
    )


def get_order_metrics() -> Optional[Dict[str, Any]]:
    """Get high-level order metrics using Cube."""
    return query_cube(
        measures=["orders.count", "orders.total_revenue", "orders.avg_order_value"],
        dimensions=[]
    )


def get_user_metrics() -> Optional[Dict[str, Any]]:
    """Get user count and activity metrics using Cube."""
    return query_cube(
        measures=["users.count", "users.total_orders_placed"],
        dimensions=[]
    )


def get_orders_by_status() -> Optional[Dict[str, Any]]:
    """Get order count by status using Cube."""
    return query_cube(
        measures=["orders.count", "orders.total_revenue"],
        dimensions=["orders.status"],
        order={"orders.count": "desc"}
    )


# Mapping from natural language intents to Cube queries
INTENT_TO_CUBE_QUERY = {
    "total_revenue": lambda: query_cube(
        measures=["orders.total_revenue"],
        dimensions=[]
    ),
    "total_orders": lambda: query_cube(
        measures=["orders.count"],
        dimensions=[]
    ),
    "revenue_by_country": get_revenue_by_country,
    "orders_by_status": get_orders_by_status,
    "daily_revenue": lambda: get_total_revenue_by_date(30),
    "user_count": get_user_metrics,
}


def execute_cube_intent(intent: str) -> Optional[Dict[str, Any]]:
    """
    Execute a pre-defined Cube query based on intent.
    
    This allows the Gemini NLQ to identify the intent, then we execute
    the corresponding optimized Cube query.
    """
    if intent in INTENT_TO_CUBE_QUERY:
        return INTENT_TO_CUBE_QUERY[intent]()
    return None
