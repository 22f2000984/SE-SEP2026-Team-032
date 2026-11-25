"""Readiness, notifications read marks, and admin analytics (KAN-37, KAN-35)."""
from tests.helpers import auth, check, make_student, register
from tests.test_checkins import set_due
from tests.test_feedback_concerns import active_match


def test_empty_profile_is_not_ready(client):
    token = register(client, "new@ds.study.iitm.ac.in", "student")
    body = check(client, "GET", "/api/students/me/readiness", 200, "A new student's profile is not ready", None, token, "student", '"ready": false')
    assert body["percent"] == 0


def test_filled_profile_is_ready(client):
    token, _ = make_student(client)
    body = check(client, "GET", "/api/students/me/readiness", 200, "A filled profile is ready", None, token, "student", '"ready": true')
    assert body["percent"] > 60


def test_readiness_is_for_students_only(client, admin_token):
    check(client, "GET", "/api/students/me/readiness", 403, "The admin has no readiness checklist", None, admin_token, "admin")


def test_mark_notifications_read(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    notes = client.get("/api/notifications", headers=auth(student_token)).get_json()["notifications"]
    first = notes[0]["notification_id"]
    body = check(client, "PATCH", f"/api/notifications/{first}/read", 200, "A user marks one notification read", None, student_token, "student", '"is_read": true')
    assert body["notification"]["is_read"] is True
    check(client, "POST", "/api/notifications/read-all", 200, "A user marks all notifications read", None, student_token, "student", "marked")
    check(client, "PATCH", f"/api/notifications/{first}/read", 404, "Another user's notification gives 404", None, admin_token, "admin")


def test_admin_analytics(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    client.post(f"/api/matches/{match_id}/feedback", json={"rating": 4}, headers=auth(student_token))
    set_due(1)
    body = check(client, "GET", "/api/admin/analytics", 200, "The admin reads the dashboard numbers", None, admin_token, "admin", "response_rate")
    assert body["feedback"]["total"] == 1 and body["feedback"]["average"] == 4.0
    assert body["pulse"]["asked"] == 2
    assert body["capacity"]["used"] == 1


def test_analytics_and_emails_are_admin_only(client):
    token, _ = make_student(client)
    check(client, "GET", "/api/admin/analytics", 403, "A student cannot read analytics", None, token, "student")
    check(client, "GET", "/api/admin/emails", 403, "A student cannot read the email log", None, token, "student")
