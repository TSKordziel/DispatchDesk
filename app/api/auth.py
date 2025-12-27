from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import hash_password, verify_password
from app.core.jwt import create_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.core.auth import get_current_user
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import TokenPair
from app.crud.user import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()

    existing = get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    pw_hash = hash_password(payload.password)
    user = create_user(db, email=email, password_hash=pw_hash)
    return user

@router.post("/login", response_model=TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username.strip().lower()  # OAuth2 form uses 'username' field
    user = get_user_by_email(db, email)

    # IMPORTANT: same error whether user exists or not
    if not user or not user.is_active or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_token(sub=str(user.id), token_type="access", expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh = create_token(sub=str(user.id), token_type="refresh", expires_minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user