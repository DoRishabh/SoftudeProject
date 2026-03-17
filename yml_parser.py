import yaml
import os
from dotenv import load_dotenv
load_dotenv()

def load_schema(yml_path=None):
    if yml_path is None:
        yml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adventure_works.yml")
    
    with open(yml_path, "r") as f:
        schema = yaml.safe_load(f)
    
    lines = []
    for table in schema["tables"]:
        cols = ", ".join([c["name"] for c in table["columns"]])
        
        rels = ""
        if "relationships" in table and table["relationships"]:
            rel_parts = []
            for r in table["relationships"]:
                join_table = r.get("join") or r.get("JOIN", "")
                join_key   = r.get("on")   or r.get("ON", "")
                if join_table and join_key:
                    rel_parts.append(f"{join_table} on {join_key}")
            if rel_parts:
                rels = " | Joins: " + ", ".join(rel_parts)
        
        lines.append(
            f"Table: {table['database']}.{table['schema']}.{table['name']} "
            f"| Columns: {cols}{rels}"
        )
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(load_schema())