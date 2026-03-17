import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_sql(question: str, schema: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a Snowflake SQL expert. Generate a valid Snowflake SQL query.

Database schema:
{schema}

STRICT RULES:
1. Use fully qualified names in FROM and JOIN: DATABASE.SCHEMA.TABLE
2. Always define a short alias for every table and use ONLY the alias for columns
3. CUSTOMER joins directly to SALES_ORDER_DETAIL on CUSTOMERKEY — NEVER through SALES_ORDER_HEADER
4. SALES_ORDER_HEADER only has these 4 columns: SALESORDERLINEKEY, SALES_ORDER_ID, SALES_ORDER_LINE, CHANNEL — nothing else
5. CORRECT customer query example:
   SELECT c.CUSTOMER_NAME, SUM(sod.SALES_AMOUNT) AS TOTAL_SALES
   FROM ADVENTUREWORKS.SALES.SALES_ORDER_DETAIL sod
   JOIN ADVENTUREWORKS.SALES.CUSTOMER c ON sod.CUSTOMERKEY = c.CUSTOMERKEY
   GROUP BY c.CUSTOMER_NAME
   ORDER BY TOTAL_SALES DESC
   LIMIT 10
6. CORRECT product query example:
   SELECT p.PRODUCT_NAME, SUM(sod.SALES_AMOUNT) AS TOTAL_SALES
   FROM ADVENTUREWORKS.SALES.SALES_ORDER_DETAIL sod
   JOIN ADVENTUREWORKS.PRODUCTION.PRODUCT p ON sod.PRODUCTKEY = p.PRODUCTKEY
   GROUP BY p.PRODUCT_NAME
   ORDER BY TOTAL_SALES DESC
   LIMIT 10
7. CORRECT territory query example:
   SELECT st.REGION, SUM(sod.SALES_AMOUNT) AS TOTAL_SALES
   FROM ADVENTUREWORKS.SALES.SALES_ORDER_DETAIL sod
   JOIN ADVENTUREWORKS.SALES.SALES_TERRITORY st ON sod.SALESTERRITORYKEY = st.SALESTERRITORYKEY
   GROUP BY st.REGION
   ORDER BY TOTAL_SALES DESC
   LIMIT 10
8. Always use LIMIT 100 regardless of what the question says — the frontend handles slicing
9. When joining CUSTOMER always add: WHERE c.CUSTOMER_NAME IS NOT NULL AND sod.CUSTOMERKEY > 0
10. If the question cannot be answered from the schema return exactly:
    SELECT 'This question cannot be answered from the available data' AS MESSAGE

Question: {question}

SQL:"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()
    sql = re.sub(r"^```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()

    return sql

if __name__ == "__main__":
    from yml_parser import load_schema
    schema = load_schema()
    sql = generate_sql("Top 5 products by total sales amount", schema)
    print(sql)
