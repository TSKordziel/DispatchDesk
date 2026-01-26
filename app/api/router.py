from fastapi import APIRouter
from app.api.routes import auth, tickets, comments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(comments.router, prefix="/tickets", tags=["comments"])
