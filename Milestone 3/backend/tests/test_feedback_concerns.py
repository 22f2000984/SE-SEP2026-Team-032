"""Feedback and concerns about a match (US-S09, US-S10)."""
from tests.helpers import auth, check, make_mentor, make_student


def active_match(client, admin_token):
    student_token, student_id = make_student(client)
    mentor_token, mentor_id = make_mentor(client, admin_token)
    match_id = client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token)).get_json()["match"]["match_id"]
    for token in (student_token, mentor_token):
        client.post(f"/api/matches/{match_id}/respond", json={"answer": "accepted"}, headers=auth(token))
    client.patch(f"/api/admin/matches/{match_id}/status", json={"status": "active"}, headers=auth(admin_token))
    return student_token, mentor_token, match_id


def test_student_gives_feedback(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    body = check(client, "POST", f"/api/matches/{match_id}/feedback", 201, "A student rates an active match",
                 {"rating": 5, "comments": "Very helpful"}, student_token, "student", '"rating": 5')
    assert body["feedback"]["author_role"] == "student"


def test_mentor_gives_feedback(client, admin_token):
    _, mentor_token, match_id = active_match(client, admin_token)
    check(client, "POST", f"/api/matches/{match_id}/feedback", 201, "A mentor rates the match too", {"rating": 4}, mentor_token, "mentor", '"author_role": "mentor"')


def test_feedback_rating_must_be_1_to_5(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    check(client, "POST", f"/api/matches/{match_id}/feedback", 400, "A rating of 6 is rejected", {"rating": 6}, student_token, "student", "1 to 5")
    check(client, "POST", f"/api/matches/{match_id}/feedback", 400, "A rating sent as text is rejected", {"rating": "5"}, student_token, "student", "1 to 5")


def test_feedback_only_once(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    client.post(f"/api/matches/{match_id}/feedback", json={"rating": 5}, headers=auth(student_token))
    check(client, "POST", f"/api/matches/{match_id}/feedback", 409, "A second feedback on the same match is refused", {"rating": 3}, student_token, "student", "already")


def test_feedback_needs_an_active_match(client, admin_token):
    student_token, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    match_id = client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token)).get_json()["match"]["match_id"]
    check(client, "POST", f"/api/matches/{match_id}/feedback", 409, "Feedback on a match that is only proposed is refused", {"rating": 5}, student_token, "student", "active")


def test_stranger_cannot_write_about_a_match(client, admin_token):
    _, _, match_id = active_match(client, admin_token)
    stranger, _ = make_student(client, "other@ds.study.iitm.ac.in", "Other Student")
    check(client, "POST", f"/api/matches/{match_id}/feedback", 404, "A student outside the match cannot rate it", {"rating": 5}, stranger, "student")
    check(client, "POST", f"/api/matches/{match_id}/concerns", 404, "A student outside the match cannot raise a concern", {"text": "x"}, stranger, "student")


def test_admin_reads_feedback_and_users_read_their_own(client, admin_token):
    student_token, mentor_token, match_id = active_match(client, admin_token)
    client.post(f"/api/matches/{match_id}/feedback", json={"rating": 5, "comments": "Great"}, headers=auth(student_token))
    client.post(f"/api/matches/{match_id}/feedback", json={"rating": 4}, headers=auth(mentor_token))
    body = check(client, "GET", "/api/admin/feedback", 200, "The admin reads all feedback", token=admin_token, role="admin", contains="Great")
    assert len(body["feedback"]) == 2
    mine = check(client, "GET", "/api/feedback/me", 200, "A student reads only their own feedback", token=student_token, role="student")
    assert len(mine["feedback"]) == 1
    check(client, "GET", "/api/admin/feedback", 403, "A student cannot read all feedback", token=student_token, role="student")


def test_raise_concern_and_admin_resolves_it(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    body = check(client, "POST", f"/api/matches/{match_id}/concerns", 201, "A student raises a concern",
                 {"text": "My mentor does not reply."}, student_token, "student", '"status": "open"')
    concern_id = body["concern"]["concern_id"]
    check(client, "GET", "/api/notifications", 200, "The admin is told about the concern", token=admin_token, role="admin", contains="raised a concern")
    check(client, "GET", "/api/admin/concerns?status=open", 200, "The admin lists open concerns", token=admin_token, role="admin", contains="does not reply")
    check(client, "PATCH", f"/api/admin/concerns/{concern_id}", 200, "The admin resolves the concern", {"status": "resolved"}, admin_token, "admin", '"status": "resolved"')
    check(client, "GET", "/api/notifications", 200, "The student is told it was resolved", token=student_token, role="student", contains="resolved")
    check(client, "GET", "/api/concerns/me", 200, "A student reads their own concerns", token=student_token, role="student", contains="resolved")


def test_concern_input_and_access(client, admin_token):
    student_token, _, match_id = active_match(client, admin_token)
    check(client, "POST", f"/api/matches/{match_id}/concerns", 400, "An empty concern is rejected", {"text": "  "}, student_token, "student", "Describe")
    check(client, "PATCH", "/api/admin/concerns/999", 404, "Resolving a concern that does not exist", {"status": "resolved"}, admin_token, "admin")
    check(client, "GET", "/api/admin/concerns?status=maybe", 400, "A concern filter that does not exist", token=admin_token, role="admin", contains="Status must be")
    check(client, "PATCH", "/api/admin/concerns/1", 403, "A student cannot resolve concerns", {"status": "resolved"}, student_token, "student")
