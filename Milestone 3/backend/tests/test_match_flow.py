"""After a match is proposed: both sides answer, the admin confirms or cancels (US-C03, US-C04)."""
from tests.helpers import auth, check, make_mentor, make_student


def proposed_match(client, admin_token):
    student_token, student_id = make_student(client)
    mentor_token, mentor_id = make_mentor(client, admin_token)
    body = client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token)).get_json()
    return student_token, mentor_token, body["match"]["match_id"]


def answer(client, token, match_id, value):
    return client.post(f"/api/matches/{match_id}/respond", json={"answer": value}, headers=auth(token))


def test_student_sees_own_match_without_mentor_email(client, admin_token):
    student_token, _, _ = proposed_match(client, admin_token)
    body = check(client, "GET", "/api/matches/me", 200, "A student lists their own matches", token=student_token, role="student", contains="Dr. Meera Iyer")
    assert "email" not in body["matches"][0]["other"]


def test_mentor_sees_own_match(client, admin_token):
    _, mentor_token, _ = proposed_match(client, admin_token)
    check(client, "GET", "/api/matches/me", 200, "A mentor lists their own matches", token=mentor_token, role="mentor", contains="Asha Verma")


def test_admin_cannot_use_my_matches(client, admin_token):
    check(client, "GET", "/api/matches/me", 403, "The admin has no 'my matches' list", token=admin_token, role="admin")


def test_student_accepts(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    check(client, "POST", f"/api/matches/{match_id}/respond", 200, "A student accepts the proposal",
          {"answer": "accepted"}, token=student_token, role="student", contains='"student_response": "accepted"')


def test_answer_must_be_accepted_or_declined(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    check(client, "POST", f"/api/matches/{match_id}/respond", 400, "An answer other than accepted or declined is rejected",
          {"answer": "maybe"}, token=student_token, role="student", contains="Answer must be")


def test_cannot_answer_twice(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    answer(client, student_token, match_id, "accepted")
    check(client, "POST", f"/api/matches/{match_id}/respond", 409, "A second answer is refused",
          {"answer": "declined"}, token=student_token, role="student", contains="already answered")


def test_other_student_cannot_answer(client, admin_token):
    _, _, match_id = proposed_match(client, admin_token)
    stranger, _ = make_student(client, "other@ds.study.iitm.ac.in", "Other Student")
    check(client, "POST", f"/api/matches/{match_id}/respond", 404, "A student outside the match cannot answer it",
          {"answer": "accepted"}, token=stranger, role="student")


def test_confirm_needs_both_answers(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    answer(client, student_token, match_id, "accepted")
    check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 409, "Confirming with only one answer is refused",
          {"status": "active"}, token=admin_token, role="admin", contains="must accept")


def test_confirm_after_both_accept(client, admin_token):
    student_token, mentor_token, match_id = proposed_match(client, admin_token)
    answer(client, student_token, match_id, "accepted")
    answer(client, mentor_token, match_id, "accepted")
    body = check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 200, "The admin confirms once both accepted",
                 {"status": "active"}, token=admin_token, role="admin", contains='"status": "active"')
    assert body["match"]["confirmed_at"] and len(body["match"]["log"]) == 2
    mine = client.get("/api/matches/me", headers=auth(student_token)).get_json()["matches"][0]
    assert mine["other"]["email"] == "meera@mentor.test"  # the email is shown once the match is active


def test_cancel_a_proposed_match(client, admin_token):
    _, _, match_id = proposed_match(client, admin_token)
    check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 200, "The admin cancels a proposed match",
          {"status": "cancelled"}, token=admin_token, role="admin", contains='"status": "cancelled"')


def test_cancelled_match_is_final(client, admin_token):
    _, _, match_id = proposed_match(client, admin_token)
    client.patch(f"/api/admin/matches/{match_id}/status", json={"status": "cancelled"}, headers=auth(admin_token))
    check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 409, "A cancelled match cannot change again",
          {"status": "active"}, token=admin_token, role="admin", contains="cannot become")


def test_unknown_status_rejected(client, admin_token):
    _, _, match_id = proposed_match(client, admin_token)
    check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 400, "A status that does not exist is rejected",
          {"status": "paused"}, token=admin_token, role="admin", contains="Status must be")


def test_status_change_is_admin_only(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    check(client, "PATCH", f"/api/admin/matches/{match_id}/status", 403, "A student cannot change a match status",
          {"status": "active"}, token=student_token, role="student")


def test_admin_is_told_about_answers(client, admin_token):
    student_token, _, match_id = proposed_match(client, admin_token)
    answer(client, student_token, match_id, "accepted")
    check(client, "GET", "/api/notifications", 200, "The admin is notified when a student answers", token=admin_token, role="admin", contains="accepted the proposed match")
