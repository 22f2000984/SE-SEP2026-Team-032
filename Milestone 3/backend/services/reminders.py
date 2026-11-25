"""The weekly reminder job. A scheduler (GitHub Actions) calls POST /api/jobs/reminders; this does the work."""
from models import now
from services.checkins import active_check_ins
from services.emailer import send_email


def send_due_reminders():
    """Emails everyone who has a check-in that is due or overdue and has not been reminded yet. Returns how many were sent."""
    sent = 0
    for checkin in active_check_ins():
        if checkin.reminder_sent_at or checkin.state() not in ("due", "overdue"):
            continue
        send_email(checkin.user, "Check-in reminder",
                   f"Your week {checkin.week} check-in is ready. Please answer it on your Check-ins page.", checkin.match_id)
        checkin.reminder_sent_at = now()
        sent += 1
    return sent
