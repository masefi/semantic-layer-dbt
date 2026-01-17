from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import os
import json
import logging
from prompts import SYSTEM_PROMPT, SCHEMA_SUMMARY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Retail Semantic Layer NLQ API")

# Initialize clients at startup
# Function to get clients lazily or at startup
def get_clients():
    project_id = os.environ.get("GCP_PROJECT_ID", "semantic-layer-484020")
    logger.info(f"Initializing Vertex AI with project: {project_id}")
    try:
        vertexai.init(project=project_id, location="us-central1")
        # Using a stable, supported version
        model_name = "gemini-2.5-flash"
        logger.info(f"Using model: {model_name}")
        llm = GenerativeModel(model_name) 
        bq = bigquery.Client(project=project_id)
        return llm, bq
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return None, None

llm_client, bq_client = None, None

@app.on_event("startup")
async def startup_event():
    global llm_client, bq_client
    llm_client, bq_client = get_clients()

BQ_DATASET = os.environ.get("BQ_DATASET", "retail_marts_dev")

# Pydantic models
class NLQRequest(BaseModel):
    query: str
    execute: bool = True  # Whether to execute the SQL and return results
    
class NLQResponse(BaseModel):
    original_query: str
    intent: str
    table_used: str
    sql: str
    explanation: str
    data: Optional[List[dict]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None

def generate_sql(user_query: str) -> dict:
    """Use Gemini to translate natural language to SQL."""
    if not llm_client:
        raise Exception("LLM client not initialized")
        
    prompt = f"""
    {SYSTEM_PROMPT}
    
    User question: {user_query}
    
    Respond with a JSON object only, no markdown formatting:
    {{
        "intent": "brief description of what user wants to know",
        "table": "primary_table_name",
        "sql": "SELECT ... FROM `semantic-layer-484020.{BQ_DATASET}.table_name` ...",
        "explanation": "brief explanation of query logic"
    }}
    """
    
    try:
        response = llm_client.generate_content(
            prompt,
            generation_config=GenerationConfig(
                temperature=0.1,  # Low temperature for consistent SQL
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )
        
        # Parse JSON from response
        result_text = response.text.strip()
        # Handle potential markdown code blocks if the model ignores the mime type hints
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        return json.loads(result_text)
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        # Fallback for demo/testing if LLM fails (e.g. auth issues locally)
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

@app.get("/")
def health_check():
    return {
        "status": "ok", 
        "service": "Retail Semantic NLQ API",
        "model": "gemini-2.5-flash",
        "dataset": BQ_DATASET,
        "clients_initialized": llm_client is not None
    }

@app.get("/schema")
def get_schema():
    """Return available tables and their descriptions."""
    return {
        "tables": SCHEMA_SUMMARY
    }

@app.post("/ask", response_model=NLQResponse)
def ask_question(request: NLQRequest):
    """Translate natural language to SQL and optionally execute."""
    try:
        # Generate SQL using Gemini
        llm_result = generate_sql(request.query)
        
        if llm_result.get("intent") == "error":
             return NLQResponse(
                original_query=request.query,
                intent="error",
                table_used="",
                sql="",
                explanation=llm_result.get("explanation"),
                error="LLM Generation Failed"
            )

        response = NLQResponse(
            original_query=request.query,
            intent=llm_result.get("intent", ""),
            table_used=llm_result.get("table", ""),
            sql=llm_result.get("sql", ""),
            explanation=llm_result.get("explanation", "")
        )
        
        # Execute if requested
        if request.execute and response.sql and "SELECT" in response.sql.upper():
            try:
                data, count = execute_query(response.sql)
                response.data = data[:100]  # Limit to 100 rows
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
