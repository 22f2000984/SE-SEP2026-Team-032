"""Readiness (US-S07 to US-S11): how ready a student's profile is for the admin to propose a mentor."""

CHECKS = [
    ("programme_level", "Programme level"),
    ("career_goals", "Career goals"),
    ("topics", "At least one topic"),
    ("skills", "Skills"),
    ("needs_text", "What you need from a mentor"),
    ("availability_note", "When you are available"),
]


def readiness(student):
    """Returns {'items': [...], 'percent': 0-100, 'ready': bool}. 'ready' needs goals, level and a topic."""
    items = []
    for field, label in CHECKS:
        value = [t.name for t in student.topics] if field == "topics" else getattr(student, field)
        items.append({"field": field, "label": label, "done": bool(value)})
    done = sum(1 for item in items if item["done"])
    required = {item["field"]: item["done"] for item in items}
    return {
        "items": items,
        "percent": round(100 * done / len(items)),
        "ready": required["programme_level"] and required["career_goals"] and required["topics"],
        "looking_for_mentor": student.looking_for_mentor,
    }
