import os
import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yml_parser import load_schema
from nl2sql_agent import generate_sql
from snowflake_executor import run_query
from pbi_auth import clear_pbi_rows, push_pbi_rows

app = FastAPI(title="AI Q&A Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_home():
    return FileResponse("index.html")

class QueryRequest(BaseModel):
    question: str

def push_to_powerbi(data: list, columns: list):
    try:
        if not data or len(columns) < 2:
            return
        clear_pbi_rows()
        rows = [
            {
                "label": str(row[columns[0]]),
                "value": float(row[columns[1]]) if row[columns[1]] is not None else 0
            }
            for row in data[:10]
        ]
        push_pbi_rows(rows)
    except Exception as e:
        print(f"Power BI failed: {e}")

@app.post("/query")
def query(req: QueryRequest):
    try:
        schema  = load_schema()
        sql     = generate_sql(req.question, schema)
        data    = run_query(sql)
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"], "sql": sql}
        columns = list(data[0].keys()) if data else []
        push_to_powerbi(data, columns)
        return {"sql": sql, "columns": columns, "data": data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
