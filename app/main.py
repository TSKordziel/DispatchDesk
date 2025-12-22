import os
from fastapi import FastAPI
import psycopg

app = FastAPI(title="DispatchDesk API", version="0.1.0")

@app.get("/")
def root():
    return {
        "name": "DispatchDesk API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return {"status": "ok", "db": "down", "detail": "DATABASE_URL not set"}
    
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "ok", "db": "down", "detail": str(e)}
