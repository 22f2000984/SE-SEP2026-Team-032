"""Passwords, login tokens and the role checks that protect every route (US-C06).
The check happens here on the server, so hiding a link in the frontend is never the only protection."""
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models import User
from responses import error


def hash_password(password):
    return generate_password_hash(password, method=current_app.config["PASSWORD_HASH_METHOD"])


def password_matches(user, password):
    return check_password_hash(user.password_hash, password)


def make_token(user):
    expires = datetime.utcnow() + timedelta(hours=current_app.config["TOKEN_HOURS"])
    payload = {"user_id": user.id, "role": user.role, "exp": expires}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def user_from_request():
    """Reads 'Authorization: Bearer <token>' and returns the User, or None if it is missing or not valid."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(header[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    user = db.session.get(User, payload["user_id"])
    return user if user and user.is_active else None


def login_required(view):
    """The caller must be logged in. 401 if not."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = user_from_request()
        if user is None:
            return error("Please log in first.", 401)
        g.user = user
        return view(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """The caller must be logged in and have one of the given roles. 401 if not logged in, 403 if the role is wrong."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = user_from_request()
            if user is None:
                return error("Please log in first.", 401)
            if user.role not in roles:
                return error("You are not allowed to do this.", 403)
            g.user = user
            return view(*args, **kwargs)
        return wrapper
    return decorator
