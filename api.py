def push_to_powerbi(data: list, columns: list):
    try:
        if not data or len(columns) < 2:
            return

        # Correct DELETE format — key in header
        base_url = "https://api.powerbi.com/beta/2b0a3b04-16bd-4638-be57-5622527eb55e/datasets/c893e7ae-aaff-41fe-a228-b81f15172acc/rows"
        key = "3rcynk/YYoVmiC807RBINRp9cTWEttGcreseey81otkMLH1UDbvJV5EpRbcIqbjsZ+wMoU8nsqwAtH0R9qJwTQ=="
        headers = {"Authorization": f"PBIKey {key}"}

        # Try DELETE with key in header
        del_resp = requests.delete(base_url, headers=headers, timeout=5)
        print(f"PBI delete: {del_resp.status_code} {del_resp.text}")

        # Push new rows
        import time
        now = int(time.time())
        rows = [
            {
                "label": str(row[columns[0]]),
                "value": float(row[columns[1]]) if row[columns[1]] is not None else 0,
                "querytime": now
            }
            for row in data[:10]
        ]
        push_url = "https://api.powerbi.com/beta/2b0a3b04-16bd-4638-be57-5622527eb55e/datasets/c893e7ae-aaff-41fe-a228-b81f15172acc/rows?experience=power-bi&key=3rcynk%2FYYoVmiC807RBINRp9cTWEttGcreseey81otkMLH1UDbvJV5EpRbcIqbjsZ%2BwMoU8nsqwAtH0R9qJwTQ%3D%3D"
        response = requests.post(push_url, json=rows, timeout=5)
        print(f"PBI push: {response.status_code}")

    except Exception as e:
        print(f"Power BI failed: {e}")
```

Push to GitHub → Render redeploys → run a query → check logs for:
```
PBI delete: 200
PBI push: 200
