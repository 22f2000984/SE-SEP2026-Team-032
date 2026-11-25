"""A student asks for a mentor, or says they do not need one now (US-S03)."""
from tests.helpers import auth, check, make_mentor, make_student


def test_new_student_is_looking_by_default(client):
    token, _ = make_student(client)
    check(client, "GET", "/api/students/me", 200, "A new student is looking for a mentor by default", token=token, role="student", contains='"looking_for_mentor": true')


def test_student_pauses_the_request(client, admin_token):
    token, student_id = make_student(client)
    check(client, "DELETE", "/api/students/me/mentor-request", 200, "A student says they do not need a mentor now", token=token, role="student", contains='"looking_for_mentor": false')
    waiting = client.get("/api/admin/overview", headers=auth(admin_token)).get_json()["students_waiting_for_match"]
    assert waiting == 0


def test_admin_cannot_propose_to_a_student_who_is_not_looking(client, admin_token):
    token, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    client.delete("/api/students/me/mentor-request", headers=auth(token))
    check(client, "POST", "/api/admin/matches", 409, "The admin cannot propose a mentor to a student who is not looking",
          {"student_id": student_id, "mentor_id": mentor_id}, admin_token, "admin", "not looking")


def test_student_asks_again_and_admin_is_told(client, admin_token):
    token, _ = make_student(client)
    client.delete("/api/students/me/mentor-request", headers=auth(token))
    check(client, "POST", "/api/students/me/mentor-request", 200, "A student asks for a mentor again", token=token, role="student", contains='"looking_for_mentor": true')
    check(client, "GET", "/api/notifications", 200, "The admin is told that a student asked for a mentor", token=admin_token, role="admin", contains="asked for a mentor")


def test_request_needs_a_filled_profile(client):
    from tests.helpers import register
    token = register(client, "new@ds.study.iitm.ac.in", "student", "New Student")
    check(client, "POST", "/api/students/me/mentor-request", 409, "A student with an empty profile cannot ask for a mentor yet", token=token, role="student", contains="Fill in")


def test_student_with_an_open_match_cannot_pause(client, admin_token):
    token, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token))
    check(client, "DELETE", "/api/students/me/mentor-request", 409, "A student with an open match cannot pause the request", token=token, role="student", contains="open match")
    check(client, "POST", "/api/students/me/mentor-request", 409, "A student with an open match cannot ask again", token=token, role="student", contains="already have")


def test_only_students_use_the_request(client, admin_token):
    check(client, "POST", "/api/students/me/mentor-request", 403, "The admin has no mentor request", token=admin_token, role="admin")
    check(client, "POST", "/api/students/me/mentor-request", 401, "A mentor request without logging in")


def test_looking_flag_must_be_true_or_false(client):
    from tests.helpers import STUDENT_PROFILE
    token, _ = make_student(client)
    check(client, "PUT", "/api/students/me", 400, "looking_for_mentor sent as text is rejected", {**STUDENT_PROFILE, "looking_for_mentor": "yes"}, token, "student", "true or false")


def test_admin_filters_students_by_looking(client, admin_token):
    token, _ = make_student(client)
    make_student(client, "rohan@ds.study.iitm.ac.in", "Rohan Das")
    client.delete("/api/students/me/mentor-request", headers=auth(token))
    body = check(client, "GET", "/api/admin/students?looking=false", 200, "The admin lists students who are not looking", token=admin_token, role="admin", contains="Asha Verma")
    assert len(body["students"]) == 1
