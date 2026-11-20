"""Matches. US-C02: the admin sees recommended mentors for a student and proposes a match.
US-C03, US-C04: both sides answer, then the admin confirms, cancels or completes it."""
from flask import Blueprint, g, jsonify, request

import validators
from auth_utils import login_required, role_required
from constants import MATCH_STATUSES
from database import db
from models import Match, MatchStatusLog, MentorProfile, Notification, StudentProfile
from responses import error, json_body
from services.match_flow import change_status, record_answer
from services.matching import eligibility_error, recommend, score_pair
from services.notifications import notify

bp = Blueprint("matches", __name__, url_prefix="/api")


@bp.get("/admin/students/<int:student_id>/recommendations")
@role_required("admin")
def recommendations(student_id):
    """The best mentors for one student. ?limit=3 by default."""
    student = db.session.get(StudentProfile, student_id)
    if student is None:
        return error("Student not found.", 404)
    limit = request.args.get("limit", default=3, type=int)
    if limit < 1:
        return error("limit must be 1 or more.", 400)
    return jsonify({"student_id": student_id, "recommendations": recommend(student, limit)})


@bp.post("/admin/matches")
@role_required("admin")
def propose_match():
    data = json_body()
    student_id, mentor_id = data.get("student_id"), data.get("mentor_id")
    if not isinstance(student_id, int) or not isinstance(mentor_id, int):
        return error("student_id and mentor_id are required whole numbers.", 400)
    student = db.session.get(StudentProfile, student_id)
    mentor = db.session.get(MentorProfile, mentor_id)
    if student is None or mentor is None:
        return error("Student or mentor not found.", 404)
    problem = eligibility_error(student, mentor)
    if problem:
        return error(problem, 409)

    score = score_pair(student, mentor)
    match = Match(student_id=student.id, mentor_id=mentor.id, proposed_by=g.user.id, status="proposed",
                  match_score=score["total"], score_reasons="; ".join(score["reasons"]),
                  notes=str(data.get("notes") or "").strip())
    db.session.add(match)
    db.session.flush()
    db.session.add(MatchStatusLog(match_id=match.id, old_status=None, new_status="proposed", changed_by=g.user.id))
    notify(mentor.user_id, "A new student match is waiting for your response.", match.id)
    notify(student.user_id, "A mentor has been proposed for you. Please accept or decline.", match.id)
    db.session.commit()
    return jsonify({"match": match.to_dict()}), 201


@bp.get("/admin/matches")
@role_required("admin")
def list_matches():
    """All matches, newest first. Optional filter: ?status=proposed"""
    status = request.args.get("status")
    if status and status not in MATCH_STATUSES:
        return error("Status must be one of: " + ", ".join(MATCH_STATUSES), 400)
    query = Match.query.order_by(Match.id.desc())
    if status:
        query = query.filter_by(status=status)
    return jsonify({"matches": [m.to_dict() for m in query.all()]})


@bp.get("/admin/matches/<int:match_id>")
@role_required("admin")
def get_match(match_id):
    match = db.session.get(Match, match_id)
    if match is None:
        return error("Match not found.", 404)
    return jsonify({"match": match.to_dict()})


@bp.get("/notifications")
@login_required
def my_notifications():
    """The logged-in user's own notifications, newest first."""
    rows = Notification.query.filter_by(user_id=g.user.id).order_by(Notification.id.desc()).all()
    return jsonify({"notifications": [n.to_dict() for n in rows]})


def my_matches(user):
    """The matches of the logged-in student or mentor, newest first."""
    if user.role == "student":
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        return Match.query.filter_by(student_id=profile.id).order_by(Match.id.desc()).all()
    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    return Match.query.filter_by(mentor_id=profile.id).order_by(Match.id.desc()).all()


def with_other_person(match, user):
    """The match, plus the profile of the other person. Their email is shown only once the match is active."""
    other = match.mentor if user.role == "student" else match.student
    person = other.to_dict()
    if match.status not in ("active", "completed"):
        person.pop("email", None)
    return {**match.to_dict(), "other": person}


@bp.get("/matches/me")
@role_required("student", "mentor")
def my_match_list():
    """Matches the logged-in student or mentor is part of, with the other person's profile."""
    return jsonify({"matches": [with_other_person(m, g.user) for m in my_matches(g.user)]})


@bp.post("/matches/<int:match_id>/respond")
@role_required("student", "mentor")
def respond(match_id):
    """The student or the mentor accepts or declines a proposed match. Body: {"answer": "accepted"}"""
    match = db.session.get(Match, match_id)
    if match is None or match not in my_matches(g.user):
        return error("Match not found.", 404)
    answer = json_body().get("answer")
    problem = validators.check_answer(answer)
    if problem:
        return error(problem, 400)
    problem = record_answer(match, g.user.role, answer)
    if problem:
        return error(problem, 409)
    db.session.commit()
    return jsonify({"match": with_other_person(match, g.user)})


@bp.patch("/admin/matches/<int:match_id>/status")
@role_required("admin")
def set_match_status(match_id):
    """The admin confirms (active), completes or cancels a match. Body: {"status": "active"}"""
    match = db.session.get(Match, match_id)
    if match is None:
        return error("Match not found.", 404)
    status = json_body().get("status")
    problem = validators.check_match_status(status)
    if problem:
        return error(problem, 400)
    problem = change_status(match, status, g.user)
    if problem:
        return error(problem, 409)
    db.session.commit()
    return jsonify({"match": match.to_dict()})
