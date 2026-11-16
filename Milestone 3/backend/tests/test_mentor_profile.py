"""A mentor's own profile and availability (US-M01, US-M02)."""
from tests.helpers import MENTOR_PROFILE, auth, check, register


def test_update_profile(client):
    token = register(client, "meera@mentor.test", "mentor")
    body = check(client, "PUT", "/api/mentors/me", 200, "A mentor saves a complete profile", MENTOR_PROFILE, token, "mentor", "PhD, Data Science")
    assert body["profile"]["profile_status"] == "pending"


def test_mentor_cannot_verify_themselves(client):
    token = register(client, "meera@mentor.test", "mentor")
    body = check(client, "PUT", "/api/mentors/me", 200, "A mentor tries to set their own status to verified (ignored)",
                 {**MENTOR_PROFILE, "profile_status": "verified"}, token, "mentor")
    assert body["profile"]["profile_status"] == "pending"


def test_qualifications_required(client):
    token = register(client, "meera@mentor.test", "mentor")
    check(client, "PUT", "/api/mentors/me", 400, "Saving without qualifications is rejected",
          {**MENTOR_PROFILE, "qualifications": ""}, token, "mentor", "Qualifications")


def test_negative_experience(client):
    token = register(client, "meera@mentor.test", "mentor")
    check(client, "PUT", "/api/mentors/me", 400, "Negative years of experience are rejected",
          {**MENTOR_PROFILE, "experience_years": -2}, token, "mentor", "Experience")


def test_experience_must_be_a_number(client):
    token = register(client, "meera@mentor.test", "mentor")
    check(client, "PUT", "/api/mentors/me", 400, "Experience given as text is rejected",
          {**MENTOR_PROFILE, "experience_years": "twelve"}, token, "mentor", "Experience")


def test_capacity_above_ten(client):
    token = register(client, "meera@mentor.test", "mentor")
    check(client, "PUT", "/api/mentors/me", 400, "A maximum of 11 students is rejected",
          {**MENTOR_PROFILE, "max_students": 11}, token, "mentor", "from 1 to 10")


def test_add_and_remove_slot(client):
    token = register(client, "meera@mentor.test", "mentor")
    slot = {"day_of_week": "Saturday", "start_time": "18:00", "end_time": "20:00"}
    body = check(client, "POST", "/api/mentors/me/availability", 201, "A mentor adds an availability slot", slot, token, "mentor", "Saturday")
    slot_id = body["slot"]["slot_id"]
    check(client, "DELETE", f"/api/mentors/me/availability/{slot_id}", 204, "A mentor removes their slot", token=token, role="mentor")
    check(client, "DELETE", f"/api/mentors/me/availability/{slot_id}", 404, "Removing the same slot again", token=token, role="mentor", contains="not found")


def test_slot_end_before_start(client):
    token = register(client, "meera@mentor.test", "mentor")
    slot = {"day_of_week": "Saturday", "start_time": "20:00", "end_time": "18:00"}
    check(client, "POST", "/api/mentors/me/availability", 400, "A slot that ends before it starts is rejected", slot, token, "mentor", "End time")


def test_slot_bad_day(client):
    token = register(client, "meera@mentor.test", "mentor")
    slot = {"day_of_week": "Funday", "start_time": "18:00", "end_time": "20:00"}
    check(client, "POST", "/api/mentors/me/availability", 400, "A day that does not exist is rejected", slot, token, "mentor", "Day must be")


def test_cannot_remove_another_mentors_slot(client):
    first = register(client, "meera@mentor.test", "mentor")
    second = register(client, "karan@mentor.test", "mentor")
    slot = {"day_of_week": "Sunday", "start_time": "17:00", "end_time": "19:00"}
    slot_id = client.post("/api/mentors/me/availability", json=slot, headers=auth(first)).get_json()["slot"]["slot_id"]
    check(client, "DELETE", f"/api/mentors/me/availability/{slot_id}", 404, "A mentor tries to remove another mentor's slot", token=second, role="mentor")
