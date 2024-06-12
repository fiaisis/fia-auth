from unittest.mock import patch, Mock

import pytest

from src.auth import authenticate
from src.exceptions import BadCredentialsError, UOWSError
from src.model import UserCredentials


@patch("requests.post")
def test_authenticate_success(mock_post):
    mock_response = Mock(status_code=201, json=lambda: {"userId": "12345"})
    mock_post.return_value = mock_response

    credentials = UserCredentials(username="valid_user", password="valid_password")

    user = authenticate(credentials)

    assert user.user_number == "12345"

    mock_post.assert_called_once_with(
        "https://devapi.facilities.rl.ac.uk/users-service/v0/sessions",
        json=({"username": "valid_user", "password": "valid_password"},),
        headers={"Content-Type": "application/json"},
    )


@patch("requests.post")
def test_authenticate_bad_credentials(mock_post):
    mock_response = Mock(status_code=401, json=lambda: {})
    mock_post.return_value = mock_response

    credentials = UserCredentials(username="invalid_user", password="invalid_password")

    with pytest.raises(BadCredentialsError) as exc_info:
        authenticate(credentials)

    assert str(exc_info.value) == "Invalid user credentials provided to authenticate with the user office web service."


@patch("requests.post")
def test_authenticate_unexpected_error(mock_post):
    mock_response = Mock(status_code=500, json=lambda: {"error": "Server error"})
    mock_post.return_value = mock_response

    credentials = UserCredentials(username="user", password="password")

    with pytest.raises(UOWSError) as exc_info:
        authenticate(credentials)

    assert "An unexpected error occurred when authenticating with the user office web service" in str(exc_info.value)