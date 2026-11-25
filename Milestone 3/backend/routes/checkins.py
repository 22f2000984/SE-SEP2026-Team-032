"""Mentorship Pulse routes. Students and mentors answer their weekly check-ins; the admin reviews the flagged ones."""
from flask import Blueprint, g, jsonify, request

import validators
from auth_utils import role_required
from database import db
from models import CheckIn, Match
from responses import error, json_body
from services.analytics import pulse_summary
from services.checkins import active_check_ins, flagged_check_ins, mark_reviewed, save_answer

bp = Blueprint("checkins", __name__, url_prefix="/api")


@bp.get("/checkins/me")
@role_required("student", "mentor")
def my_check_ins():
    """The logged-in person's own check-ins for active matches. Optional filter: ?state=due|overdue|upcoming|submitted"""
    state = request.args.get("state")
    rows = [c for c in active_check_ins() if c.user_id == g.user.id]
    if state:
        rows = [c for c in rows if c.state() == state]
    return jsonify({"checkins": [c.to_dict() for c in rows]})


@bp.post("/checkins/<int:checkin_id>/answer")
@role_required("student", "mentor")
def answer_check_in(checkin_id):
    """Body: {"rating": 1 to 5, "comment": "..."}. Only the person it belongs to, once it is due, and only once."""
    checkin = db.session.get(CheckIn, checkin_id)
    if checkin is None or checkin.user_id != g.user.id:
        return error("Check-in not found.", 404)
    data = json_body()
    problem = validators.check_feedback({"rating": data.get("rating"), "comments": data.get("comment")})
    if problem:
        return error(problem, 400)
    if checkin.match.status != "active":
        return error("This match is not active, so there is nothing to check in on.", 409)
    if checkin.submitted_at:
        return error("You have already answered this check-in.", 409)
    if checkin.state() == "upcoming":
        return error("This check-in is not due yet.", 409)
    save_answer(checkin, data["rating"], data.get("comment"))
    db.session.commit()
    return jsonify({"checkin": checkin.to_dict()})


@bp.get("/admin/pulse")
@role_required("admin")
def pulse():
    """The review queue (flagged answers and check-ins nobody answered) plus the summary numbers."""
    return jsonify({"summary": pulse_summary(), "needs_review": [c.to_dict() for c in flagged_check_ins()]})


@bp.get("/admin/matches/<int:match_id>/checkins")
@role_required("admin")
def match_check_ins(match_id):
    """All check-ins of one match, week by week."""
    if db.session.get(Match, match_id) is None:
        return error("Match not found.", 404)
    rows = CheckIn.query.filter_by(match_id=match_id).order_by(CheckIn.week, CheckIn.by_role).all()
    return jsonify({"checkins": [c.to_dict() for c in rows]})


@bp.patch("/admin/checkins/<int:checkin_id>/review")
@role_required("admin")
def review_check_in(checkin_id):
    """The admin marks a flagged check-in as reviewed. Body: {"note": "what I did"} (optional)."""
    checkin = db.session.get(CheckIn, checkin_id)
    if checkin is None:
        return error("Check-in not found.", 404)
    note = json_body().get("note")
    if note is not None and not isinstance(note, str):
        return error("note must be text.", 400)
    if checkin.review_status == "reviewed":
        return error("This check-in is already reviewed.", 409)
    if not (checkin.review_status == "open" or (checkin.submitted_at is None and checkin.state() == "overdue")):
        return error("This check-in does not need a review.", 409)
    mark_reviewed(checkin, note)
    db.session.commit()
    return jsonify({"checkin": checkin.to_dict()})
