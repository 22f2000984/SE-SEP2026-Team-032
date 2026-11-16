"""The admin (client) dashboard: overview, search of both profile types, and editing mentors
(US-C01, US-C05, US-C06). Every route here is for admins only; students and mentors get 403."""
from flask import Blueprint, jsonify, request

import validators
from auth_utils import role_required
from constants import MATCH_STATUSES
from database import db
from models import Match, MentorProfile, StudentProfile
from responses import error, json_body
from services import profiles as profile_service
from services.matching import waiting_students

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def contains(text, search):
    return search.lower() in (text or "").lower()


@bp.get("/overview")
@role_required("admin")
def overview():
    """Numbers for the dashboard: people, matches by status, and what is waiting."""
    mentors = MentorProfile.query.all()
    return jsonify({
        "students": StudentProfile.query.count(),
        "mentors": {"total": len(mentors), "verified": sum(m.profile_status == "verified" for m in mentors),
                    "pending": sum(m.profile_status == "pending" for m in mentors)},
        "matches": {status: Match.query.filter_by(status=status).count() for status in MATCH_STATUSES},
        "students_waiting_for_match": len(waiting_students()),
    })


@bp.get("/students")
@role_required("admin")
def list_students():
    """Optional filters: ?search=name or skills, ?topic=Data Science, ?programme_level=Diploma"""
    students = StudentProfile.query.all()
    search, topic, level = request.args.get("search"), request.args.get("topic"), request.args.get("programme_level")
    if search:
        students = [s for s in students if contains(s.user.full_name, search) or contains(s.skills, search)]
    if topic:
        students = [s for s in students if topic in [t.name for t in s.topics]]
    if level:
        students = [s for s in students if s.programme_level == level]
    return jsonify({"students": [s.to_dict() for s in students]})


@bp.get("/students/<int:student_id>")
@role_required("admin")
def get_student(student_id):
    student = db.session.get(StudentProfile, student_id)
    if student is None:
        return error("Student not found.", 404)
    return jsonify({"profile": student.to_dict()})


@bp.get("/mentors")
@role_required("admin")
def list_mentors():
    """Optional filters: ?status=pending|verified, ?topic=Data Science, ?search=name or skills"""
    mentors = MentorProfile.query.all()
    status, topic, search = request.args.get("status"), request.args.get("topic"), request.args.get("search")
    if status:
        mentors = [m for m in mentors if m.profile_status == status]
    if topic:
        mentors = [m for m in mentors if topic in [t.name for t in m.topics]]
    if search:
        mentors = [m for m in mentors if contains(m.user.full_name, search) or contains(m.skills_text, search)]
    return jsonify({"mentors": [m.to_dict() for m in mentors]})


@bp.get("/mentors/<int:mentor_id>")
@role_required("admin")
def get_mentor(mentor_id):
    mentor = db.session.get(MentorProfile, mentor_id)
    if mentor is None:
        return error("Mentor not found.", 404)
    return jsonify({"profile": mentor.to_dict()})


@bp.put("/mentors/<int:mentor_id>")
@role_required("admin")
def update_mentor(mentor_id):
    """The admin edits a mentor's expertise, skills, experience and capacity (US-C05)."""
    mentor = db.session.get(MentorProfile, mentor_id)
    if mentor is None:
        return error("Mentor not found.", 404)
    problem = profile_service.save_mentor_profile(mentor, json_body())
    if problem:
        return error(problem, 400)
    return jsonify({"profile": mentor.to_dict()})


@bp.patch("/mentors/<int:mentor_id>/status")
@role_required("admin")
def set_mentor_status(mentor_id):
    """Verify a mentor (or put them back to pending)."""
    mentor = db.session.get(MentorProfile, mentor_id)
    if mentor is None:
        return error("Mentor not found.", 404)
    status = (json_body()).get("status")
    problem = validators.check_mentor_status(status)
    if problem:
        return error(problem, 400)
    mentor.profile_status = status
    db.session.commit()
    return jsonify({"profile": mentor.to_dict()})


@bp.post("/mentors/<int:mentor_id>/availability")
@role_required("admin")
def add_mentor_slot(mentor_id):
    mentor = db.session.get(MentorProfile, mentor_id)
    if mentor is None:
        return error("Mentor not found.", 404)
    slot, problem = profile_service.add_slot(mentor, json_body())
    if problem:
        return error(problem, 400)
    return jsonify({"slot": slot.to_dict()}), 201


@bp.delete("/mentors/<int:mentor_id>/availability/<int:slot_id>")
@role_required("admin")
def remove_mentor_slot(mentor_id, slot_id):
    mentor = db.session.get(MentorProfile, mentor_id)
    if mentor is None or not profile_service.remove_slot(mentor, slot_id):
        return error("Slot not found.", 404)
    return "", 204
