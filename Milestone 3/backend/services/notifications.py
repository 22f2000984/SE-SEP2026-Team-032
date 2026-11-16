"""Notifications are rows in the database. Emails come in Sprint 2."""
from database import db
from models import Notification


def notify(user_id, message, match_id=None):
    db.session.add(Notification(user_id=user_id, message=message, match_id=match_id))
