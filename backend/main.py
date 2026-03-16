from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, date
import random
import smtplib
from email.mime.text import MIMEText
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
users = {}             
verification_codes = {}  

VERIFICATION_CODE_TTL_MINUTES = 10
MAX_VERIFICATION_ATTEMPTS = 5
SENDER_EMAIL = "modbox.noreply@gmail.com"

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

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def generate_verification_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def send_verification_email(to_email: str, code: str):
    subject = "Your ScriptBox Verification Code"
    body = f"Your ScriptBox verification code is: {code}\n\nThis code expires in {VERIFICATION_CODE_TTL_MINUTES} minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            print(f"[DEBUG] Would send email to {to_email} with code {code}")
    except Exception as e:
        print(f"[ERROR] Email send failed: {e}")

def create_or_update_verification(email: str):
    code = generate_verification_code()
    verification_codes[email] = {
        "code": code,
        "expires_at": datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_TTL_MINUTES),
        "attempts": 0,
    }
    return code

@app.post("/auth/signup")
def signup(payload: SignUpRequest):
    if payload.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")

    age = calculate_age(payload.date_of_birth)
    is_minor = age < 13

    if is_minor and not payload.parent_email:
        raise HTTPException(status_code=400, detail="Parent email required for users under 13")

    user = {
        "username": payload.username,
        "email": payload.email,
        "password_hash": payload.password,  
        "dob": payload.date_of_birth,
        "is_minor": is_minor,
        "parent_email": payload.parent_email,
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }
    users[payload.email] = user

    code = create_or_update_verification(payload.email)

    target_email = payload.parent_email if is_minor else payload.email
    send_verification_email(target_email, code)

    return {"message": "Signup successful. Verification code sent.", "is_minor": is_minor}

@app.post("/auth/send-code")
def resend_code(payload: SendCodeRequest):
    if payload.email not in users:
        raise HTTPException(status_code=404, detail="User not found")

    user = users[payload.email]
    code = create_or_update_verification(payload.email)

    target_email = user["parent_email"] if user["is_minor"] else user["email"]
    send_verification_email(target_email, code)

    return {"message": "Verification code resent."}

@app.post("/auth/verify-code")
def verify_code(payload: VerifyCodeRequest):
    if payload.email not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email not in verification_codes:
        raise HTTPException(status_code=400, detail="No verification code found. Request a new one.")

    record = verification_codes[payload.email]

    if record["attempts"] >= MAX_VERIFICATION_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")

    if datetime.utcnow() > record["expires_at"]:
        raise HTTPException(status_code=400, detail="Verification code expired. Request a new one.")

    if payload.code != record["code"]:
        record["attempts"] += 1
        raise HTTPException(status_code=400, detail="Incorrect verification code.")

    users[payload.email]["is_verified"] = True
    del verification_codes[payload.email]

    return {"message": "Verification successful."}
