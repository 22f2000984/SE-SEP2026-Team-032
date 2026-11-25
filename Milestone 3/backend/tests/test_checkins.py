"""Mentorship Pulse: weekly check-ins, the review and the admin queue (KAN-41, KAN-42)."""
from datetime import timedelta

from database import db
from models import CheckIn, now
from tests.helpers import auth, check
from tests.test_feedback_concerns import active_match


def set_due(days_ago, week=1):
    """Moves the given week's check-ins so that they were due `days_ago` days ago."""
    for row in CheckIn.query.filter_by(week=week).all():
        row.due_at = now() - timedelta(days=days_ago)
    db.session.commit()


def my_first(client, token):
    return client.get("/api/checkins/me", headers=auth(token)).get_json()["checkins"]


def test_check_ins_are_created_when_a_match_becomes_active(client, admin_token):
    student_token, mentor_token, _ = active_match(client, admin_token)
    body = check(client, "GET", "/api/checkins/me", 200, "The student sees the check-ins of the active match", None, student_token, "student", '"by": "student"')
    assert len(body["checkins"]) == 12  # the sample student chose 3 months = 12 weeks
    check(client, "GET", "/api/checkins/me", 200, "The mentor sees their own check-ins", None, mentor_token, "mentor", '"by": "mentor"')


def test_both_people_get_each_others_email_when_active(client, admin_token):
    active_match(client, admin_token)
    body = check(client, "GET", "/api/admin/emails", 200, "The admin sees the emails sent", None, admin_token, "admin", "meera@mentor.test")
    assert len(body["emails"]) == 2
    assert body["emails"][0]["status"] == "not_configured"  # no Brevo key in the tests


def test_check_in_that_is_not_due_yet_is_refused(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    first = my_first(client, student_token)[0]
    check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 409, "A check-in before its date is refused", {"rating": 4}, student_token, "student", "not due")


def test_student_answers_a_due_check_in(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    body = check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 200, "The student answers with a good rating",
                 {"rating": 5, "comment": "Great session"}, student_token, "student", "on track")
    assert body["checkin"]["state"] == "submitted"
    assert body["checkin"]["review"]["status"] == "ok"


def test_check_in_cannot_be_answered_twice(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    client.post(f"/api/checkins/{first['checkin_id']}/answer", json={"rating": 5}, headers=auth(student_token))
    check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 409, "A second answer is refused", {"rating": 4}, student_token, "student", "already")


def test_rating_must_be_valid(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 400, "A rating of 9 is rejected", {"rating": 9}, student_token, "student", "1 to 5")


def test_someone_else_cannot_answer_my_check_in(client, admin_token):
    student_token, mentor_token, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 404, "The mentor cannot answer the student's check-in", {"rating": 5}, mentor_token, "mentor")
    check(client, "POST", f"/api/checkins/{first['checkin_id']}/answer", 403, "The admin cannot answer check-ins", {"rating": 5}, admin_token, "admin")


def test_low_rating_is_flagged_for_the_admin(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    client.post(f"/api/checkins/{first['checkin_id']}/answer", json={"rating": 1, "comment": "My mentor is not responding"}, headers=auth(student_token))
    body = check(client, "GET", "/api/admin/pulse", 200, "A low rating shows in the admin review queue", None, admin_token, "admin", "needs attention")
    assert len(body["needs_review"]) == 1
    assert body["summary"]["needs_attention"] == 1


def test_admin_marks_a_flagged_check_in_reviewed(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    client.post(f"/api/checkins/{first['checkin_id']}/answer", json={"rating": 2}, headers=auth(student_token))
    check(client, "PATCH", f"/api/admin/checkins/{first['checkin_id']}/review", 200, "The admin marks it reviewed with a note", {"note": "Called the mentor"}, admin_token, "admin", "reviewed")
    check(client, "PATCH", f"/api/admin/checkins/{first['checkin_id']}/review", 409, "Reviewing it again is refused", {}, admin_token, "admin", "already")
    assert client.get("/api/admin/pulse", headers=auth(admin_token)).get_json()["needs_review"] == []


def test_good_answer_does_not_need_a_review(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = my_first(client, student_token)[0]
    client.post(f"/api/checkins/{first['checkin_id']}/answer", json={"rating": 5}, headers=auth(student_token))
    check(client, "PATCH", f"/api/admin/checkins/{first['checkin_id']}/review", 409, "A good answer cannot be reviewed", {}, admin_token, "admin", "does not need")


def test_unanswered_overdue_check_in_goes_to_the_admin(client, admin_token):
    active_match(client, admin_token)
    set_due(10)
    body = check(client, "GET", "/api/admin/pulse", 200, "A check-in nobody answered in time is in the queue", None, admin_token, "admin", "overdue")
    assert len(body["needs_review"]) == 2  # the student's and the mentor's
    assert body["summary"]["unanswered"] == 2


def test_admin_sees_all_check_ins_of_a_match(client, admin_token):
    _, _, match_id = active_match(client, admin_token)
    body = check(client, "GET", f"/api/admin/matches/{match_id}/checkins", 200, "The admin lists the check-ins of one match", None, admin_token, "admin", '"week": 1')
    assert len(body["checkins"]) == 24
    check(client, "GET", "/api/admin/matches/999/checkins", 404, "An unknown match gives 404", None, admin_token, "admin")


def test_check_in_routes_need_the_right_role(client, admin_token):
    check(client, "GET", "/api/checkins/me", 401, "Check-ins need a login")
    check(client, "GET", "/api/admin/pulse", 403, "A student cannot open the admin queue", None, active_match(client, admin_token)[0], "student")


def test_ai_can_raise_the_verdict_but_not_lower_it(client, admin_token, monkeypatch):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    set_due(1, week=2)
    first, second = my_first(client, student_token)[0], my_first(client, student_token)[1]
    monkeypatch.setattr("services.pulse_review.ask_json", lambda instructions, data: {"verdict": "needs attention", "reason": "The student sounds upset."})
    body = client.post(f"/api/checkins/{first['checkin_id']}/answer", json={"rating": 5, "comment": "ok"}, headers=auth(student_token)).get_json()
    assert body["checkin"]["review"]["verdict"] == "needs attention"
    assert body["checkin"]["review"]["source"] == "ai"
    monkeypatch.setattr("services.pulse_review.ask_json", lambda instructions, data: {"verdict": "on track", "reason": "Fine."})
    body = client.post(f"/api/checkins/{second['checkin_id']}/answer", json={"rating": 1, "comment": "bad"}, headers=auth(student_token)).get_json()
    assert body["checkin"]["review"]["verdict"] == "needs attention"  # the rule keeps it high even if the AI says fine
