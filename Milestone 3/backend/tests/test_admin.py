"""The admin dashboard (US-C01, US-C05)."""
from tests.helpers import auth, check, make_mentor, make_student, register


def test_overview_counts(client, admin_token):
    make_student(client)
    make_mentor(client, admin_token, verified=False)
    body = check(client, "GET", "/api/admin/overview", 200, "The admin opens the overview", token=admin_token, role="admin", contains="students_waiting_for_match")
    assert body["students"] == 1
    assert body["mentors"] == {"total": 1, "verified": 0, "pending": 1}
    assert body["students_waiting_for_match"] == 1


def test_list_and_search_students(client, admin_token):
    make_student(client, "asha@student.test", "Asha Verma")
    make_student(client, "rohan@student.test", "Rohan Das", {"programme_level": "Foundation", "career_goals": "Interviews",
                 "mentoring_format": "No preference", "expected_duration": "1 month", "topics": ["Web Development"], "skills": "JavaScript"})
    body = check(client, "GET", "/api/admin/students", 200, "The admin lists all students", token=admin_token, role="admin")
    assert len(body["students"]) == 2
    body = check(client, "GET", "/api/admin/students?search=rohan", 200, "The admin searches students by name", token=admin_token, role="admin", contains="Rohan Das")
    assert len(body["students"]) == 1
    body = check(client, "GET", "/api/admin/students?topic=Data Science", 200, "The admin filters students by topic", token=admin_token, role="admin", contains="Asha Verma")
    assert len(body["students"]) == 1
    body = check(client, "GET", "/api/admin/students?programme_level=Foundation", 200, "The admin filters students by programme level", token=admin_token, role="admin")
    assert len(body["students"]) == 1


def test_get_one_student(client, admin_token):
    _, student_id = make_student(client)
    check(client, "GET", f"/api/admin/students/{student_id}", 200, "The admin opens one student's profile", token=admin_token, role="admin", contains="Move into data analytics")
    check(client, "GET", "/api/admin/students/999", 404, "The admin opens a student that does not exist", token=admin_token, role="admin", contains="not found")


def test_list_and_filter_mentors(client, admin_token):
    make_mentor(client, admin_token, "meera@mentor.test", "Dr. Meera Iyer", verified=True)
    make_mentor(client, admin_token, "karan@mentor.test", "Karan Shah", verified=False)
    body = check(client, "GET", "/api/admin/mentors", 200, "The admin lists all mentors", token=admin_token, role="admin")
    assert len(body["mentors"]) == 2
    body = check(client, "GET", "/api/admin/mentors?status=pending", 200, "The admin lists mentors waiting for verification", token=admin_token, role="admin", contains="Karan Shah")
    assert len(body["mentors"]) == 1
    body = check(client, "GET", "/api/admin/mentors?search=meera", 200, "The admin searches mentors by name", token=admin_token, role="admin")
    assert len(body["mentors"]) == 1


def test_get_one_mentor(client, admin_token):
    _, mentor_id = make_mentor(client, admin_token)
    check(client, "GET", f"/api/admin/mentors/{mentor_id}", 200, "The admin opens one mentor's profile", token=admin_token, role="admin", contains="PhD, Data Science")
    check(client, "GET", "/api/admin/mentors/999", 404, "The admin opens a mentor that does not exist", token=admin_token, role="admin")


def test_admin_edits_mentor(client, admin_token):
    _, mentor_id = make_mentor(client, admin_token)
    body = check(client, "PUT", f"/api/admin/mentors/{mentor_id}", 200, "The admin updates a mentor's experience and topics",
                 {"experience_years": 15, "topics": ["Cloud and DevOps"]}, admin_token, "admin", "Cloud and DevOps")
    assert body["profile"]["experience_years"] == 15
    assert body["profile"]["qualifications"] == "PhD, Data Science"  # fields not sent stay the same
    check(client, "PUT", f"/api/admin/mentors/{mentor_id}", 400, "The admin sets an invalid capacity",
          {"max_students": 0}, admin_token, "admin", "from 1 to 10")


def test_verify_mentor(client, admin_token):
    _, mentor_id = make_mentor(client, admin_token, verified=False)
    body = check(client, "PATCH", f"/api/admin/mentors/{mentor_id}/status", 200, "The admin verifies a mentor",
                 {"status": "verified"}, admin_token, "admin", "verified")
    assert body["profile"]["profile_status"] == "verified"
    check(client, "PATCH", f"/api/admin/mentors/{mentor_id}/status", 400, "The admin sends a status that does not exist",
          {"status": "banned"}, admin_token, "admin", "Status must be")
    check(client, "PATCH", "/api/admin/mentors/999/status", 404, "The admin verifies a mentor that does not exist",
          {"status": "verified"}, admin_token, "admin")


def test_admin_edits_availability(client, admin_token):
    _, mentor_id = make_mentor(client, admin_token)
    slot = {"day_of_week": "Wednesday", "start_time": "18:00", "end_time": "19:30"}
    body = check(client, "POST", f"/api/admin/mentors/{mentor_id}/availability", 201, "The admin adds a slot for a mentor", slot, admin_token, "admin", "Wednesday")
    check(client, "DELETE", f"/api/admin/mentors/{mentor_id}/availability/{body['slot']['slot_id']}", 204, "The admin removes that slot", token=admin_token, role="admin")
    check(client, "POST", "/api/admin/mentors/999/availability", 404, "The admin adds a slot for a mentor that does not exist", slot, admin_token, "admin")
