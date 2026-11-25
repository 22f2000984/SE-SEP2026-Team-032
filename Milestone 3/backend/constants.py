"""Fixed lists and rules used across the backend. Change a value here and it changes everywhere."""

TOPICS = [
    "Data Science", "Web Development", "Career Switching", "Interview Preparation",
    "Product Management", "Higher Studies", "Entrepreneurship", "Cloud and DevOps",
]
FORMATS = ["No preference", "Video call", "Phone call", "Messaging"]
DURATIONS = ["Not sure yet", "1 month", "3 months", "6 months"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Students must register with an IITM email (for example name@ds.study.iitm.ac.in). Mentors can use any email.
STUDENT_EMAIL_DOMAIN = "iitm.ac.in"

ROLES = ["student", "mentor", "admin"]
MATCH_STATUSES = ["proposed", "active", "completed", "cancelled"]
MENTOR_STATUSES = ["pending", "verified"]

# Text limits
GOALS_LIMIT = 500
TEXT_LIMIT = 800

# Mentor capacity: how many students a mentor can have at the same time
DEFAULT_CAPACITY = 3
MAX_CAPACITY = 10

# Matching score out of 100: topics 70 + experience 30
TOPIC_WEIGHT = 70
EXPERIENCE_WEIGHT = 30
EXPERIENCE_CAP_YEARS = 10

# What a match may become next (US-C04). The admin moves it; both sides must accept before it becomes active.
MATCH_NEXT = {"proposed": ["active", "cancelled"], "active": ["completed", "cancelled"], "completed": [], "cancelled": []}
ANSWERS = ["accepted", "declined"]
CONCERN_STATUSES = ["open", "resolved"]

# ---- Mentorship Pulse (weekly check-ins) ----
# How many weekly check-ins a match gets, by the duration the student chose
CHECKIN_WEEKS = {"Not sure yet": 4, "1 month": 4, "3 months": 12, "6 months": 24}
CHECKIN_GRACE_DAYS = 2  # a check-in is "due" for this many days after its date, then it is "overdue"
LOW_RATING = 2          # a rating of 2 or less is always flagged for the admin
VERDICTS = ["on track", "watch", "needs attention"]  # from best to worst
REVIEW_STATUSES = ["ok", "open", "reviewed"]
WORRYING_WORDS = ["not responding", "no response", "cancelled", "canceled", "no show", "unhelpful", "rude",
                  "confused", "ignored", "hard to reach", "clash", "stopped"]

# ---- Smart Match ----
SMART_TEXT_WEIGHT = 60   # points from how well the two free-text answers fit
SMART_RULE_WEIGHT = 40   # points from the rule score (topics and experience)
SMART_MAX_KEYWORDS = 5
