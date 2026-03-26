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

GROUP_ID    = "f19c474c-d2d1-4f91-853d-a5839a682e30"
REPORT_ID   = "771ac7b8-a37d-4028-825d-8b9f189ed0c4"  # page 1 - AI Query
REPORT_ID_2 = "4f1df241-4d62-4774-bb25-8af18d1e553f"  # page 2 - Dynamic Slicer
REPORT_ID_3 = "1123e3e7-5f3a-4499-b1ca-0c37f673f29a"  # page 3 - US Map
REPORT_ID_4 = "f109fb78-c9fd-472d-8747-040f4ffc0daa"  # page 4 - Interactive Sales
REPORT_ID_5 = "20c745e8-2d1f-455d-b05f-a25f1471a59c"  # page 5 - Year End Medals


def generate_embed_token(report_id: str, access_level: str = "View"):
    access_token = get_pbi_token()
    if not access_token:
        return {"error": "No access token"}

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    body = {"accessLevel": access_level}

    # try group workspace first
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{report_id}/GenerateToken"
    resp = requests.post(url, headers=headers, json=body)
    data = resp.json()
    token = data.get("token")
    if token:
        return {
            "token": token,
            "report_id": report_id,
            "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={GROUP_ID}"
        }

    # fallback: My Workspace
    url2 = f"https://api.powerbi.com/v1.0/myorg/reports/{report_id}/GenerateToken"
    resp2 = requests.post(url2, headers=headers, json=body)
    data2 = resp2.json()
    token2 = data2.get("token")
    if token2:
        return {
            "token": token2,
            "report_id": report_id,
            "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={report_id}"
        }

    return {"error": str(data2)}


# ── page routes ────────────────────────────────────────────────
@app.get("/")
def serve_home():
    return FileResponse("index.html")

@app.get("/slicer2")
def serve_slicer2():
    return FileResponse("slicer2.html")

@app.get("/usmap")
def serve_usmap():
    return FileResponse("usmap.html")

@app.get("/interactivesales")          # ✅ fixed — no space, correct file
def serve_interactivesales():
    return FileResponse("interactivesales.html")

@app.get("/yearendmedals")
def serve_yearendmedals():
    return FileResponse("yearendmedals.html")


# ── token routes ───────────────────────────────────────────────
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
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{REPORT_ID}/GenerateToken"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json={"accessLevel": "Edit"})
        data = resp.json()
        token = data.get("token")
        if not token:
            return {"error": str(data)}
        return {
            "token": token,
            "report_id": REPORT_ID,
            "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={REPORT_ID}&groupId={GROUP_ID}"
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/pbi-embed-token-2")
def pbi_embed_token_2():
    try:
        return generate_embed_token(REPORT_ID_2)
    except Exception as e:
        return {"error": str(e)}


@app.get("/pbi-embed-token-3")
def pbi_embed_token_3():
    try:
        return generate_embed_token(REPORT_ID_3)
    except Exception as e:
        return {"error": str(e)}


@app.get("/pbi-embed-token-4")
def pbi_embed_token_4():
    try:
        return generate_embed_token(REPORT_ID_4)
    except Exception as e:
        return {"error": str(e)}


@app.get("/pbi-embed-token-5")
def pbi_embed_token_5():
    try:
        return generate_embed_token(REPORT_ID_5)
    except Exception as e:
        return {"error": str(e)}


# ── query route ────────────────────────────────────────────────
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
            for row in data
        ]
        push_pbi_rows(rows)
    except Exception as e:
        print(f"Power BI failed: {e}")


@app.post("/query")
def query(req: QueryRequest):
    try:
        schema = load_schema()
        sql = generate_sql(req.question, schema)
        data = run_query(sql)
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
