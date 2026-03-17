import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_sql(question: str, schema: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a Snowflake SQL expert.

Database schema:
{schema}

Rules you MUST follow:
- Use ONLY tables and columns listed in the schema above
- Use fully qualified names for FROM and JOIN clauses: DATABASE.SCHEMA.TABLE
- Always use short table aliases (e.g. soh, sod, p, c, st) and use ONLY the alias to reference columns
- Example: FROM ADVENTUREWORKS.SALES.CUSTOMER c JOIN ADVENTUREWORKS.SALES.SALES_ORDER_HEADER soh ON c.CUSTOMER_ID = soh.CUSTOMER_ID
- If the question specifies a number (e.g. "top 10", "top 5"), use that number as the LIMIT
- If no number is specified, use LIMIT 20 as default
- Never exceed LIMIT 100
- Return ONLY the raw SQL query
- No markdown, no backticks, no explanation, no preamble
- If the question cannot be answered from the schema, return exactly this SQL and nothing else:
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