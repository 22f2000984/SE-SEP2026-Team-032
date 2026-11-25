"""Smart Match. Ranks the eligible mentors for one student by reading what the student and the mentors wrote.
Total score (0 to 100) = 60% text fit + 40% rule score (topics and experience, from services/matching.py).
The text fit comes from OpenAI when it is switched on; otherwise from shared keywords (the fallback)."""
import re

from constants import SMART_MAX_KEYWORDS, SMART_RULE_WEIGHT, SMART_TEXT_WEIGHT
from models import MentorProfile
from services.ai import ask_json
from services.matching import eligibility_error, score_pair

STOP_WORDS = set((
    "i a an and are as at be been but by can do for from get has have help how in into is it its me my need needs of on or our "
    "so that the their them then there these this to want wants was we what when which who will with would you your am about "
    "also very much more most like any all some such than too").split())

AI_INSTRUCTIONS = (
    "You help an admin match a student with mentors. For every mentor, judge how well the mentor's text fits what the student "
    "needs. Reply with JSON only: {\"results\": [{\"mentor_id\": 1, \"fit\": 0-100, \"reason\": \"one short sentence\"}]}. "
    "Give one result for every mentor you were sent.")


def stem(word):
    if len(word) > 5:
        return re.sub(r"(ing|ed|es|s)$", "", word)
    return re.sub(r"s$", "", word)


def keywords(text):
    """The meaningful words of a text, as a dictionary from word stem to the word as written."""
    found = {}
    for word in re.findall(r"[a-z]+", (text or "").lower()):
        if len(word) < 3 or word in STOP_WORDS:
            continue
        found.setdefault(stem(word), word)
    return found


def student_text(student):
    return f"{student.needs_text or ''} {student.career_goals or ''}"


def mentor_text(mentor):
    return f"{mentor.skills_text or ''} {mentor.bio or ''} {mentor.qualifications or ''}"


def keyword_fit(student, mentor):
    """Fallback text fit: returns (fit 0-100, reason)."""
    need = keywords(student_text(student))
    offer = keywords(mentor_text(mentor))
    shared = [need[key] for key in need if key in offer]
    base = min(len(need), SMART_MAX_KEYWORDS)
    fit = min(1, len(shared) / base) * 100 if base else 0
    reason = "Both describe: " + ", ".join(shared[:6]) if shared else "The free-text answers share no wording"
    return round(fit), reason


def ai_fits(student, mentors):
    """Asks the AI once for all mentors. Returns {mentor_id: (fit, reason)}; empty when the AI is off or failed."""
    answer = ask_json(AI_INSTRUCTIONS, {
        "student": {"needs": student.needs_text, "goals": student.career_goals,
                    "topics": [t.name for t in student.topics]},
        "mentors": [{"mentor_id": m.id, "bio": m.bio, "skills": m.skills_text, "qualifications": m.qualifications,
                     "topics": [t.name for t in m.topics]} for m in mentors]})
    fits = {}
    if not answer or not isinstance(answer.get("results"), list):
        return fits
    for item in answer["results"]:
        if not isinstance(item, dict):
            continue
        fit = item.get("fit")
        if isinstance(item.get("mentor_id"), int) and isinstance(fit, (int, float)) and not isinstance(fit, bool):
            fits[item["mentor_id"]] = (max(0, min(100, round(fit))), str(item.get("reason") or "")[:300])
    return fits


def smart_recommend(student, limit=3):
    """Returns (results, source). source is 'ai' when at least one score came from the AI, otherwise 'rules'."""
    mentors = [m for m in MentorProfile.query.all() if eligibility_error(student, m) is None]
    fits = ai_fits(student, mentors) if mentors else {}
    results = []
    for mentor in mentors:
        rule = score_pair(student, mentor)
        if mentor.id in fits:
            fit, reason, source = fits[mentor.id][0], fits[mentor.id][1], "ai"
        else:
            fit, reason = keyword_fit(student, mentor)
            source = "rules"
        total = round((SMART_TEXT_WEIGHT * fit + SMART_RULE_WEIGHT * rule["total"]) / 100)
        results.append({"mentor_id": mentor.id, "mentor_name": mentor.user.full_name, "score": total,
                        "text_fit": fit, "rule_score": rule["total"], "source": source,
                        "reasons": [reason] + rule["reasons"]})
    results.sort(key=lambda r: r["score"], reverse=True)
    overall = "ai" if any(r["source"] == "ai" for r in results) else "rules"
    return results[:limit], overall
