"""Settings for the app. TestConfig is used by the pytest tests."""
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mentor-connect-dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mentor_connect.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_HOURS = 8
    PASSWORD_HASH_METHOD = "pbkdf2:sha256"
    # Which websites may call the API from a browser. "*" means any; on the live site set it to the frontend address.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    # Fill an empty database with sample students, mentors and one match (set LOAD_DEMO_DATA=1)
    LOAD_DEMO_DATA = os.environ.get("LOAD_DEMO_DATA", "0") == "1"


class TestConfig(Config):
    TESTING = True
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:1000"  # fewer rounds so the tests run fast
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
