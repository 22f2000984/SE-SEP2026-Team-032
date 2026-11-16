"""Registration and login (US-S01, US-M01)."""
from flask import Blueprint, g, jsonify, request

import validators
from auth_utils import hash_password, login_required, make_token, password_matches
from database import db
from models import MentorProfile, StudentProfile, User
from responses import error, json_body

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = json_body()
    problem = validators.check_register(data)
    if problem:
        return error(problem, 400)
    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return error("This email is already registered.", 409)
    user = User(email=email, password_hash=hash_password(data["password"]),
                full_name=data["full_name"].strip(), role=data["role"])
    db.session.add(user)
    db.session.flush()  # gives the user an id before the profile is created
    profile = StudentProfile(user_id=user.id) if user.role == "student" else MentorProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = json_body()
    user = User.query.filter_by(email=str(data.get("email", "")).strip().lower()).first()
    if user is None or not password_matches(user, str(data.get("password", ""))):
        return error("Invalid email or password.", 401)
    if not user.is_active:
        return error("This account is switched off.", 403)
    return jsonify({"token": make_token(user), "user": user.to_dict()})


@bp.get("/me")
@login_required
def me():
    return jsonify({"user": g.user.to_dict()})
