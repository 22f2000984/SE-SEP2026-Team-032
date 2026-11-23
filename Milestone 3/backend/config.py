"""Settings for the app. TestConfig is used by the pytest tests."""
import os

try:  # a local .env file (not in git) can hold DATABASE_URL and the API keys
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def database_url():
    """DATABASE_URL as given by Supabase or Render. SQLAlchemy wants 'postgresql://', and Supabase needs SSL."""
    url = os.environ.get("DATABASE_URL", "sqlite:///mentor_connect.db")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql") and "sslmode" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mentor-connect-dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # reconnect if the database closed an idle connection
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
