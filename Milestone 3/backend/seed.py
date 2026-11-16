"""Creates the fixed topics and the admin account the first time the app starts.
The admin is the client (IIC team): it is not created through registration."""
from auth_utils import hash_password
from constants import TOPICS
from database import db
from models import Topic, User

ADMIN_EMAIL = "admin@client.test"
ADMIN_PASSWORD = "demo123"


def seed_basics():
    for name in TOPICS:
        if not Topic.query.filter_by(name=name).first():
            db.session.add(Topic(name=name))
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        db.session.add(User(email=ADMIN_EMAIL, password_hash=hash_password(ADMIN_PASSWORD), full_name="Admin", role="admin"))
    db.session.commit()
