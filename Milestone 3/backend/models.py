"""Database tables. Each table is a small class with a to_dict() that gives the JSON the API returns.
The tables follow the ER diagram in the Milestone 2 report."""
from datetime import datetime

from constants import DEFAULT_CAPACITY
from database import db


def now():
    return datetime.utcnow()


def to_text(moment):
    return moment.isoformat() if moment else None


# Many-to-many links between profiles and topics
student_topic = db.Table(
    "student_topic",
    db.Column("student_id", db.Integer, db.ForeignKey("student_profile.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topic.id"), primary_key=True),
)
mentor_topic = db.Table(
    "mentor_topic",
    db.Column("mentor_id", db.Integer, db.ForeignKey("mentor_profile.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topic.id"), primary_key=True),
)


class Topic(db.Model):
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | mentor | admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "full_name": self.full_name, "role": self.role}


class StudentProfile(db.Model):
    __tablename__ = "student_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    programme_level = db.Column(db.String(60), default="")
    career_goals = db.Column(db.Text, default="")
    skills = db.Column(db.Text, default="")
    needs_text = db.Column(db.Text, default="")
    mentoring_format = db.Column(db.String(40), default="No preference")
    expected_duration = db.Column(db.String(40), default="Not sure yet")
    preferences = db.Column(db.Text, default="")
    availability_note = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=now, onupdate=now)

    user = db.relationship("User")
    topics = db.relationship("Topic", secondary=student_topic)

    def to_dict(self):
        return {
            "student_id": self.id, "user_id": self.user_id, "full_name": self.user.full_name, "email": self.user.email,
            "programme_level": self.programme_level, "career_goals": self.career_goals, "skills": self.skills,
            "needs_text": self.needs_text, "mentoring_format": self.mentoring_format,
            "expected_duration": self.expected_duration, "preferences": self.preferences,
            "availability_note": self.availability_note, "topics": [t.name for t in self.topics],
            "updated_at": to_text(self.updated_at),
        }


class MentorProfile(db.Model):
    __tablename__ = "mentor_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    qualifications = db.Column(db.String(200), default="")
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, default="")
    skills_text = db.Column(db.Text, default="")
    profile_status = db.Column(db.String(20), default="pending")  # pending | verified
    max_students = db.Column(db.Integer, default=DEFAULT_CAPACITY)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now)

    user = db.relationship("User")
    topics = db.relationship("Topic", secondary=mentor_topic)
    slots = db.relationship("AvailabilitySlot", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "mentor_id": self.id, "user_id": self.user_id, "full_name": self.user.full_name, "email": self.user.email,
            "qualifications": self.qualifications, "experience_years": self.experience_years, "bio": self.bio,
            "skills_text": self.skills_text, "profile_status": self.profile_status, "max_students": self.max_students,
            "topics": [t.name for t in self.topics], "availability": [s.to_dict() for s in self.slots],
            "updated_at": to_text(self.updated_at),
        }


class AvailabilitySlot(db.Model):
    __tablename__ = "availability_slot"
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False)
    day_of_week = db.Column(db.String(12), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # "18:00"
    end_time = db.Column(db.String(5), nullable=False)

    def to_dict(self):
        return {"slot_id": self.id, "day_of_week": self.day_of_week, "start_time": self.start_time, "end_time": self.end_time}


class Match(db.Model):
    __tablename__ = "match"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False)
    proposed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="proposed")  # proposed | active | completed | cancelled
    mentor_response = db.Column(db.String(20), default="pending")
    student_response = db.Column(db.String(20), default="pending")
    match_score = db.Column(db.Integer, default=0)
    score_reasons = db.Column(db.Text, default="")
    notes = db.Column(db.Text, default="")
    proposed_at = db.Column(db.DateTime, default=now)
    confirmed_at = db.Column(db.DateTime)

    student = db.relationship("StudentProfile")
    mentor = db.relationship("MentorProfile")

    def to_dict(self):
        return {
            "match_id": self.id, "student_id": self.student_id, "student_name": self.student.user.full_name,
            "mentor_id": self.mentor_id, "mentor_name": self.mentor.user.full_name, "status": self.status,
            "mentor_response": self.mentor_response, "student_response": self.student_response,
            "match_score": self.match_score, "score_reasons": self.score_reasons, "notes": self.notes,
            "proposed_at": to_text(self.proposed_at), "confirmed_at": to_text(self.confirmed_at),
        }


class MatchStatusLog(db.Model):
    __tablename__ = "match_status_log"
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    changed_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    changed_at = db.Column(db.DateTime, default=now)


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {"notification_id": self.id, "message": self.message, "is_read": self.is_read, "sent_at": to_text(self.sent_at)}
