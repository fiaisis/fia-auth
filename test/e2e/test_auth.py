from http import HTTPStatus
from unittest.mock import Mock, patch

import jwt
from starlette.testclient import TestClient

from fia_auth.fia_auth import app
from fia_auth.model import User
from fia_auth.tokens import generate_access_token, generate_refresh_token

client = TestClient(app)


@patch("fia_auth.auth.requests")
def test_successful_login(mock_requests):
    mock_response = Mock()
    mock_requests.post.return_value = mock_response

    mock_response.status_code = HTTPStatus.CREATED
    mock_response.json.return_value = {"userId": 1234}
    response = client.post("/api/jwt/authenticate", json={"username": "foo", "password": "foo"})
    assert response.json()["token"].startswith("ey")
    assert response.cookies["refresh_token"].startswith("ey")


@patch("fia_auth.auth.requests.post")
def test_unsuccessful_login(mock_post):
    mock_response = Mock()
    mock_post.return_value = mock_response

    mock_response.status_code = HTTPStatus.UNAUTHORIZED

    response = client.post("/api/jwt/authenticate", json={"username": "foo", "password": "foo"})
    assert response.status_code == HTTPStatus.FORBIDDEN


@patch("fia_auth.auth.requests.post")
def test_unsuccessful_login_uows_failure(mock_post):
    mock_response = Mock()
    mock_post.return_value = mock_response

    mock_response.status_code = HTTPStatus.UNAUTHORIZED.INTERNAL_SERVER_ERROR

    response = client.post("/api/jwt/authenticate", json={"username": "foo", "password": "foo"})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_verify_success():
    user = User(123)
    access_token = generate_access_token(user)
    response = client.post("/api/jwt/checkToken", json={"token": access_token.jwt})

    assert response.status_code == HTTPStatus.OK


def test_verify_fail_badly_formed_token():
    response = client.post("/api/jwt/checkToken", json={"token": "foo"})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_verify_fail_bad_signature():
    response = client.post("/api/jwt/checkToken", json={"token": jwt.encode({"foo": "bar"}, key="foo")})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_token_refresh_success():
    user = User(123)
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token()
    response = client.post(
        "/api/jwt/refresh", json={"token": access_token.jwt}, cookies={"refresh_token": refresh_token.jwt}
    )
    assert response.json()["token"].startswith("ey")


def test_token_refresh_no_refresh_token_given():
    user = User(123)
    access_token = generate_access_token(user)
    response = client.post(
        "/api/jwt/refresh",
        json={"token": access_token.jwt},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_token_refresh_expired_refresh_token():
    user = User(123)
    access_token = generate_access_token(user)
    refresh_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTgwMjEyNDB9.iHITGf2RyX_49pY7Xy8xdutYE4Pc6k9mfKWQjxCKgOk"  # noqa: S105
    )
    response = client.post(
        "/api/jwt/refresh", json={"token": access_token.jwt}, cookies={"refresh_token": refresh_token}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
