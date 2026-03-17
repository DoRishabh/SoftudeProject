import os
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def run_query(sql: str):
    conn = None
    try:
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        df = pd.DataFrame(
            cursor.fetchall(),
            columns=[d[0] for d in cursor.description]
        )
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

# Quick test
if __name__ == "__main__":
    rows = run_query("SELECT CURRENT_DATE()")
    print(rows)