import os
import time
import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

def get_pbi_token():
    tenant_id     = os.getenv("AZURE_TENANT_ID")
    client_id     = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    username      = os.getenv("PBI_USERNAME")
    password      = os.getenv("PBI_PASSWORD")

    url  = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type":    "password",
        "client_id":     client_id,
        "client_secret": client_secret,
        "username":      username,
        "password":      password,
        "scope":         "https://analysis.windows.net/powerbi/api/.default"
    }
    response = requests.post(url, data=data)
    print(f"Token response: {response.status_code}")
    token = response.json().get("access_token")
    print(f"Token fetch: {'OK' if token else 'FAILED - ' + str(response.json())}")
    return token

def clear_pbi_rows():
    token = get_pbi_token()
    if not token:
        print("Skipping clear — no token")
        return
    dataset_id = os.getenv("PBI_DATASET_ID")
    url        = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables/RealTimeData/rows"
    headers    = {"Authorization": f"Bearer {token}"}
    resp       = requests.delete(url, headers=headers, timeout=10)
    print(f"PBI clear: {resp.status_code} {resp.text[:200]}")
    time.sleep(3)

def push_pbi_rows(rows: list):
    token = get_pbi_token()
    if not token:
        print("Skipping push — no token")
        return
    dataset_id = os.getenv("PBI_DATASET_ID")
    url        = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables/RealTimeData/rows"
    headers    = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body       = {"rows": rows}
    resp       = requests.post(url, headers=headers, json=body, timeout=10)
    print(f"PBI push: {resp.status_code} {resp.text[:200]}")

@app.get("/pbi-embed-token")
def pbi_embed_token():
    try:
        from pbi_auth import get_pbi_token
        access_token = get_pbi_token()
        if not access_token:
            return {"error": "No access token"}
        
        report_id  = "f4644695-c79c-484d-9c3f-dfe66ddf8c7e"
        group_id   = "me"
        url        = f"https://api.powerbi.com/v1.0/myorg/reports/{report_id}/GenerateToken"
        headers    = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        body       = {"accessLevel": "view"}
        resp       = requests.post(url, headers=headers, json=body)
        print(f"Embed token: {resp.status_code} {resp.text[:200]}")
        data       = resp.json()
        return {
            "token":     data.get("token"),
            "report_id": report_id,
            "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={report_id}"
        }
    except Exception as e:
        return {"error": str(e)}
