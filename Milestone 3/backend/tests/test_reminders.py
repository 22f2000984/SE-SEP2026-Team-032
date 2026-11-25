"""The scheduled reminder job and the email sender (KAN-41, KAN-34)."""
from tests.helpers import auth, check
from tests.test_checkins import set_due
from tests.test_feedback_concerns import active_match

SECRET = {"X-Job-Secret": "test-job-secret"}


def test_job_needs_the_secret(client):
    check(client, "POST", "/api/jobs/reminders", 403, "No secret is refused")
    response = client.post("/api/jobs/reminders", headers={"X-Job-Secret": "wrong"})
    assert response.status_code == 403


def test_job_is_off_without_a_secret_in_the_settings(client):
    from flask import current_app
    current_app.config["JOBS_SECRET"] = ""
    check(client, "POST", "/api/jobs/reminders", 503, "The job is off when no secret is set", None, None, "", "not switched on")


def test_reminders_go_to_people_with_due_check_ins_once(client, admin_token):
    student_token, _, _ = active_match(client, admin_token)
    set_due(1)
    first = client.post("/api/jobs/reminders", headers=SECRET)
    assert first.status_code == 200 and first.get_json()["reminders_sent"] == 2  # the student and the mentor
    again = client.post("/api/jobs/reminders", headers=SECRET)
    assert again.get_json()["reminders_sent"] == 0  # nobody is reminded twice
    notes = client.get("/api/notifications", headers=auth(student_token)).get_json()["notifications"]
    assert any("Check-in reminder" in n["message"] for n in notes)


def test_no_reminder_for_check_ins_that_are_not_due(client, admin_token):
    active_match(client, admin_token)
    assert client.post("/api/jobs/reminders", headers=SECRET).get_json()["reminders_sent"] == 0


def test_email_is_sent_through_brevo_when_configured(client, admin_token, monkeypatch):
    from flask import current_app
    current_app.config["BREVO_API_KEY"] = "fake-key"
    current_app.config["EMAIL_FROM"] = "team@example.com"
    monkeypatch.setattr("services.emailer.post_to_brevo", lambda user, subject, body: True)
    active_match(client, admin_token)
    emails = client.get("/api/admin/emails", headers=auth(admin_token)).get_json()["emails"]
    assert [e["status"] for e in emails] == ["sent", "sent"]


def test_failed_email_is_logged_as_failed(client, admin_token, monkeypatch):
    from flask import current_app
    current_app.config["BREVO_API_KEY"] = "fake-key"
    current_app.config["EMAIL_FROM"] = "team@example.com"
    monkeypatch.setattr("services.emailer.post_to_brevo", lambda user, subject, body: False)
    active_match(client, admin_token)
    emails = client.get("/api/admin/emails", headers=auth(admin_token)).get_json()["emails"]
    assert emails[0]["status"] == "failed"
