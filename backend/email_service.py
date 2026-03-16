import smtplib
from email.mime.text import MIMEText
from .config import SENDER_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, VERIFICATION_CODE_TTL_MINUTES


def send_verification_email(to_email: str, code: str):
    subject = "Your ScriptBox Verification Code"
    body = f"Your ScriptBox verification code is: {code}\n\nThis code expires in {VERIFICATION_CODE_TTL_MINUTES} minutes."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        if SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
