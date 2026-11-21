"""A student's own profile (US-S01, US-S02)."""
from tests.helpers import STUDENT_PROFILE, check, register


def test_new_student_has_an_empty_profile(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    body = check(client, "GET", "/api/students/me", 200, "A new student opens their profile", token=token, role="student")
    assert body["profile"]["topics"] == []


def test_update_profile(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    body = check(client, "PUT", "/api/students/me", 200, "A student saves a complete profile", STUDENT_PROFILE, token, "student", "Data Science")
    assert body["profile"]["career_goals"] == "Move into data analytics"


def test_partial_update_keeps_other_fields(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    client.put("/api/students/me", json=STUDENT_PROFILE, headers={"Authorization": "Bearer " + token})
    body = check(client, "PUT", "/api/students/me", 200, "Changing only the goals keeps the other fields",
                 {"career_goals": "Become a product manager"}, token, "student")
    assert body["profile"]["programme_level"] == "Diploma"
    assert body["profile"]["career_goals"] == "Become a product manager"


def test_profile_needs_goals(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "Saving without career goals is rejected",
          {**STUDENT_PROFILE, "career_goals": ""}, token, "student", "career goals")


def test_goals_too_long(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "Career goals over 500 characters are rejected",
          {**STUDENT_PROFILE, "career_goals": "x" * 501}, token, "student", "500 characters")


def test_needs_text_too_long(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "Needs text over 800 characters is rejected",
          {**STUDENT_PROFILE, "needs_text": "x" * 801}, token, "student", "800 characters")


def test_at_least_one_topic(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "Saving with no topic is rejected",
          {**STUDENT_PROFILE, "topics": []}, token, "student", "at least one topic")


def test_unknown_topic(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "A topic that does not exist is rejected",
          {**STUDENT_PROFILE, "topics": ["Underwater Basket Weaving"]}, token, "student", "Unknown topic")


def test_bad_duration(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "PUT", "/api/students/me", 400, "A duration that is not in the list is rejected",
          {**STUDENT_PROFILE, "expected_duration": "forever"}, token, "student", "Expected duration")


def test_options_lists(client):
    check(client, "GET", "/api/options", 200, "The profile form asks for the fixed lists", contains="Cloud and DevOps")
