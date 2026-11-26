"""Settings for the app. TestConfig is used by the pytest tests."""
import os

try:  # a local .env file (not in git) can hold DATABASE_URL and the API keys
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def database_url():
    """DATABASE_URL as given by Supabase or Render. SQLAlchemy wants 'postgresql://', and Supabase needs SSL."""
    url = os.environ.get("DATABASE_URL") or "sqlite:///mentor_connect.db"  # an empty value also means SQLite
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql") and "sslmode" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "mentor-connect-dev-secret-key-change-in-production"
    # Password of the admin account created on the first start. Set your own on the live site.
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # reconnect if the database closed an idle connection
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_HOURS = 8
    PASSWORD_HASH_METHOD = "pbkdf2:sha256"
    # Which websites may call the API from a browser. "*" means any; on the live site set it to the frontend address.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    # Fill an empty database with sample students, mentors and one match (set LOAD_DEMO_DATA=1)
    LOAD_DEMO_DATA = os.environ.get("LOAD_DEMO_DATA", "0") == "1"

    # OpenAI (Smart Match and Pulse review). Leave the key empty and the app uses its simple rules instead.
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    # Brevo (emails). Leave the key empty and emails are only saved in the email log and as notifications.
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "")  # a sender address you verified in Brevo
    EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME") or "Mentor Connect"
    # The scheduled job (GitHub Actions) sends this secret in the X-Job-Secret header. Empty means the job is switched off.
    JOBS_SECRET = os.environ.get("JOBS_SECRET", "")


class TestConfig(Config):
    TESTING = True
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:1000"  # fewer rounds so the tests run fast
    OPENAI_API_KEY = ""   # the tests never call OpenAI or Brevo
    BREVO_API_KEY = ""
    JOBS_SECRET = "test-job-secret"
    ADMIN_PASSWORD = ""   # the tests use the default admin password
    LOAD_DEMO_DATA = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
