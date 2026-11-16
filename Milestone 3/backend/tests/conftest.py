"""Shared pytest fixtures. Every test gets a fresh in-memory database."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # lets the tests import the backend modules

from app import create_app  # noqa: E402
from config import TestConfig  # noqa: E402
from seed import ADMIN_EMAIL, ADMIN_PASSWORD  # noqa: E402
from tests import helpers  # noqa: E402


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        yield app.test_client()


@pytest.fixture
def admin_token(client):
    response = client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    return response.get_json()["token"]


def pytest_sessionfinish(session, exitstatus):
    """Writes the test-case table (API, inputs, expected output, actual output, result) after the run."""
    if not helpers.CASES:
        return
    path = os.path.join(os.path.dirname(__file__), "test_cases.md")
    rows = ["| # | API being tested | Test case | Inputs | Expected output | Actual output | Result |",
            "|---|---|---|---|---|---|---|"]
    for number, c in enumerate(helpers.CASES, start=1):
        cells = [c["api"], c["case"], c["inputs"], c["expected"], c["actual"], c["result"]]
        rows.append(f"| {number} | " + " | ".join(cell.replace("|", "/") for cell in cells) + " |")
    passed = sum(c["result"] == "Success" for c in helpers.CASES)
    with open(path, "w") as out:
        out.write(f"# Test cases\n\n{passed} of {len(helpers.CASES)} test cases passed.\n\n" + "\n".join(rows) + "\n")
