"""Input checks. Each function returns an error message, or None when the input is fine."""
from constants import (DURATIONS, FORMATS, GOALS_LIMIT, MAX_CAPACITY, MENTOR_STATUSES, TEXT_LIMIT, WEEKDAYS)
from models import Topic


def is_text(value):
    return isinstance(value, str) and value.strip() != ""


def not_text(data, fields):
    """Returns the first of these fields that is present but is not text (for example a number or a list)."""
    for field in fields:
        if data.get(field) is not None and not isinstance(data[field], str):
            return field
    return None


def check_register(data):
    if not is_text(data.get("full_name")):
        return "Full name is required."
    email = data.get("email")
    if not is_text(email) or "@" not in email or "." not in email.split("@")[-1]:
        return "A valid email is required."
    password = data.get("password")
    if not isinstance(password, str) or len(password) < 6:
        return "Password must be at least 6 characters."
    if data.get("role") not in ("student", "mentor"):
        return "Role must be 'student' or 'mentor'."
    return None


def check_topics(names):
    """names must be a non-empty list of topic names that exist."""
    if not isinstance(names, list) or not names:
        return "Choose at least one topic."
    known = {t.name for t in Topic.query.all()}
    unknown = [n for n in names if n not in known]
    if unknown:
        return "Unknown topic: " + ", ".join(str(n) for n in unknown)
    return None


def check_student_profile(data):
    bad = not_text(data, ["programme_level", "career_goals", "skills", "needs_text", "mentoring_format",
                          "expected_duration", "preferences", "availability_note"])
    if bad:
        return f"{bad} must be text."
    if not is_text(data.get("programme_level")) or not is_text(data.get("career_goals")):
        return "Programme level and career goals are required."
    if len(data["career_goals"]) > GOALS_LIMIT:
        return f"Career goals must be {GOALS_LIMIT} characters or fewer."
    if len(data.get("needs_text") or "") > TEXT_LIMIT:
        return f"Needs text must be {TEXT_LIMIT} characters or fewer."
    if data.get("mentoring_format") not in FORMATS:
        return "Mentoring format must be one of: " + ", ".join(FORMATS)
    if data.get("expected_duration") not in DURATIONS:
        return "Expected duration must be one of: " + ", ".join(DURATIONS)
    return check_topics(data.get("topics"))


def check_mentor_profile(data, places_in_use=0):
    bad = not_text(data, ["qualifications", "bio", "skills_text"])
    if bad:
        return f"{bad} must be text."
    if not is_text(data.get("qualifications")):
        return "Qualifications are required."
    years = data.get("experience_years")
    if not isinstance(years, int) or isinstance(years, bool) or years < 0 or years > 60:
        return "Experience must be a whole number of years from 0 to 60."
    if len(data.get("skills_text") or "") > TEXT_LIMIT:
        return f"Skills text must be {TEXT_LIMIT} characters or fewer."
    capacity = data.get("max_students")
    if not isinstance(capacity, int) or isinstance(capacity, bool) or not 1 <= capacity <= MAX_CAPACITY:
        return f"Maximum students must be a whole number from 1 to {MAX_CAPACITY}."
    if capacity < places_in_use:
        return f"This mentor already has {places_in_use} open matches, so the maximum cannot be lower."
    return check_topics(data.get("topics"))


def check_slot(data):
    if data.get("day_of_week") not in WEEKDAYS:
        return "Day must be one of: " + ", ".join(WEEKDAYS)
    start, end = data.get("start_time"), data.get("end_time")
    if not is_text(start) or not is_text(end) or len(start) != 5 or len(end) != 5:
        return "Start and end time must look like 18:00."
    if end <= start:
        return "End time must be after start time."
    return None


def check_mentor_status(value):
    if value not in MENTOR_STATUSES:
        return "Status must be one of: " + ", ".join(MENTOR_STATUSES)
    return None
