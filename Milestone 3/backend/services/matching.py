"""Matching rules (US-C02). Plain functions that read the database and return results.
The rules are the same as the frontend prototype: a mentor is eligible when verified, with a free place,
and the student has no open match. The score is out of 100: topics 70 + experience 30."""
from constants import (DEFAULT_CAPACITY, EXPERIENCE_CAP_YEARS, EXPERIENCE_WEIGHT, TOPIC_WEIGHT)
from models import Match, MentorProfile, StudentProfile

OPEN = ("proposed", "active")


def places_used(mentor_id):
    return Match.query.filter(Match.mentor_id == mentor_id, Match.status.in_(OPEN)).count()


def places_max(mentor):
    return mentor.max_students or DEFAULT_CAPACITY


def has_open_match(student_id):
    return Match.query.filter(Match.student_id == student_id, Match.status.in_(OPEN)).count() > 0


def eligibility_error(student, mentor):
    """Returns the reason this pair may not be proposed, or None when it may."""
    if mentor.profile_status != "verified":
        return "The mentor is not verified yet."
    if places_used(mentor.id) >= places_max(mentor):
        return "This mentor has no free places."
    if has_open_match(student.id):
        return "This student already has an open match."
    if not student.looking_for_mentor:
        return "This student is not looking for a mentor right now."
    return None


def score_pair(student, mentor):
    """Returns {'total': 0-100, 'reasons': [...]} for one student and one mentor."""
    wanted = {t.name for t in student.topics}
    shared = sorted(wanted & {t.name for t in mentor.topics})
    topic_points = round(TOPIC_WEIGHT * len(shared) / len(wanted)) if wanted else 0
    years = mentor.experience_years or 0
    experience_points = round(EXPERIENCE_WEIGHT * min(years, EXPERIENCE_CAP_YEARS) / EXPERIENCE_CAP_YEARS)
    free = max(0, places_max(mentor) - places_used(mentor.id))
    reasons = [
        "Shared topics: " + ", ".join(shared) if shared else "No shared topics",
        f"{years} years of experience",
        f"{free} of {places_max(mentor)} places free",
    ]
    return {"total": topic_points + experience_points, "reasons": reasons}


def recommend(student, limit=3):
    """The best eligible mentors for one student, highest score first."""
    results = []
    for mentor in MentorProfile.query.all():
        if eligibility_error(student, mentor) is None:
            score = score_pair(student, mentor)
            results.append({"mentor_id": mentor.id, "mentor_name": mentor.user.full_name, "score": score["total"],
                            "reasons": score["reasons"]})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]


def waiting_students():
    """Students who are looking for a mentor and have no proposed or active match."""
    return [s for s in StudentProfile.query.all() if s.looking_for_mentor and not has_open_match(s.id)]
