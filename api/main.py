from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import os
import json
import logging
from prompts import SYSTEM_PROMPT, SCHEMA_SUMMARY

# Import Cube client
try:
    from cube_client import (
        check_cube_health,
        get_cube_meta,
        query_cube,
        get_total_revenue_by_date,
        get_revenue_by_country,
        get_order_metrics,
        get_user_metrics,
        get_orders_by_status
    )
    CUBE_AVAILABLE = True
except ImportError:
    CUBE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Retail Semantic Layer API",
    description="AI-powered semantic layer with Cube metrics and Gemini NLQ",
    version="2.0.0"
)

# Initialize clients at startup
def get_clients():
    project_id = os.environ.get("GCP_PROJECT_ID", "semantic-layer-484020")
    logger.info(f"Initializing Vertex AI with project: {project_id}")
    try:
        vertexai.init(project=project_id, location="us-central1")
        model_name = "gemini-2.5-flash"
        logger.info(f"Using model: {model_name}")
        llm = GenerativeModel(model_name) 
        bq = bigquery.Client(project=project_id)
        return llm, bq
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return None, None

llm_client, bq_client = None, None
cube_healthy = False

@app.on_event("startup")
async def startup_event():
    global llm_client, bq_client, cube_healthy
    llm_client, bq_client = get_clients()
    if CUBE_AVAILABLE:
        cube_healthy = check_cube_health()
        logger.info(f"Cube health: {'✅ Connected' if cube_healthy else '❌ Not available'}")

BQ_DATASET = os.environ.get("BQ_DATASET", "retail_marts_dev")

# ============================================================================
# Pydantic Models
# ============================================================================

class NLQRequest(BaseModel):
    query: str
    execute: bool = True
    
class NLQResponse(BaseModel):
    original_query: str
    intent: str
    table_used: str
    sql: str
    explanation: str
    data: Optional[List[dict]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None
    source: str = "bigquery"  # "bigquery" or "cube"

class CubeQueryRequest(BaseModel):
    measures: List[str]
    dimensions: Optional[List[str]] = None
    filters: Optional[List[Dict]] = None
    time_dimensions: Optional[List[Dict]] = None
    order: Optional[Dict[str, str]] = None
    limit: int = 100

class CubeQueryResponse(BaseModel):
    data: List[dict]
    row_count: int
    query: dict
    error: Optional[str] = None

# ============================================================================
# Helper Functions
# ============================================================================

def generate_sql(user_query: str) -> dict:
    """Use Gemini to translate natural language to SQL."""
    if not llm_client:
        raise Exception("LLM client not initialized")
        
    prompt = f"""
    {SYSTEM_PROMPT}
    
    User question: {user_query}
    
    Respond with a VALID JSON object only.
    Example structure:
    {{
        "intent": "analyze_something",
        "table": "fct_something",
        "sql": "SELECT ...",
        "explanation": "..."
    }}
    
    IMPORTANT: Provide the FULL SQL query. Do not truncate.
    """
    
    try:
        response = llm_client.generate_content(
            prompt,
            generation_config=GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048
            )
        )
        
        result_text = response.text.strip()
        
        if "{" in result_text and "}" in result_text:
            start_index = result_text.find("{")
            end_index = result_text.rfind("}") + 1
            result_text = result_text[start_index:end_index]
        
        try:
            return json.loads(result_text)
        except json.JSONDecodeError as je:
            logger.error(f"JSON Parse Error: {je}. Raw text: {result_text}")
            return {
                "intent": "error",
                "table": "unknown",
                "sql": "",
                "explanation": f"Failed to parse LLM response: {str(je)}"
            }

    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        return {
            "intent": "error",
            "table": "unknown",
            "sql": "",
            "explanation": f"Failed to generate SQL: {str(e)}"
        }

