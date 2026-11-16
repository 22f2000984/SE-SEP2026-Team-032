"""Fixed lists and rules used across the backend. Change a value here and it changes everywhere."""

TOPICS = [
    "Data Science", "Web Development", "Career Switching", "Interview Preparation",
    "Product Management", "Higher Studies", "Entrepreneurship", "Cloud and DevOps",
]
FORMATS = ["No preference", "Video call", "Phone call", "Messaging"]
DURATIONS = ["Not sure yet", "1 month", "3 months", "6 months"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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
