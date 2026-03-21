from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
import csv
import json
import os
from datetime import datetime
from typing import Optional

from db import init_db, execute_query, get_schema_string, SCHEMA_INFO
from model import nl_to_sql, explain_sql, validate_sql

app = FastAPI(
    title="NL2SQL API",
    description="Convert natural language queries to SQL and execute them.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nl2sql-sigma.vercel.app",
        "http://localhost:3000",
        "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory query history (use Redis/DB in production)
query_history: list[dict] = []

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized.")


class QueryRequest(BaseModel):
    natural_language: str = Field(..., min_length=3, max_length=500)
    explain: Optional[bool] = False


class QueryResponse(BaseModel):
    sql: str
    columns: list
    rows: list
    row_count: int
    explanation: Optional[str] = None
    execution_time_ms: float


@app.get("/")
def root():
    return {"status": "ok", "message": "NL2SQL API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    start_time = datetime.utcnow()

    # 1. Convert NL to SQL
    try:
        result = nl_to_sql(req.natural_language)
        sql = result["sql"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NL-to-SQL conversion failed: {str(e)}")

    # 2. Validate SQL
    is_valid, reason = validate_sql(sql)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid SQL generated: {reason}")

    # 3. Execute query
    try:
        db_result = execute_query(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")

    # 4. Optional explanation
    explanation = None
    if req.explain:
        try:
            explanation = explain_sql(sql)
        except Exception:
            explanation = "Explanation unavailable."

    exec_time = (datetime.utcnow() - start_time).total_seconds() * 1000

    # 5. Save to history
    history_entry = {
        "id": len(query_history) + 1,
        "natural_language": req.natural_language,
        "sql": sql,
        "row_count": db_result["row_count"],
        "timestamp": datetime.utcnow().isoformat(),
        "execution_time_ms": round(exec_time, 2)
    }
    query_history.insert(0, history_entry)
    if len(query_history) > 50:
        query_history.pop()

    return QueryResponse(
        sql=sql,
        columns=db_result["columns"],
        rows=db_result["rows"],
        row_count=db_result["row_count"],
        explanation=explanation,
        execution_time_ms=round(exec_time, 2)
    )


@app.get("/history")
def get_history(limit: int = 20):
    return {"history": query_history[:limit], "total": len(query_history)}


@app.delete("/history")
def clear_history():
    query_history.clear()
    return {"message": "History cleared."}


@app.get("/schema")
def get_schema():
    return {
        "tables": SCHEMA_INFO,
        "schema_string": get_schema_string()
    }


@app.post("/download-csv")
async def download_csv(req: QueryRequest):
    """Execute query and return results as CSV file."""
    result = nl_to_sql(req.natural_language)
    sql = result["sql"]

    is_valid, reason = validate_sql(sql)
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    db_result = execute_query(sql)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(db_result["columns"])
    writer.writerows(db_result["rows"])
    output.seek(0)

    filename = f"nl2sql_result_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/sample-questions")
def sample_questions():
    return {
        "questions": [
            "Show all employees with salary above 80000",
            "Which department has the highest average salary?",
            "List the top 5 students by GPA",
            "Count students per major",
            "Show total sales by region",
            "Find all employees hired after 2020",
            "Which products have less than 50 items in stock?",
            "Show me courses with more than 10 enrolled students",
            "What is the average GPA by major?",
            "List all sales made in 2024 with product names",
            "Show employees and their department names",
            "Which employee made the most sales?",
        ]
    }
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized.")
    # Add this line:
    from keep_alive import start_keep_alive
    start_keep_alive()