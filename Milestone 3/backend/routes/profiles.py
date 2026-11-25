"""A student or mentor looking after their own profile (US-S02, US-M02, US-M01 availability).
Only the owner can reach these routes: the profile is always the logged-in user's own."""
from flask import Blueprint, g, jsonify, request

from auth_utils import role_required
from constants import DURATIONS, FORMATS, TOPICS, WEEKDAYS
from models import MentorProfile, StudentProfile
from services.matching import has_open_match
from services.notifications import notify_admins
from database import db
from responses import error, json_body
from services import profiles as profile_service
from services.readiness import readiness

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


@bp.get("/students/me/readiness")
@role_required("student")
def my_readiness():
    """A checklist of what is filled in on the student's profile, and whether the profile is ready for a match."""
    return jsonify(readiness(my_student()))


@bp.post("/students/me/mentor-request")
@role_required("student")
def request_mentor():
    """The student asks for a mentor: they are marked as looking and the admins are told (US-S03)."""
    profile = my_student()
    if has_open_match(profile.id):
        return error("You already have a mentor match.", 409)
    if not profile.career_goals or not profile.topics:
        return error("Fill in your career goals and topics before asking for a mentor.", 409)
    profile.looking_for_mentor = True
    notify_admins(f"{g.user.full_name} asked for a mentor.")
    db.session.commit()
    return jsonify({"profile": profile.to_dict()})


@bp.delete("/students/me/mentor-request")
@role_required("student")
def pause_mentor_request():
    """The student does not need a mentor now: the admin will not propose one."""
    profile = my_student()
    if has_open_match(profile.id):
        return error("You have an open match. Ask the admin to cancel it first.", 409)
    profile.looking_for_mentor = False
    db.session.commit()
    return jsonify({"profile": profile.to_dict()})


@bp.get("/mentors/me")
@role_required("mentor")
def get_mentor_profile():
    return jsonify({"profile": my_mentor().to_dict()})


@bp.put("/mentors/me")
@role_required("mentor")
def update_mentor_profile():
    profile = my_mentor()
    was_complete = profile.profile_complete
    problem = profile_service.save_mentor_profile(profile, json_body())
    if problem:
        return error(problem, 400)
    profile_service.tell_admins_if_complete(profile, was_complete)
    return jsonify({"profile": profile.to_dict()})


@bp.post("/mentors/me/availability")
@role_required("mentor")
def add_my_slot():
    mentor = my_mentor()
    was_complete = mentor.profile_complete
    slot, problem = profile_service.add_slot(mentor, json_body())
    if problem:
        return error(problem, 400)
    profile_service.tell_admins_if_complete(mentor, was_complete)
    return jsonify({"slot": slot.to_dict()}), 201


@bp.delete("/mentors/me/availability/<int:slot_id>")
@role_required("mentor")
def remove_my_slot(slot_id):
    if not profile_service.remove_slot(my_mentor(), slot_id):
        return error("Slot not found.", 404)
    return "", 204
