"""Inputs of the wrong type. Before these tests were added, each of the cases below crashed the server (HTTP 500)
instead of answering 400; see 'Bugs found by testing' in the Milestone 3 report."""
from tests.helpers import MENTOR_PROFILE, STUDENT_PROFILE, check, register


def test_body_is_a_list_not_an_object(client):
    check(client, "POST", "/api/auth/register", 400, "Registration where the body is a list, not an object", [1, 2])
    check(client, "POST", "/api/auth/login", 401, "Login where the body is a list, not an object", [1, 2])
    token = register(client, "asha@student.test", "student")
    check(client, "PUT", "/api/students/me", 400, "Student profile where the body is a list", [1, 2], token, "student")


def test_student_text_fields_must_be_text(client):
    token = register(client, "asha@student.test", "student")
    check(client, "PUT", "/api/students/me", 400, "needs_text sent as a number",
          {**STUDENT_PROFILE, "needs_text": 123}, token, "student", "needs_text must be text")
    check(client, "PUT", "/api/students/me", 400, "skills sent as a list",
          {**STUDENT_PROFILE, "skills": ["Python"]}, token, "student", "skills must be text")
    check(client, "PUT", "/api/students/me", 400, "career_goals sent as a number",
          {**STUDENT_PROFILE, "career_goals": 5}, token, "student", "career_goals must be text")


def test_mentor_text_fields_must_be_text(client):
    token = register(client, "meera@mentor.test", "mentor")
    check(client, "PUT", "/api/mentors/me", 400, "bio sent as a list",
          {**MENTOR_PROFILE, "bio": ["x"]}, token, "mentor", "bio must be text")
    check(client, "PUT", "/api/mentors/me", 400, "qualifications sent as a number",
          {**MENTOR_PROFILE, "qualifications": 99}, token, "mentor", "qualifications must be text")


def test_login_with_numbers(client):
    check(client, "POST", "/api/auth/login", 401, "Login with numbers instead of text", {"email": 5, "password": 5})


def test_server_still_works_after_bad_input(client):
    token = register(client, "asha@student.test", "student")
    client.put("/api/students/me", json={**STUDENT_PROFILE, "skills": ["Python"]}, headers={"Authorization": "Bearer " + token})
    check(client, "GET", "/api/students/me", 200, "A normal request right after bad input works", token=token, role="student")
