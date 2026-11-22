"""A mentor must finish the profile first; only then the admin sees them for verification (with their email)."""
from tests.helpers import MENTOR_PROFILE, auth, check, register

SLOT = {"day_of_week": "Monday", "start_time": "18:00", "end_time": "19:00"}


def new_mentor(client, email="new@mentor.test", name="New Mentor"):
    token = register(client, email, "mentor", name)
    profile_id = client.get("/api/mentors/me", headers=auth(token)).get_json()["profile"]["mentor_id"]
    return token, profile_id


def test_new_mentor_profile_is_incomplete(client):
    token, _ = new_mentor(client)
    body = check(client, "GET", "/api/mentors/me", 200, "A new mentor's profile is not complete", token=token, role="mentor", contains='"profile_complete": false')
    assert body["profile"]["profile_status"] == "pending"


def test_incomplete_mentor_is_hidden_from_admin(client, admin_token):
    new_mentor(client)
    body = check(client, "GET", "/api/admin/mentors", 200, "The admin does not see a mentor who has not finished the profile", token=admin_token, role="admin")
    assert body["mentors"] == []
    overview = client.get("/api/admin/overview", headers=auth(admin_token)).get_json()
    assert overview["mentors"]["pending"] == 0 and overview["mentors"]["incomplete"] == 1


def test_profile_without_availability_is_still_incomplete(client, admin_token):
    token, _ = new_mentor(client)
    client.put("/api/mentors/me", json=MENTOR_PROFILE, headers=auth(token))
    body = client.get("/api/admin/mentors", headers=auth(admin_token)).get_json()
    assert body["mentors"] == []


def test_completed_mentor_appears_with_email(client, admin_token):
    token, _ = new_mentor(client)
    client.put("/api/mentors/me", json=MENTOR_PROFILE, headers=auth(token))
    client.post("/api/mentors/me/availability", json=SLOT, headers=auth(token))
    body = check(client, "GET", "/api/admin/mentors?status=pending", 200, "A mentor who finished the profile is on the verification list, with their email",
                 token=admin_token, role="admin", contains="new@mentor.test")
    assert body["mentors"][0]["profile_complete"] is True


def test_admin_is_told_when_a_mentor_finishes(client, admin_token):
    token, _ = new_mentor(client)
    client.put("/api/mentors/me", json=MENTOR_PROFILE, headers=auth(token))
    client.post("/api/mentors/me/availability", json=SLOT, headers=auth(token))
    check(client, "GET", "/api/notifications", 200, "The admin is notified that the mentor is ready for verification",
          token=admin_token, role="admin", contains="waiting for verification")


def test_cannot_verify_an_incomplete_mentor(client, admin_token):
    _, mentor_id = new_mentor(client)
    check(client, "PATCH", f"/api/admin/mentors/{mentor_id}/status", 409, "The admin cannot verify a mentor who has not finished the profile",
          {"status": "verified"}, admin_token, "admin", "not finished")
