"""Marking notifications as read. (Listing them is GET /api/notifications in routes/matches.py.)"""
from flask import Blueprint, g, jsonify

from auth_utils import login_required
from database import db
from models import Notification
from responses import error

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@bp.patch("/<int:notification_id>/read")
@login_required
def mark_read(notification_id):
    row = db.session.get(Notification, notification_id)
    if row is None or row.user_id != g.user.id:
        return error("Notification not found.", 404)
    row.is_read = True
    db.session.commit()
    return jsonify({"notification": row.to_dict()})


@bp.post("/read-all")
@login_required
def mark_all_read():
    rows = Notification.query.filter_by(user_id=g.user.id, is_read=False).all()
    for row in rows:
        row.is_read = True
    db.session.commit()
    return jsonify({"marked": len(rows)})
