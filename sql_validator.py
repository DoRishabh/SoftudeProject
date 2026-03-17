# sql_validator.py
import re

FORBIDDEN = re.compile(r'\b(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|TRUNCATE|MERGE|GRANT|REVOKE)\b', re.I)
SELECT_START = re.compile(r'^\s*SELECT\b', re.I)

def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not SELECT_START.search(sql):
        return False, "SQL must be a SELECT query."
    if FORBIDDEN.search(sql):
        return False, "Query contains forbidden DDL/DML operations."
    sql_clean = sql.strip().rstrip(';')
    # prevent multiple statements
    if ';' in sql_clean:
        return False, "Multiple SQL statements detected; only one SELECT allowed."
    # append LIMIT if missing (safe guard)
    if re.search(r'\bLIMIT\b', sql_clean, re.I) is None:
        sql_clean = sql_clean + " LIMIT 100"
    return True, sql_clean