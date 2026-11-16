"""Role-based access control (US-C06). The server must refuse, not just the frontend hide the link."""
from tests.helpers import check, make_mentor, make_student, register


def test_admin_routes_need_login(client):
    for url in ("/api/admin/overview", "/api/admin/students", "/api/admin/mentors", "/api/admin/matches"):
        check(client, "GET", url, 401, "Admin page without logging in", contains="log in")


def test_student_cannot_use_admin_routes(client, admin_token):
    student_token, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    check(client, "GET", "/api/admin/overview", 403, "A student asks for the admin overview", token=student_token, role="student", contains="not allowed")
    check(client, "GET", "/api/admin/mentors", 403, "A student tries to browse the mentor list", token=student_token, role="student")
    check(client, "GET", f"/api/admin/mentors/{mentor_id}", 403, "A student tries to open a mentor's profile", token=student_token, role="student")
    check(client, "GET", "/api/admin/students", 403, "A student tries to browse all students", token=student_token, role="student")
    check(client, "GET", f"/api/admin/students/{student_id}", 403, "A student tries to open a student profile through the admin route", token=student_token, role="student")


def test_mentor_cannot_use_admin_routes(client, admin_token):
    mentor_token, mentor_id = make_mentor(client, admin_token)
    _, student_id = make_student(client)
    check(client, "GET", "/api/admin/students", 403, "A mentor tries to browse students", token=mentor_token, role="mentor")
    check(client, "GET", f"/api/admin/students/{student_id}", 403, "A mentor tries to open a student's profile", token=mentor_token, role="mentor")
    check(client, "PATCH", f"/api/admin/mentors/{mentor_id}/status", 403, "A mentor tries to verify themselves through the admin route",
          {"status": "verified"}, mentor_token, "mentor")


def test_students_and_mentors_only_reach_their_own_profile_routes(client, admin_token):
    student_token, _ = make_student(client)
    mentor_token, _ = make_mentor(client, admin_token)
    check(client, "GET", "/api/mentors/me", 403, "A student opens the mentor profile route", token=student_token, role="student")
    check(client, "GET", "/api/students/me", 403, "A mentor opens the student profile route", token=mentor_token, role="mentor")
    check(client, "GET", "/api/students/me", 403, "The admin opens the student profile route", token=admin_token, role="admin")


def test_student_and_mentor_cannot_create_matches(client, admin_token):
    student_token, student_id = make_student(client)
    mentor_token, mentor_id = make_mentor(client, admin_token)
    body = {"student_id": student_id, "mentor_id": mentor_id}
    check(client, "POST", "/api/admin/matches", 403, "A student tries to create a match", body, student_token, "student")
    check(client, "POST", "/api/admin/matches", 403, "A mentor tries to create a match", body, mentor_token, "mentor")
    check(client, "POST", "/api/admin/matches", 401, "Creating a match without logging in", body)


def test_unknown_route(client):
    check(client, "GET", "/api/nothing-here", 404, "A route that does not exist", contains="Not found")
