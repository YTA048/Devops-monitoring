"""
Authentification basique via JWT.
SECRET à fournir via variable d'environnement JWT_SECRET en production.
"""
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod-please-32-chars-min")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Démo : utilisateurs en dur (à remplacer par une vraie BDD en prod)
FAKE_USERS = {
    "admin": {
        "username": "admin",
        # password = "admin123" (à changer en prod)
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
    },
}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = FAKE_USERS.get(payload.username)
    if not user or not pwd_context.verify(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return TokenResponse(access_token=token, expires_in=JWT_EXPIRE_MINUTES * 60)


@router.get("/verify")
def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "user": payload.get("sub"), "role": payload.get("role")}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token invalide : {exc}") from exc
