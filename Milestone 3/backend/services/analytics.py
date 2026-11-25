"""Numbers for the admin dashboard (US-C07). Everything is counted from the tables; nothing is stored separately."""
from models import Feedback, MentorProfile
from services.checkins import active_check_ins
from services.matching import places_max, places_used


def percent(part, whole):
    return round(100 * part / whole) if whole else 0


def pulse_summary():
    """How the weekly check-ins of active matches are going. Only check-ins that are due or older count."""
    live = [c for c in active_check_ins() if c.state() != "upcoming"]
    answered = [c for c in live if c.submitted_at]

    def count(verdict):
        return sum(1 for c in answered if c.review_verdict == verdict)

    return {"asked": len(live), "answered": len(answered), "response_rate": percent(len(answered), len(live)),
            "on_track": count("on track"), "watch": count("watch"), "needs_attention": count("needs attention"),
            "unanswered": len(live) - len(answered)}


def feedback_summary():
    rows = Feedback.query.all()
    average = round(sum(r.rating for r in rows) / len(rows), 1) if rows else None
    return {"total": len(rows), "average": average,
            "counts": [{"rating": star, "count": sum(1 for r in rows if r.rating == star)} for star in (5, 4, 3, 2, 1)]}


def capacity_summary():
    """Places in use across the verified mentors, and one row per mentor."""
    rows = [{"mentor_id": m.id, "mentor_name": m.user.full_name, "used": places_used(m.id), "max": places_max(m)}
            for m in MentorProfile.query.filter_by(profile_status="verified").all()]
    used = sum(r["used"] for r in rows)
    places = sum(r["max"] for r in rows)
    return {"rows": rows, "used": used, "places": places, "percent": percent(used, places)}
