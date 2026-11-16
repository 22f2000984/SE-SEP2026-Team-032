# Mentor Connect backend (Sprint 1, Milestone 3)

Team 032 (Himalayan Coders): Student Mentoring and Career Support Platform.
A small Flask + SQLite backend. It implements the Sprint 1 user stories and is described in `swagger.yaml`.

## Run it

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                     # http://localhost:5001
```

The first start creates `instance/mentor_connect.db`, the eight topics and one admin account
(`admin@client.test` / `demo123`). Students and mentors register through `POST /api/auth/register`.
Open `swagger.yaml` in https://editor.swagger.io to read the API.

## Run the tests

```bash
pytest -v                         # 71 tests; each test uses its own in-memory database
```

After a run, `tests/test_cases.md` holds the test-case table (API, inputs, expected output, actual output, result).

## Folder guide

| File | What it does |
|---|---|
| `app.py` | Creates the app and registers the routes |
| `config.py`, `constants.py` | Settings, and the fixed lists and rules |
| `models.py`, `database.py` | The database tables (same as the ER diagram) |
| `auth_utils.py` | Passwords, login tokens, `login_required` and `role_required` |
| `validators.py` | Input checks that return an error message or `None` |
| `responses.py` | The one error format `{"error": "message"}` |
| `routes/` | One file per area: `auth`, `profiles`, `admin`, `matches` (thin: read input, call a function, return JSON) |
| `services/` | The logic: `matching` (rules and score), `profiles` (saving), `notifications` |
| `seed.py` | Topics and the admin account |
| `swagger.yaml` | The API description with user-story mapping and errors |
| `tests/` | pytest tests |

## How a request flows

`route` (reads the JSON) -> `validators` (checks it) -> `services` (does the work) -> `models` (database) -> JSON answer.
Errors always look like `{"error": "..."}` with the status codes 400, 401, 403, 404 or 409.
