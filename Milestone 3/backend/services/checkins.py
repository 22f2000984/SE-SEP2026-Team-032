"""Weekly check-ins (Mentorship Pulse). One row per week for the student and one for the mentor of an active match."""
from datetime import timedelta

from constants import CHECKIN_WEEKS
from database import db
from models import CheckIn, Match, now
from services.pulse_review import review_check_in
from services.notifications import notify_admins


def weeks_for(duration):
    return CHECKIN_WEEKS.get(duration, CHECKIN_WEEKS["Not sure yet"])


def schedule_check_ins(match):
    """Called when a match becomes active. Creates the rows for every week (only once)."""
    if CheckIn.query.filter_by(match_id=match.id).count() > 0:
        return
    start = match.confirmed_at or now()
    for week in range(1, weeks_for(match.student.expected_duration) + 1):
        due = start + timedelta(days=7 * week)
        for role, profile in (("student", match.student), ("mentor", match.mentor)):
            db.session.add(CheckIn(match_id=match.id, user_id=profile.user_id, by_role=role, week=week, due_at=due))


def save_answer(checkin, rating, comment):
    """Stores the answer, reviews it and tells the admins when it was flagged."""
    checkin.rating = rating
    checkin.comment = (comment or "").strip()
    checkin.submitted_at = now()
    review_check_in(checkin)
    if checkin.review_status == "open":
        notify_admins(f"Mentorship Pulse: week {checkin.week} check-in from {checkin.user.full_name} "
                      f"is marked \"{checkin.review_verdict}\". Please review.", checkin.match_id)


def active_check_ins():
    """Every check-in that belongs to a match that is still active."""
    return (CheckIn.query.join(Match, CheckIn.match_id == Match.id).filter(Match.status == "active")
            .order_by(CheckIn.due_at).all())


def needs_admin(checkin):
    """True for an answer the review flagged, or a check-in nobody answered in time."""
    if checkin.review_status == "open":
        return True
    return checkin.submitted_at is None and checkin.state() == "overdue" and checkin.review_status is None


def flagged_check_ins():
    return [c for c in active_check_ins() if needs_admin(c)]


def mark_reviewed(checkin, note):
    if checkin.review_verdict is None:  # an unanswered check-in has no review yet
        checkin.review_verdict = "needs attention"
        checkin.review_reason = "The check-in was not answered in time."
        checkin.review_source = "rules"
    checkin.review_status = "reviewed"
    checkin.admin_note = (note or "").strip()
