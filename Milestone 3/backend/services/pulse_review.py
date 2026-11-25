"""Mentorship Pulse review (US-C07 health of a mentorship). Reads one check-in answer and decides whether the admin must look.
It only flags. It never changes a match. The rules always run; the AI (if switched on) can only make the verdict worse, never better."""
from constants import LOW_RATING, VERDICTS, WORRYING_WORDS
from services.ai import ask_json

AI_INSTRUCTIONS = (
    "You review one weekly check-in about a mentoring relationship between a student and a mentor. "
    "Reply with JSON only: {\"verdict\": \"on track\" | \"watch\" | \"needs attention\", \"reason\": \"one short sentence\"}. "
    "Use 'needs attention' for conflict, no contact, disrespect or a very unhappy answer; 'watch' for mild worry; "
    "otherwise 'on track'.")


def rule_review(rating, comment):
    """Returns (level, reasons). level 0 = on track, 1 = watch, 2 = needs attention."""
    text = (comment or "").lower()
    words_found = [word for word in WORRYING_WORDS if word in text]
    level = 0
    reasons = []
    if rating <= LOW_RATING:
        level = 2
        reasons.append(f"The rating of {rating}/5 is low")
    elif rating == 3:
        level = 1
        reasons.append("The rating of 3/5 is middling")
    if words_found:
        level = max(level, 1)
        reasons.append("The comment mentions: " + ", ".join(words_found))
    return level, reasons


def review_check_in(checkin):
    """Fills in the review fields of an answered check-in."""
    level, reasons = rule_review(checkin.rating, checkin.comment)
    reason = ". ".join(reasons) + "." if reasons else "The rating is good and the comment shows no worry."
    source = "rules"

    answer = ask_json(AI_INSTRUCTIONS, {"rating": checkin.rating, "comment": checkin.comment, "week": checkin.week,
                                         "written_by": checkin.by_role})
    if answer and answer.get("verdict") in VERDICTS:
        ai_level = VERDICTS.index(answer["verdict"])
        if ai_level >= level:  # the AI may only raise the level
            level = ai_level
            reason = str(answer.get("reason") or reason)[:300]
            source = "ai"

    checkin.review_verdict = VERDICTS[level]
    checkin.review_reason = reason
    checkin.review_source = source
    checkin.review_status = "open" if level > 0 else "ok"
