from datetime import datetime, date

users = {}
verification_codes = {}
sessions = {}


def create_user(username, email, password_hash, dob, is_minor, parent_email):
    users[email] = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "dob": dob,
        "is_minor": is_minor,
        "parent_email": parent_email,
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }


def get_user(email):
    return users.get(email)


def set_verified(email):
    if email in users:
        users[email]["is_verified"] = True


def save_verification_code(email, code, expires_at):
    verification_codes[email] = {
        "code": code,
        "expires_at": expires_at,
        "attempts": 0,
    }


def get_verification_record(email):
    return verification_codes.get(email)


def increment_attempts(email):
    if email in verification_codes:
        verification_codes[email]["attempts"] += 1


def delete_verification_record(email):
    if email in verification_codes:
        del verification_codes[email]


def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def create_session(email: str, token: str):
    sessions[token] = {
        "email": email,
        "created_at": datetime.utcnow(),
    }


def get_user_by_session(token: str):
    session = sessions.get(token)
    if not session:
        return None
    return get_user(session["email"])
