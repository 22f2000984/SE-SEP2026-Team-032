"""Level quiz: turns a student's answers for one topic into beginner, intermediate or advanced, and saves it."""
from constants import QUIZ_LEVELS, QUIZ_QUESTIONS
from database import db
from models import QuizResult, now


def level_for(score):
    for highest, level in QUIZ_LEVELS:
        if score <= highest:
            return level
    return QUIZ_LEVELS[-1][1]


def check_answers(answers):
    """answers must be one whole number (0, 1 or 2) for every question. Returns an error message or None."""
    if not isinstance(answers, list) or len(answers) != len(QUIZ_QUESTIONS):
        return f"answers must be a list of {len(QUIZ_QUESTIONS)} numbers."
    for answer, question in zip(answers, QUIZ_QUESTIONS):
        if not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer < len(question["options"]):
            return "Each answer must be 0, 1 or 2."
    return None


def save_result(student, topic, answers):
    """One result per student and topic: taking the quiz again replaces the old one."""
    result = QuizResult.query.filter_by(student_id=student.id, topic=topic).first()
    if result is None:
        result = QuizResult(student=student, topic=topic)
        db.session.add(result)
    result.score = sum(answers)
    result.level = level_for(result.score)
    result.taken_at = now()
    return result
