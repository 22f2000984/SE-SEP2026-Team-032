"""Recommendations and creating matches (US-C02)."""
from tests.helpers import MENTOR_PROFILE, auth, check, make_mentor, make_student


def test_recommendations_are_sorted_and_only_eligible(client, admin_token):
    _, student_id = make_student(client)
    _, best = make_mentor(client, admin_token, "meera@mentor.test", "Dr. Meera Iyer")  # both topics, 12 years
    other = {**MENTOR_PROFILE, "topics": ["Data Science"], "experience_years": 2}
    _, second = make_mentor(client, admin_token, "karan@mentor.test", "Karan Shah", other)
    make_mentor(client, admin_token, "pending@mentor.test", "Not Verified", verified=False)
    body = check(client, "GET", f"/api/admin/students/{student_id}/recommendations", 200, "The admin asks for the best mentors for a student",
                 token=admin_token, role="admin", contains="Shared topics")
    ids = [r["mentor_id"] for r in body["recommendations"]]
    assert ids == [best, second]  # unverified mentor is left out, best score first
    assert body["recommendations"][0]["score"] == 100


def test_recommendation_limit(client, admin_token):
    _, student_id = make_student(client)
    make_mentor(client, admin_token, "a@mentor.test", "A")
    make_mentor(client, admin_token, "b@mentor.test", "B")
    body = check(client, "GET", f"/api/admin/students/{student_id}/recommendations?limit=1", 200, "The admin asks for only the top mentor", token=admin_token, role="admin")
    assert len(body["recommendations"]) == 1
    check(client, "GET", f"/api/admin/students/{student_id}/recommendations?limit=0", 400, "The admin asks for a limit of 0", token=admin_token, role="admin")
    check(client, "GET", "/api/admin/students/999/recommendations", 404, "Recommendations for a student that does not exist", token=admin_token, role="admin")


def test_propose_match(client, admin_token):
    student_token, student_id = make_student(client)
    mentor_token, mentor_id = make_mentor(client, admin_token)
    body = check(client, "POST", "/api/admin/matches", 201, "The admin proposes a match",
                 {"student_id": student_id, "mentor_id": mentor_id, "notes": "Goal fit: analytics"}, admin_token, "admin", '"status": "proposed"')
    assert body["match"]["match_score"] == 100
    assert body["match"]["mentor_response"] == "pending"
    # both people are told (notifications)
    note = check(client, "GET", "/api/notifications", 200, "The mentor reads their notifications", token=mentor_token, role="mentor", contains="waiting for your response")
    assert len(note["notifications"]) == 1
    check(client, "GET", "/api/notifications", 200, "The student reads their notifications", token=student_token, role="student", contains="mentor has been proposed")


def test_cannot_propose_unverified_mentor(client, admin_token):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token, verified=False)
    check(client, "POST", "/api/admin/matches", 409, "Proposing a mentor who is not verified",
          {"student_id": student_id, "mentor_id": mentor_id}, admin_token, "admin", "not verified")


def test_cannot_propose_second_open_match_for_a_student(client, admin_token):
    _, student_id = make_student(client)
    _, first = make_mentor(client, admin_token, "a@mentor.test", "A")
    _, second = make_mentor(client, admin_token, "b@mentor.test", "B")
    client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": first}, headers=auth(admin_token))
    check(client, "POST", "/api/admin/matches", 409, "Proposing a second match for a student who already has one",
          {"student_id": student_id, "mentor_id": second}, admin_token, "admin", "already has an open match")


def test_cannot_propose_mentor_with_no_free_places(client, admin_token):
    _, mentor_id = make_mentor(client, admin_token, profile={**MENTOR_PROFILE, "max_students": 1})
    _, first = make_student(client, "a@ds.study.iitm.ac.in", "A")
    _, second = make_student(client, "b@ds.study.iitm.ac.in", "B")
    client.post("/api/admin/matches", json={"student_id": first, "mentor_id": mentor_id}, headers=auth(admin_token))
    check(client, "POST", "/api/admin/matches", 409, "Proposing a mentor whose places are all taken",
          {"student_id": second, "mentor_id": mentor_id}, admin_token, "admin", "no free places")


def test_propose_match_bad_input(client, admin_token):
    _, student_id = make_student(client)
    check(client, "POST", "/api/admin/matches", 400, "Proposing without a mentor", {"student_id": student_id}, admin_token, "admin", "required")
    check(client, "POST", "/api/admin/matches", 400, "Proposing with ids given as text", {"student_id": "1", "mentor_id": "2"}, admin_token, "admin", "whole numbers")
    check(client, "POST", "/api/admin/matches", 404, "Proposing a mentor that does not exist", {"student_id": student_id, "mentor_id": 999}, admin_token, "admin", "not found")


def test_list_and_get_matches(client, admin_token):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    created = client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token)).get_json()
    match_id = created["match"]["match_id"]
    body = check(client, "GET", "/api/admin/matches", 200, "The admin lists all matches", token=admin_token, role="admin")
    assert len(body["matches"]) == 1
    body = check(client, "GET", "/api/admin/matches?status=active", 200, "The admin lists active matches (none yet)", token=admin_token, role="admin")
    assert body["matches"] == []
    check(client, "GET", "/api/admin/matches?status=unknown", 400, "The admin filters by a status that does not exist", token=admin_token, role="admin", contains="Status must be")
    check(client, "GET", f"/api/admin/matches/{match_id}", 200, "The admin opens one match", token=admin_token, role="admin", contains="Asha Verma")
    check(client, "GET", "/api/admin/matches/999", 404, "The admin opens a match that does not exist", token=admin_token, role="admin")


def test_overview_counts_matches_and_waiting_students(client, admin_token):
    _, student_id = make_student(client)
    make_student(client, "rohan@ds.study.iitm.ac.in", "Rohan Das")
    _, mentor_id = make_mentor(client, admin_token)
    client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token))
    body = check(client, "GET", "/api/admin/overview", 200, "The overview after one match is proposed", token=admin_token, role="admin")
    assert body["matches"]["proposed"] == 1
    assert body["students_waiting_for_match"] == 1
