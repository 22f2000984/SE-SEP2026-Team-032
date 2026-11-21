"""The sample data used for demos (LOAD_DEMO_DATA=1)."""
from app import create_app
from config import TestConfig
from tests.helpers import auth


class DemoConfig(TestConfig):
    LOAD_DEMO_DATA = True


def test_demo_data_fills_an_empty_database():
    app = create_app(DemoConfig)
    with app.app_context():
        client = app.test_client()
        token = client.post("/api/auth/login", json={"email": "admin@client.test", "password": "demo123"}).get_json()["token"]
        overview = client.get("/api/admin/overview", headers=auth(token)).get_json()
        assert overview["students"] == 3 and overview["mentors"]["total"] == 3 and overview["matches"]["proposed"] == 1
        login = client.post("/api/auth/login", json={"email": "asha@ds.study.iitm.ac.in", "password": "demo123"})
        assert login.status_code == 200


def test_demo_data_is_not_loaded_twice():
    from database import db
    from models import StudentProfile
    from seed import seed_demo
    app = create_app(DemoConfig)
    with app.app_context():
        seed_demo()
        assert StudentProfile.query.count() == 3