def execute_query(sql: str) -> tuple[List[dict], int]:
    """Execute SQL against BigQuery and return results."""
    if not bq_client:
        raise Exception("BigQuery client not initialized")

    logger.info(f"Executing SQL: {sql}")
    query_job = bq_client.query(sql)
    results = query_job.result()
    rows = [dict(row) for row in results]
    return rows, len(rows)

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/")
def health_check():
    """API health check with component status."""
    cube_status = "connected" if (CUBE_AVAILABLE and check_cube_health()) else "not_available"
    return {
        "status": "ok", 
        "service": "Retail Semantic Layer API",
        "version": "2.0.0",
        "components": {
            "gemini": {
                "status": "connected" if llm_client else "not_initialized",
                "model": "gemini-2.5-flash"
            },
            "bigquery": {
                "status": "connected" if bq_client else "not_initialized",
                "dataset": BQ_DATASET
            },
            "cube": {
                "status": cube_status,
                "url": os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
            }
        }
    }

@app.get("/schema")
def get_schema():
    """Return available tables and their descriptions."""
    return {
        "tables": SCHEMA_SUMMARY
    }

# ============================================================================
# Gemini NLQ Endpoints
# ============================================================================

@app.post("/ask", response_model=NLQResponse)
def ask_question(request: NLQRequest):
    """Translate natural language to SQL and optionally execute."""
    try:
        llm_result = generate_sql(request.query)
        
        if llm_result.get("intent") == "error":
             return NLQResponse(
                original_query=request.query,
                intent="error",
                table_used="",
                sql="",
                explanation=llm_result.get("explanation"),
                error="LLM Generation Failed",
                source="gemini"
            )

        response = NLQResponse(
            original_query=request.query,
            intent=llm_result.get("intent", ""),
            table_used=llm_result.get("table", ""),
            sql=llm_result.get("sql", ""),
            explanation=llm_result.get("explanation", ""),
            source="bigquery"
        )
        
        if request.execute and response.sql and "SELECT" in response.sql.upper():
            try:
                data, count = execute_query(response.sql)
                response.data = data[:100]
                response.row_count = count
            except Exception as e:
                response.error = f"Query execution failed: {str(e)}"
                logger.error(f"BigQuery error: {e}")
                logger.error(f"Failed SQL: {response.sql}")
        
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM response")
    except Exception as e:
        logger.error(f"NLQ processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sql-only")
def get_sql_only(request: NLQRequest):
    """Generate SQL without executing - useful for review."""
    request.execute = False
    return ask_question(request)

# ============================================================================
# Cube Endpoints
# ============================================================================

@app.get("/cube/health")
def cube_health():
    """Check Cube server health."""
    if not CUBE_AVAILABLE:
        return {"status": "unavailable", "message": "Cube client not installed"}
    
    healthy = check_cube_health()
    return {
        "status": "healthy" if healthy else "unhealthy",
        "url": os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
    }

@app.get("/cube/meta")
def cube_meta():
    """Get Cube metadata (available cubes, measures, dimensions)."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    meta = get_cube_meta()
    if meta is None:
        raise HTTPException(status_code=503, detail="Failed to connect to Cube server")
    return meta

@app.post("/cube/query", response_model=CubeQueryResponse)
def cube_query(request: CubeQueryRequest):
    """Execute a raw Cube query."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = query_cube(
        measures=request.measures,
        dimensions=request.dimensions,
        filters=request.filters,
        time_dimensions=request.time_dimensions,
        order=request.order,
        limit=request.limit
    )
    
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    
    return CubeQueryResponse(
        data=result.get("data", []),
        row_count=len(result.get("data", [])),
        query=result.get("query", {}),
        error=result.get("error")
    )

# Pre-built Cube metric endpoints
@app.get("/cube/metrics/revenue/daily")
def cube_daily_revenue(days: int = 30):
    """Get daily revenue metrics from Cube."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = get_total_revenue_by_date(days)
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    return result

@app.get("/cube/metrics/revenue/by-country")
def cube_revenue_by_country():
    """Get revenue by country from Cube."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = get_revenue_by_country()
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    return result

@app.get("/cube/metrics/orders")
def cube_order_metrics():
    """Get high-level order metrics from Cube."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = get_order_metrics()
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    return result

@app.get("/cube/metrics/orders/by-status")
def cube_orders_by_status():
    """Get orders grouped by status from Cube."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = get_orders_by_status()
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    return result

@app.get("/cube/metrics/users")
def cube_user_metrics():
    """Get user metrics from Cube."""
    if not CUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cube client not available")
    
    result = get_user_metrics()
    if result is None:
        raise HTTPException(status_code=503, detail="Cube query failed")
    return result
