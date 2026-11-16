"""Helpers for the tests.

check() makes one API call, compares it with what we expect and records a row for the test-case table
(API being tested, inputs, expected output, actual output, result). conftest.py writes the table at the end of the run."""
import json

CASES = []  # one dict per check() call


def auth(token):
    return {"Authorization": "Bearer " + token} if token else {}


def short(value, limit=160):
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return text if len(text) <= limit else text[:limit] + "..."


def hide_password(data):
    if isinstance(data, dict) and "password" in data:
        return {**data, "password": "******"}
    return data


def check(client, method, url, status, case, json_body=None, token=None, role="", contains=None):
    """Calls the API and asserts that the status code is `status` and, if given, that `contains` is in the body.
    `case` is a short description of the test case; `role` says who is calling (for the table only)."""
    response = client.open(url, method=method, json=json_body, headers=auth(token))
    body = response.get_json(silent=True)
    actual_text = json.dumps(body, ensure_ascii=False) if body is not None else ""
    passed = response.status_code == status and (contains is None or contains in actual_text)

    inputs = "no body" if json_body is None else short(hide_password(json_body))
    if role:
        inputs = f"[{role}] " + inputs
    expected = f"{status}" + (f", body contains '{contains}'" if contains else "")
    CASES.append({
        "api": f"{method} {url}", "case": case, "inputs": inputs, "expected": expected,
        "actual": f"{response.status_code} {short(body) if body is not None else '(empty)'}",
        "result": "Success" if passed else "Fail",
    })
    assert passed, f"{case}: expected {expected}, got {response.status_code} {actual_text}"
    return body


# ---- small setup helpers (not recorded as test cases) ----

def register(client, email, role, name="Test User", password="secret1"):
    client.post("/api/auth/register", json={"full_name": name, "email": email, "password": password, "role": role})
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    return response.get_json()["token"]


STUDENT_PROFILE = {
    "programme_level": "Diploma", "career_goals": "Move into data analytics", "skills": "Python, SQL",
    "needs_text": "I need help building a portfolio.", "mentoring_format": "Video call",
    "expected_duration": "3 months", "topics": ["Data Science", "Career Switching"],
}
MENTOR_PROFILE = {
    "qualifications": "PhD, Data Science", "experience_years": 12, "bio": "Leads an analytics team.",
    "skills_text": "I coach students on analytics careers.", "max_students": 3, "topics": ["Data Science", "Career Switching"],
}


def make_student(client, email="asha@student.test", name="Asha Verma", profile=None):
    """Registers a student, fills the profile and returns (token, student_id)."""
    token = register(client, email, "student", name)
    body = client.put("/api/students/me", json=profile or STUDENT_PROFILE, headers=auth(token)).get_json()
    return token, body["profile"]["student_id"]


def make_mentor(client, admin_token, email="meera@mentor.test", name="Dr. Meera Iyer", profile=None, verified=True):
    """Registers a mentor, fills the profile, optionally verifies them, and returns (token, mentor_id)."""
    token = register(client, email, "mentor", name)
    body = client.put("/api/mentors/me", json=profile or MENTOR_PROFILE, headers=auth(token)).get_json()
    mentor_id = body["profile"]["mentor_id"]
    if verified:
        client.patch(f"/api/admin/mentors/{mentor_id}/status", json={"status": "verified"}, headers=auth(admin_token))
    return token, mentor_id
