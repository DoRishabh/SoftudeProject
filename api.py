import os
import time
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

app = FastAPI(title="AI Q&A Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PBI_BASE_URL = "https://api.powerbi.com/beta/2b0a3b04-16bd-4638-be57-5622527eb55e/datasets/c893e7ae-aaff-41fe-a228-b81f15172acc/rows"
PBI_PUSH_URL = "https://api.powerbi.com/beta/2b0a3b04-16bd-4638-be57-5622527eb55e/datasets/c893e7ae-aaff-41fe-a228-b81f15172acc/rows?experience=power-bi&key=3rcynk%2FYYoVmiC807RBINRp9cTWEttGcreseey81otkMLH1UDbvJV5EpRbcIqbjsZ%2BwMoU8nsqwAtH0R9qJwTQ%3D%3D"
PBI_KEY = "3rcynk/YYoVmiC807RBINRp9cTWEttGcreseey81otkMLH1UDbvJV5EpRbcIqbjsZ+wMoU8nsqwAtH0R9qJwTQ=="

@app.get("/")
def serve_home():
    return FileResponse("index.html")

class QueryRequest(BaseModel):
    question: str

def push_to_powerbi(data: list, columns: list):
    try:
        if not data or len(columns) < 2:
            return
        headers = {"Authorization": f"PBIKey {PBI_KEY}"}
        del_resp = requests.delete(PBI_BASE_URL, headers=headers, timeout=5)
        print(f"PBI delete: {del_resp.status_code} {del_resp.text}")
        now = int(time.time())
        rows = [
            {
                "label": str(row[columns[0]]),
                "value": float(row[columns[1]]) if row[columns[1]] is not None else 0,
                "querytime": now
            }
            for row in data[:10]
        ]
        response = requests.post(PBI_PUSH_URL, json=rows, timeout=5)
        print(f"PBI push: {response.status_code}")
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
