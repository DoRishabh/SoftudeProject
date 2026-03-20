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
from pbi_auth import clear_pbi_rows, push_pbi_rows, get_pbi_token

app = FastAPI(title="AI Q&A Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORT_ID = "771ac7b8-a37d-4028-825d-8b9f189ed0c4"
GROUP_ID  = "f19c474c-d2d1-4f91-853d-a5839a682e30"

@app.get("/")
def serve_home():
    return FileResponse("index.html")

@app.get("/pbi-token")
def pbi_token():
    try:
        token = get_pbi_token()
        if not token:
            return {"error": "Failed to fetch token"}
        return {"token": token}
    except Exception as e:
        return {"error": str(e)}

@app.get("/pbi-embed-token")
def pbi_embed_token():
    try:
        access_token = get_pbi_token()
        if not access_token:
            return {"error": "No access token"}
        url     = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{REPORT_ID}/GenerateToken"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        body    = {"accessLevel": "Edit"}
        resp    = requests.post(url, headers=headers, json=body)
        print(f"Embed token: {resp.status_code} {resp.text[:200]}")
        data    = resp.json()
        token   = data.get("token")
        if not token:
            print(f"Embed token failed: {data}")
            return {"error": str(data)}
        return {
            "token":     token,
            "report_id": REPORT_ID,
            "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={REPORT_ID}&groupId={GROUP_ID}"
        }
    except Exception as e:
        return {"error": str(e)}

class QueryRequest(BaseModel):
    question: str

def push_to_powerbi(data: list, columns: list):
    try:
        if not data or len(columns) < 2:
            return
        clear_pbi_rows()
        # Push all rows — no slicing, respect query limit
        rows = [
            {
                "label": str(row[columns[0]]),
                "value": float(row[columns[1]]) if row[columns[1]] is not None else 0
            }
            for row in data
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
