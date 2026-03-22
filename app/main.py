import os
import time
import uuid

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.bootstrap import ensure_bootstrap_admin
from app.core.errors import build_error, STATUS_CODE_TO_ERROR_CODE
from app.core.logging import setup_logging

from app.db.session import SessionLocal

from app.api.router import api_router
#from app.api.auth import router as auth_router
#from app.api.tickets import router as tickets_router

logger = setup_logging()

app = FastAPI(title="DispatchDesk API", version="0.1.0")

app.include_router(api_router)

#app.include_router(auth_router)
#app.include_router(tickets_router)

@app.on_event("startup")
def bootstrap():
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if not email or not password:
        return
    db = SessionLocal()
    try:
        ensure_bootstrap_admin(db, email, password)
    finally:
        db.close()

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        client_host = request.client.host if request.client else "unknown"
        logger.exception(
            "request_failed method=%s path=%s duration_ms=%.2f request_id=%s client=%s",
            request.method,
            request.url.path,
            duration_ms,
            request_id,
            client_host,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    client_host = request.client.host if request.client else "unknown"
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%.2f request_id=%s client=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
        client_host,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code") or STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, "error")
        message = detail.get("message") or detail.get("detail") or "Error"
        details = detail.get("details")
    else:
        code = STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, "error")
        message = detail or "Error"
        details = None

    payload = build_error(code=code, message=message, details=details, request_id=request_id)
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    payload = build_error(
        code="validation_error",
        message="Validation error",
        details=exc.errors(),
        request_id=request_id,
    )
    return JSONResponse(status_code=422, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_exception request_id=%s", request_id)
    payload = build_error(
        code="internal_error",
        message="Internal server error",
        details=None,
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=payload)


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
