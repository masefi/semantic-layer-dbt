from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI(title="Retail Semantic Layer NLQ API")

class NLQRequest(BaseModel):
    query: str
    user_id: Optional[str] = "demo_user"

class CubeQuery(BaseModel):
    measures: List[str]
    dimensions: List[str]
    filters: Optional[List[dict]] = None
    timeDimensions: Optional[List[dict]] = None

class NLQResponse(BaseModel):
    original_query: str
    interpreted_intent: str
    cube_query: CubeQuery
    sql_generated: str
    data: dict

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Retail Semantic NLQ API"}

@app.post("/ask", response_model=NLQResponse)
def ask_question(request: NLQRequest):
    """
    Translates natural language to Semantic Layer (Cube) query.
    MOCK IMPLEMENTATION for demo.
    """
    q = request.query.lower()
    
    # Simple Mock Logic
    intent = "unknown"
    cube_q = CubeQuery(measures=[], dimensions=[])
    sql = ""
    data = {}
    
    if "revenue" in q:
        intent = "analyze_revenue"
        cube_q = CubeQuery(
            measures=["Orders.totalRevenue"], 
            dimensions=[],
            timeDimensions=[{"dimension": "Orders.orderDate", "granularity": "day"}]
        )
        sql = "SELECT order_date, SUM(revenue) FROM orders GROUP BY 1"
        data = {"result": "$1.2M", "trend": "up"}
        
    elif "orders" in q or "sales" in q:
        intent = "analyze_order_count"
        cube_q = CubeQuery(
            measures=["Orders.count"], 
            dimensions=["Orders.status"]
        )
        sql = "SELECT status, COUNT(*) FROM orders GROUP BY 1"
        data = {"count": 14500}
        
    elif "users" in q or "customers" in q:
        intent = "analyze_users"
        cube_q = CubeQuery(
            measures=["Users.count"], 
            dimensions=["Users.country"]
        )
        sql = "SELECT country, COUNT(*) FROM users GROUP BY 1"
        data = {"total_users": 5200}
        
    # Simulate thinking time
    time.sleep(1)
    
    return NLQResponse(
        original_query=request.query,
        interpreted_intent=intent,
        cube_query=cube_q,
        sql_generated=sql,
        data=data
    )
