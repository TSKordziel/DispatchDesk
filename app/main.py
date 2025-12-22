from fastapi import FastAPI

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
    return {"status": "ok"}
