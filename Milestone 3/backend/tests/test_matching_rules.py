"""Unit tests for the matching rules, without going through the API (US-C02)."""
from database import db
from models import Match
from services.matching import eligibility_error, places_used, recommend, score_pair
from tests.helpers import MENTOR_PROFILE, auth, make_mentor, make_student
from models import MentorProfile, StudentProfile


def get(model, row_id):
    return db.session.get(model, row_id)


def test_score_full_topics_and_ten_years(client, admin_token):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)  # 12 years counts as 10, both topics shared
    score = score_pair(get(StudentProfile, student_id), get(MentorProfile, mentor_id))
    assert score["total"] == 100
    assert "Shared topics: Career Switching, Data Science" in score["reasons"][0]


def test_score_half_topics_and_five_years(client, admin_token):
    _, student_id = make_student(client)
    profile = {**MENTOR_PROFILE, "topics": ["Data Science"], "experience_years": 5}
    _, mentor_id = make_mentor(client, admin_token, profile=profile)
    score = score_pair(get(StudentProfile, student_id), get(MentorProfile, mentor_id))
    assert score["total"] == 35 + 15  # half of 70 and half of 30


def test_score_no_shared_topics(client, admin_token):
    _, student_id = make_student(client)
    profile = {**MENTOR_PROFILE, "topics": ["Cloud and DevOps"], "experience_years": 0}
    _, mentor_id = make_mentor(client, admin_token, profile=profile)
    score = score_pair(get(StudentProfile, student_id), get(MentorProfile, mentor_id))
    assert score["total"] == 0
    assert score["reasons"][0] == "No shared topics"


def test_eligibility_rules(client, admin_token):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token, verified=False)
    student, mentor = get(StudentProfile, student_id), get(MentorProfile, mentor_id)
    assert eligibility_error(student, mentor) == "The mentor is not verified yet."
    mentor.profile_status = "verified"
    assert eligibility_error(student, mentor) is None


def test_cancelled_matches_free_the_place(client, admin_token):
    _, student_id = make_student(client)
    _, mentor_id = make_mentor(client, admin_token)
    client.post("/api/admin/matches", json={"student_id": student_id, "mentor_id": mentor_id}, headers=auth(admin_token))
    assert places_used(mentor_id) == 1
    Match.query.first().status = "cancelled"
    db.session.commit()
    assert places_used(mentor_id) == 0
    assert len(recommend(get(StudentProfile, student_id))) == 1
