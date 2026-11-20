"""Registration and login (US-S01, US-M01)."""
from tests.helpers import check, register

NEW_STUDENT = {"full_name": "Asha Verma", "email": "asha@ds.study.iitm.ac.in", "password": "secret1", "role": "student"}


def test_register_student(client):
    check(client, "POST", "/api/auth/register", 201, "A student registers with valid details", NEW_STUDENT, contains='"role": "student"')


def test_register_student_needs_iitm_email(client):
    body = {**NEW_STUDENT, "email": "asha@gmail.com"}
    check(client, "POST", "/api/auth/register", 400, "A student with a non-IITM email is rejected", body, contains="IITM email")


def test_register_student_lookalike_domain(client):
    body = {**NEW_STUDENT, "email": "asha@notiitm.ac.in"}
    check(client, "POST", "/api/auth/register", 400, "A look-alike domain is not accepted as IITM", body, contains="IITM email")


def test_register_student_main_iitm_domain(client):
    body = {**NEW_STUDENT, "email": "asha@iitm.ac.in"}
    check(client, "POST", "/api/auth/register", 201, "A student with an @iitm.ac.in email registers", body)


def test_register_mentor_any_email(client):
    body = {**NEW_STUDENT, "email": "meera@gmail.com", "role": "mentor"}
    check(client, "POST", "/api/auth/register", 201, "A mentor can register with any email", body, contains='"role": "mentor"')


def test_register_mentor(client):
    body = {**NEW_STUDENT, "email": "meera@mentor.test", "role": "mentor"}
    check(client, "POST", "/api/auth/register", 201, "A mentor registers with valid details", body, contains='"role": "mentor"')


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json=NEW_STUDENT)
    check(client, "POST", "/api/auth/register", 409, "The same email cannot register twice", NEW_STUDENT, contains="already registered")


def test_register_email_is_not_case_sensitive(client):
    client.post("/api/auth/register", json=NEW_STUDENT)
    body = {**NEW_STUDENT, "email": "ASHA@ds.study.iitm.ac.in"}
    check(client, "POST", "/api/auth/register", 409, "The same email in capital letters is still a duplicate", body)


def test_register_missing_name(client):
    check(client, "POST", "/api/auth/register", 400, "Registration without a name is rejected", {**NEW_STUDENT, "full_name": ""}, contains="Full name")


def test_register_bad_email(client):
    check(client, "POST", "/api/auth/register", 400, "Registration with an invalid email is rejected", {**NEW_STUDENT, "email": "not-an-email"}, contains="valid email")


def test_register_short_password(client):
    check(client, "POST", "/api/auth/register", 400, "A password under 6 characters is rejected", {**NEW_STUDENT, "password": "123"}, contains="Password")


def test_register_cannot_create_admin(client):
    check(client, "POST", "/api/auth/register", 400, "Nobody can register as admin", {**NEW_STUDENT, "role": "admin"}, contains="Role")


def test_register_without_json_body(client):
    check(client, "POST", "/api/auth/register", 400, "A request with no body is rejected")


def test_login_success(client):
    client.post("/api/auth/register", json=NEW_STUDENT)
    body = check(client, "POST", "/api/auth/login", 200, "Login with the right email and password",
                 {"email": "asha@ds.study.iitm.ac.in", "password": "secret1"}, contains="token")
    assert body["user"]["role"] == "student"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json=NEW_STUDENT)
    check(client, "POST", "/api/auth/login", 401, "Login with a wrong password",
          {"email": "asha@ds.study.iitm.ac.in", "password": "wrong-pass"}, contains="Invalid email or password")


def test_login_unknown_email(client):
    check(client, "POST", "/api/auth/login", 401, "Login with an email that is not registered",
          {"email": "nobody@ds.study.iitm.ac.in", "password": "secret1"}, contains="Invalid email or password")


def test_me_with_token(client):
    token = register(client, "asha@ds.study.iitm.ac.in", "student")
    check(client, "GET", "/api/auth/me", 200, "A logged-in user asks who they are", token=token, role="student", contains="asha@ds.study.iitm.ac.in")


def test_me_without_token(client):
    check(client, "GET", "/api/auth/me", 401, "Asking who I am without logging in", contains="log in")


def test_me_with_bad_token(client):
    check(client, "GET", "/api/auth/me", 401, "A made-up token is not accepted", token="not-a-real-token")
