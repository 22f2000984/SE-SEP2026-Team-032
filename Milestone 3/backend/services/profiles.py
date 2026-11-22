"""Saving student and mentor profiles (US-S02, US-M02, US-C05). Shared by the user's own routes and the admin routes.
Each save function returns an error message, or None when it worked."""
from database import db
from models import AvailabilitySlot, Topic
from services.matching import places_used
from services.notifications import notify_admins
import validators

STUDENT_FIELDS = ["programme_level", "career_goals", "skills", "needs_text", "mentoring_format",
                  "expected_duration", "preferences", "availability_note"]
MENTOR_FIELDS = ["qualifications", "experience_years", "bio", "skills_text", "max_students"]


def set_topics(profile, names):
    profile.topics = Topic.query.filter(Topic.name.in_(names)).all()


def copy_fields(profile, data, fields):
    for field in fields:
        if field in data:
            setattr(profile, field, data[field].strip() if isinstance(data[field], str) else data[field])


def save_student_profile(profile, data):
    """Fields that are missing from data keep their current value, so a partial update is fine."""
    merged = {**profile.to_dict(), **data}
    error = validators.check_student_profile(merged)
    if error:
        return error
    copy_fields(profile, data, STUDENT_FIELDS)
    if "topics" in data:
        set_topics(profile, data["topics"])
    db.session.commit()
    return None


def save_mentor_profile(profile, data):
    merged = {**profile.to_dict(), **data}
    error = validators.check_mentor_profile(merged, places_used(profile.id))
    if error:
        return error
    copy_fields(profile, data, MENTOR_FIELDS)
    if "topics" in data:
        set_topics(profile, data["topics"])
    db.session.commit()
    return None


def tell_admins_if_complete(mentor, was_complete):
    """When a mentor finishes the profile, the admins are told that the mentor is ready for verification."""
    if mentor.profile_complete and not was_complete and mentor.profile_status == "pending":
        notify_admins(f"{mentor.user.full_name} ({mentor.user.email}) finished their profile and is waiting for verification.")
        db.session.commit()


def add_slot(mentor, data):
    """Returns (slot, error)."""
    error = validators.check_slot(data)
    if error:
        return None, error
    slot = AvailabilitySlot(mentor_id=mentor.id, day_of_week=data["day_of_week"],
                            start_time=data["start_time"], end_time=data["end_time"])
    db.session.add(slot)
    db.session.commit()
    return slot, None


def remove_slot(mentor, slot_id):
    """Returns True if the slot belonged to this mentor and was removed."""
    slot = AvailabilitySlot.query.filter_by(id=slot_id, mentor_id=mentor.id).first()
    if slot is None:
        return False
    db.session.delete(slot)
    db.session.commit()
    return True
