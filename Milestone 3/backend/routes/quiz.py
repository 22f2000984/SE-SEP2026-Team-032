"""Level quiz routes (a student's own results only)."""
from flask import Blueprint, g, jsonify

from auth_utils import login_required, role_required
from constants import QUIZ_QUESTIONS, TOPICS
from database import db
from models import StudentProfile
from responses import error, json_body
from services.quiz import check_answers, save_result

bp = Blueprint("quiz", __name__, url_prefix="/api")


@bp.get("/quiz")
@login_required
def questions():
    return jsonify({"questions": QUIZ_QUESTIONS})


@bp.post("/students/me/quiz")
@role_required("student")
def take_quiz():
    """Body: {"topic": "Data Science", "answers": [0, 1, 2, 1, 0]}"""
    data = json_body()
    topic = data.get("topic")
    if topic not in TOPICS:
        return error("topic must be one of: " + ", ".join(TOPICS), 400)
    problem = check_answers(data.get("answers"))
    if problem:
        return error(problem, 400)
    student = StudentProfile.query.filter_by(user_id=g.user.id).first()
    result = save_result(student, topic, data["answers"])
    db.session.commit()
    return jsonify({"result": result.to_dict()})
