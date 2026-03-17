from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yml_parser import load_schema
from nl2sql_agent import generate_sql
from snowflake_executor import run_query

app = FastAPI(title="AI Q&A Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def query(req: QueryRequest):
    try:
        schema = load_schema()
        sql = generate_sql(req.question, schema)
        data = run_query(sql)

        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"], "sql": sql}

        columns = list(data[0].keys()) if data else []
        return {"sql": sql, "columns": columns, "data": data}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)