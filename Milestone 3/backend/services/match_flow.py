"""What happens to a match after it is proposed (US-C03, US-C04).
Both sides answer. The admin confirms the match only when both accepted, or cancels it. Each function returns an
error message, or None when it worked. The route commits the change."""
from constants import MATCH_NEXT
from database import db
from models import MatchStatusLog, now
from services.notifications import notify, notify_admins


def both_accepted(match):
    return match.mentor_response == "accepted" and match.student_response == "accepted"


def record_answer(match, who, answer):
    """who is 'mentor' or 'student'; answer is 'accepted' or 'declined'."""
    if match.status != "proposed":
        return "This match is no longer waiting for an answer."
    if getattr(match, who + "_response") != "pending":
        return "You have already answered this proposal."
    setattr(match, who + "_response", answer)
    setattr(match, who + "_responded_at", now())
    names = f"{match.student.user.full_name} / {match.mentor.user.full_name}"
    person = match.student.user.full_name if who == "student" else match.mentor.user.full_name
    notify_admins(f"{person} ({who}) {answer} the proposed match {names}.", match.id)
    if both_accepted(match):
        notify_admins(f"Both accepted: {names} is ready for you to confirm.", match.id)
    return None


def change_status(match, new_status, admin):
    """The admin moves the match to its next status."""
    if new_status not in MATCH_NEXT[match.status]:
        return f"A {match.status} match cannot become {new_status}."
    if match.status == "proposed" and new_status == "active" and not both_accepted(match):
        return "Both the mentor and the student must accept before the match can be confirmed."
    db.session.add(MatchStatusLog(match_id=match.id, old_status=match.status, new_status=new_status, changed_by=admin.id))
    match.status = new_status
    if new_status == "active":
        match.confirmed_at = now()
    student, mentor = match.student, match.mentor
    notify(student.user_id, f"Your mentoring match with {mentor.user.full_name} is now {new_status}.", match.id)
    notify(mentor.user_id, f"Your match with {student.user.full_name} is now {new_status}.", match.id)
    notify_admins(f"Match {student.user.full_name} / {mentor.user.full_name} is now {new_status}.", match.id)
    return None
