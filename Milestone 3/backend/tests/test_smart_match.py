"""Smart Match (KAN-40): ranking by free text, with a rule fallback when the AI is off or fails."""
from tests.helpers import auth, check, make_mentor, make_student
from services.smart_match import keywords


def test_keywords_ignore_small_words():
    words = list(keywords("I want help with analytics").values())
    assert "analytics" in words and "want" not in words


def test_smart_recommendations_use_rules_without_ai(client, admin_token):
    _, student_id = make_student(client)
    make_mentor(client, admin_token)
    body = check(client, "GET", f"/api/admin/students/{student_id}/smart-recommendations", 200, "Smart Match falls back to rules when the AI is off",
                 None, admin_token, "admin", '"source": "rules"')
    assert body["recommendations"][0]["mentor_name"] == "Dr. Meera Iyer"
    assert 0 <= body["recommendations"][0]["score"] <= 100


def test_smart_recommendations_use_ai_when_available(client, admin_token, monkeypatch):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    monkeypatch.setattr("services.smart_match.ask_json", lambda instructions, data: {"results": [{"mentor_id": mentor_id, "fit": 90, "reason": "Great fit"}]})
    body = check(client, "GET", f"/api/admin/students/{student_id}/smart-recommendations", 200, "Smart Match uses the AI score and reason",
                 None, admin_token, "admin", "Great fit")
    assert body["source"] == "ai"
    assert body["recommendations"][0]["text_fit"] == 90


def test_bad_ai_answer_falls_back_to_rules(client, admin_token, monkeypatch):
    _, student_id = make_student(client)
    make_mentor(client, admin_token)
    monkeypatch.setattr("services.smart_match.ask_json", lambda instructions, data: {"results": "nonsense"})
    body = client.get(f"/api/admin/students/{student_id}/smart-recommendations", headers=auth(admin_token)).get_json()
    assert body["source"] == "rules" and len(body["recommendations"]) == 1


def test_smart_recommendations_checks(client, admin_token):
    student_token, student_id = make_student(client)
    check(client, "GET", "/api/admin/students/999/smart-recommendations", 404, "An unknown student gives 404", None, admin_token, "admin")
    check(client, "GET", f"/api/admin/students/{student_id}/smart-recommendations?limit=0", 400, "limit 0 is rejected", None, admin_token, "admin")
    check(client, "GET", f"/api/admin/students/{student_id}/smart-recommendations", 403, "A student cannot use Smart Match", None, student_token, "student")
