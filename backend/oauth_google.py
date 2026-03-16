import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .models import get_user, create_user, create_session, set_verified
import secrets

router = APIRouter(prefix="/auth/oauth/google", tags=["oauth"])

GOOGLE_CLIENT_ID = "484573911641-vepujquvvl229otcchk9k486dqgoj4bc.apps.googleusercontent.com"
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleOAuthRequest(BaseModel):
    id_token: str


@router.post("")
def google_oauth(payload: GoogleOAuthRequest):
    params = {"id_token": payload.id_token}
    google_res = requests.get(GOOGLE_TOKEN_INFO_URL, params=params)

    if google_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    data = google_res.json()

    if data.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid Google Client ID")

    email = data.get("email")
    name = data.get("name", "Google User")

    if not email:
        raise HTTPException(status_code=400, detail="Google account missing email")

    user = get_user(email)

    if not user:
        create_user(
            username=name,
            email=email,
            password_hash="google_oauth",
            dob=None,
            is_minor=False,
            parent_email=None
        )
        set_verified(email)

    token = secrets.token_hex(32)
    create_session(email, token)

    return {"message": "Google login successful", "token": token}
