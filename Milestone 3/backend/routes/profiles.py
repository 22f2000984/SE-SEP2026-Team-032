"""A student or mentor looking after their own profile (US-S02, US-M02, US-M01 availability).
Only the owner can reach these routes: the profile is always the logged-in user's own."""
from flask import Blueprint, g, jsonify, request

from auth_utils import role_required
from constants import DURATIONS, FORMATS, TOPICS, WEEKDAYS
from models import MentorProfile, StudentProfile
from responses import error, json_body
from services import profiles as profile_service

bp = Blueprint("profiles", __name__, url_prefix="/api")


def my_student():
    return StudentProfile.query.filter_by(user_id=g.user.id).first()


def my_mentor():
    return MentorProfile.query.filter_by(user_id=g.user.id).first()


@bp.get("/options")
def options():
    """The fixed lists the profile forms use."""
    return jsonify({"topics": TOPICS, "formats": FORMATS, "durations": DURATIONS, "weekdays": WEEKDAYS})


@bp.get("/students/me")
@role_required("student")
def get_student_profile():
    return jsonify({"profile": my_student().to_dict()})


@bp.put("/students/me")
@role_required("student")
def update_student_profile():
    profile = my_student()
    problem = profile_service.save_student_profile(profile, json_body())
    if problem:
        return error(problem, 400)
    return jsonify({"profile": profile.to_dict()})


@bp.get("/mentors/me")
@role_required("mentor")
def get_mentor_profile():
    return jsonify({"profile": my_mentor().to_dict()})


@bp.put("/mentors/me")
@role_required("mentor")
def update_mentor_profile():
    profile = my_mentor()
    problem = profile_service.save_mentor_profile(profile, json_body())
    if problem:
        return error(problem, 400)
    return jsonify({"profile": profile.to_dict()})


@bp.post("/mentors/me/availability")
@role_required("mentor")
def add_my_slot():
    slot, problem = profile_service.add_slot(my_mentor(), json_body())
    if problem:
        return error(problem, 400)
    return jsonify({"slot": slot.to_dict()}), 201


@bp.delete("/mentors/me/availability/<int:slot_id>")
@role_required("mentor")
def remove_my_slot(slot_id):
    if not profile_service.remove_slot(my_mentor(), slot_id):
        return error("Slot not found.", 404)
    return "", 204
