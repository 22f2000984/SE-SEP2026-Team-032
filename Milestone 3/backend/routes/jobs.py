"""Routes for scheduled jobs. A scheduler (GitHub Actions cron) calls them with the secret in the X-Job-Secret header."""
from flask import Blueprint, current_app, jsonify, request

from database import db
from responses import error
from services.reminders import send_due_reminders

bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@bp.post("/reminders")
def reminders():
    """Sends the reminder email for every check-in that is due and not reminded yet."""
    secret = current_app.config["JOBS_SECRET"]
    if not secret:
        return error("The scheduled job is not switched on (JOBS_SECRET is not set).", 503)
    if request.headers.get("X-Job-Secret") != secret:
        return error("Wrong or missing job secret.", 403)
    sent = send_due_reminders()
    db.session.commit()
    return jsonify({"reminders_sent": sent})
