# AdventureWorks AI Q&A Tool

A full-stack AI-powered analytics dashboard where you type a business 
question in plain English, the AI reads the AdventureWorks database schema, 
generates Snowflake SQL using Groq (LLaMA 3.3), executes it live, and 
returns the answer as an interactive Power BI-style dashboard with 
multiple charts, KPI cards, and data tables.

# Project Link
https://softudeproject.onrender.com/

## Stack
- Groq (LLaMA 3.3) — natural language to SQL
- Snowflake — data warehouse
- FastAPI — REST API backend
- HTML + Chart.js — frontend UI

## How to Run

1. Clone the repo and activate your virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Create a .env file with your credentials (see .env.example)
4. Start the server:
   uvicorn api:app --reload
5. Open index.html in your browser

## Project Structure
- yml_parser.py       — reads adventure_works.yml schema
- nl2sql_agent.py     — sends question + schema to Groq, returns SQL
- snowflake_executor.py — runs SQL on Snowflake, returns results
- api.py              — FastAPI endpoint that connects all components
- index.html          — browser UI with Chart.js visualisation

## Sample Questions
- Top 10 products by total sales amount
- Total sales by territory region
- Top 10 customers by total sales amount
- Sales by product category

## Notes
- Never commit .env to Git as it contains your API keys and credentials
- The app reads adventure_works.yml on every request, so adding a new
  table to the YML and restarting the server is all that is needed

## .env Example
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile

SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ADVENTUREWORKS
SNOWFLAKE_SCHEMA=SALES
