"""Level quiz (added after the Sprint 1 user feedback)."""
from tests.helpers import auth, check, make_mentor, make_student


def take(topic="Data Science", answers=(1, 1, 1, 1, 1)):
    return {"topic": topic, "answers": list(answers)}


def test_questions_are_listed(client):
    token, _ = make_student(client)
    body = check(client, "GET", "/api/quiz", 200, "A student reads the quiz", None, token, "student", "mentor")
    assert len(body["questions"]) == 5


def test_each_level(client):
    token, _ = make_student(client)
    for answers, level in (((0, 0, 0, 0, 0), "beginner"), ((1, 1, 1, 1, 1), "intermediate"), ((2, 2, 2, 2, 2), "advanced")):
        check(client, "POST", "/api/students/me/quiz", 200, f"Answers give the level {level}", take(answers=answers), token, "student", level)
    levels = client.get("/api/students/me", headers=auth(token)).get_json()["profile"]["levels"]
    assert levels == {"Data Science": "advanced"}  # the newest result replaces the old one


def test_bad_quiz_input(client):
    token, _ = make_student(client)
    check(client, "POST", "/api/students/me/quiz", 400, "An unknown topic is rejected", take("Cooking"), token, "student", "topic")
    check(client, "POST", "/api/students/me/quiz", 400, "Too few answers are rejected", take(answers=(1, 1)), token, "student", "list")
    check(client, "POST", "/api/students/me/quiz", 400, "An answer of 5 is rejected", take(answers=(5, 1, 1, 1, 1)), token, "student", "0, 1 or 2")


def test_quiz_is_for_students(client, admin_token):
    check(client, "POST", "/api/students/me/quiz", 403, "The admin cannot take the quiz", take(), admin_token, "admin")


def test_smart_match_shows_the_level(client, admin_token):
    token, student_id = make_student(client)
    make_mentor(client, admin_token)
    client.post("/api/students/me/quiz", json=take(), headers=auth(token))
    check(client, "GET", f"/api/admin/students/{student_id}/smart-recommendations", 200, "Smart Match shows the quiz level", None, admin_token, "admin", "intermediate")
