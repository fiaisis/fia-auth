# ruff: noqa: D100, D103
import os
from http import HTTPStatus
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from fia_auth.auth import authenticate
from fia_auth.exceptions import BadCredentialsError, UOWSError
from fia_auth.model import UserCredentials


@patch("requests.get")
@patch("requests.post")
def test_authenticate_success(mock_post, mock_get):
    uows_api_key = str(mock.MagicMock())
    os.environ["UOWS_API_KEY"] = uows_api_key
    mock_post_response = Mock(
        status_code=HTTPStatus.CREATED, json=lambda: {"userId": "12345", "displayName": "Mr Cool"}
    )
    mock_get_response = Mock(status_code=HTTPStatus.OK, json=lambda: [{"displayName": "Mr Cool"}])
    mock_post.return_value = mock_post_response
    mock_get.return_value = mock_get_response

    credentials = UserCredentials(username="valid_user", password="valid_password")  # noqa: S106

    user = authenticate(credentials)

    assert user.user_number == "12345"
    assert user.username == "Mr Cool"

    mock_post.assert_called_once_with(
        "https://devapi.facilities.rl.ac.uk/users-service/v1/sessions",
        json={"username": "valid_user", "password": "valid_password"},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    mock_get.assert_called_once_with(
        "https://devapi.facilities.rl.ac.uk/users-service/v1/basic-person-details?userNumbers=12345",
        headers={"Authorization": f"Api-key {uows_api_key}", "Content-Type": "application/json"},
        timeout=30,
    )


@patch("requests.post")
def test_authenticate_bad_credentials(mock_post):
    mock_response = Mock(status_code=HTTPStatus.UNAUTHORIZED, json=lambda: {})
    mock_post.return_value = mock_response

    credentials = UserCredentials(username="invalid_user", password="invalid_password")  # noqa: S106

    with pytest.raises(BadCredentialsError) as exc_info:
        authenticate(credentials)

    assert str(exc_info.value) == "Invalid user credentials provided to authenticate with the user office web service."


@patch("requests.post")
def test_authenticate_unexpected_error(mock_post):
    mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, json=lambda: {"error": "Server error"})
    mock_post.return_value = mock_response

    credentials = UserCredentials(username="user", password="password")  # noqa: S106

    with pytest.raises(UOWSError) as exc_info:
        authenticate(credentials)

    assert "An unexpected error occurred when authenticating with the user office web service" in str(exc_info.value)
