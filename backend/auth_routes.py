import random
import secrets
from datetime import datetime, timedelta, date
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr

from .config import VERIFICATION_CODE_TTL_MINUTES, MAX_VERIFICATION_ATTEMPTS
from .models import (
    create_user,
    get_user,
    set_verified,
    save_verification_code,
    get_verification_record,
    increment_attempts,
    delete_verification_record,
    calculate_age,
    create_session,
    get_user_by_session,
)
from .email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    date_of_birth: date
    parent_email: Optional[EmailStr] = None


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str


class SendCodeRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def generate_verification_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


@router.post("/signup")
def signup(payload: SignUpRequest):
    if get_user(payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    age = calculate_age(payload.date_of_birth)
    is_minor = age < 13
    if is_minor and not payload.parent_email:
        raise HTTPException(status_code=400, detail="Parent email required for users under 13")
    password_hash = hash_password(payload.password)
    create_user(payload.username, payload.email, password_hash, payload.date_of_birth, is_minor, payload.parent_email)
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_TTL_MINUTES)
    save_verification_code(payload.email, code, expires_at)
    target_email = payload.parent_email if is_minor else payload.email
    send_verification_email(target_email, code)
    return {"message": "Signup successful. Verification code sent.", "is_minor": is_minor}


@router.post("/send-code")
def resend_code(payload: SendCodeRequest):
    user = get_user(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_TTL_MINUTES)
    save_verification_code(payload.email, code, expires_at)
    target_email = user["parent_email"] if user["is_minor"] else user["email"]
    send_verification_email(target_email, code)
    return {"message": "Verification code resent."}


@router.post("/verify-code")
def verify_code(payload: VerifyCodeRequest):
    user = get_user(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    record = get_verification_record(payload.email)
    if not record:
        raise HTTPException(status_code=400, detail="No verification code found. Request a new one.")
    if record["attempts"] >= MAX_VERIFICATION_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")
    if datetime.utcnow() > record["expires_at"]:
        raise HTTPException(status_code=400, detail="Verification code expired. Request a new one.")
    if payload.code != record["code"]:
        increment_attempts(payload.email)
        raise HTTPException(status_code=400, detail="Incorrect verification code.")
    set_verified(payload.email)
    delete_verification_record(payload.email)
    token = secrets.token_hex(32)
    create_session(payload.email, token)
    return {"message": "Verification successful.", "token": token}


@router.post("/login")
def login(payload: LoginRequest):
    user = get_user(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user["is_verified"]:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = secrets.token_hex(32)
    create_session(payload.email, token)
    return {"message": "Login successful.", "token": token}


@router.get("/me")
def me(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    user = get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return {
        "username": user["username"],
        "email": user["email"],
        "dob": str(user["dob"]),
        "is_minor": user["is_minor"],
        "is_verified": user["is_verified"],
    }
