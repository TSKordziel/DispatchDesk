from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.api.router import api_router
#from app.api.auth import router as auth_router
#from app.api.tickets import router as tickets_router

app = FastAPI(title="DispatchDesk API", version="0.1.0")

app.include_router(api_router)

#app.include_router(auth_router)
#app.include_router(tickets_router)

@app.get("/")
def root():
    return {
        "name": "DispatchDesk API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "ok", "db": "down", "detail": str(e)}
