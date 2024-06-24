from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from fia_auth.exceptions import BadJWTError
from fia_auth.model import User
from fia_auth.tokens import AccessToken, RefreshToken, Token, generate_access_token


@patch("jwt.decode")
@patch("fia_auth.tokens.logger")
def test_verify_success(mock_logger, mock_decode):
    token_instance = Token()
    token_instance.jwt = "valid_jwt_token"
    mock_decode.return_value = {"some": "payload"}

    token_instance.verify()

    mock_decode.assert_called_once_with(
        "valid_jwt_token",
        "shh",
        algorithms=["HS256"],
        options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
    )
    mock_logger.warning.assert_not_called()


@patch("jwt.decode")
@patch("fia_auth.tokens.logger")
def test_verify_invalid_signature(mock_logger, mock_decode):
    token_instance = Token()
    token_instance.jwt = "bad_signature_jwt"
    mock_decode.side_effect = jwt.InvalidSignatureError()

    with pytest.raises(BadJWTError):
        token_instance.verify()
    mock_logger.warning.assert_called_once_with("token has bad signature - %s", "bad_signature_jwt")


@patch("jwt.decode")
@patch("fia_auth.tokens.logger")
def test_verify_expired_signature(mock_logger, mock_decode):
    token_instance = Token()
    token_instance.jwt = "expired_jwt_token"
    mock_decode.side_effect = jwt.ExpiredSignatureError()

    with pytest.raises(BadJWTError):
        token_instance.verify()
    mock_logger.warning.assert_called_once_with("token signature is expired - %s", "expired_jwt_token")


@patch("jwt.decode")
@patch("fia_auth.tokens.logger")
def test_verify_invalid_token(mock_logger, mock_decode):
    token_instance = Token()
    token_instance.jwt = "invalid_jwt_token"
    mock_decode.side_effect = jwt.InvalidTokenError()

    with pytest.raises(BadJWTError):
        token_instance.verify()
    mock_logger.warning.assert_called_once_with("Issue decoding token - %s", "invalid_jwt_token")


@patch("jwt.decode")
@patch("fia_auth.tokens.logger")
def test_verify_general_exception(mock_logger, mock_decode):
    token_instance = Token()
    token_instance.jwt = "jwt_with_general_issue"
    exception = Exception("Unexpected error")
    mock_decode.side_effect = exception

    with pytest.raises(BadJWTError):
        token_instance.verify()
    mock_logger.exception.assert_called_once_with("JWT verification Failed for unknown reason")


@patch("fia_auth.tokens.datetime")
@patch("jwt.encode")
def test_access_token_with_payload(mock_encode, mock_datetime):
    fixed_time = datetime(2021, 1, 1, 12, 0, 0, tzinfo=UTC)
    mock_datetime.now.return_value = fixed_time
    payload = {"user": "test_user"}

    AccessToken(payload=payload)

    mock_encode.assert_called_once_with(
        {"user": "test_user", "exp": fixed_time + timedelta(minutes=10)},
        b"shh",
        algorithm="HS256",
    )


@patch("jwt.decode")
def test_access_token_with_jwt_token(mock_decode):
    jwt_token = "encoded.jwt.token"  # noqa: S105
    expected_payload = {"exp": datetime.now(UTC) + timedelta(minutes=1)}
    mock_decode.return_value = expected_payload

    token = AccessToken(jwt_token=jwt_token)

    assert token.jwt == jwt_token
    assert token._payload == expected_payload
    mock_decode.assert_called_once_with(
        jwt_token,
        "shh",
        algorithms=["HS256"],
        options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
    )


def test_access_token_with_both_none():
    with pytest.raises(BadJWTError):
        AccessToken()


@patch("jwt.encode")
@patch("jwt.decode")
def test_access_token_refresh(mock_decode, mock_encode):
    jwt_token = "valid.jwt.token"  # noqa: S105
    mock_decode.return_value = {"user": "test_user", "exp": datetime.now(UTC)}
    token = AccessToken(jwt_token=jwt_token)

    token.refresh()

    args, kwargs = mock_encode.call_args
    assert args[0]["exp"] > datetime.now(UTC)  # checks if the expiration time is extended


@patch("fia_auth.tokens.datetime")
@patch("jwt.encode")
def test_refresh_token_creation_no_jwt(mock_encode, mock_datetime):
    fixed_time = datetime(2021, 1, 1, 12, 0, 0, tzinfo=UTC)
    mock_datetime.now.return_value = fixed_time

    RefreshToken()

    mock_encode.assert_called_once_with(
        {"exp": fixed_time + timedelta(hours=12)},
        b"shh",
        algorithm="HS256",
    )


@patch("jwt.decode")
def test_refresh_token_creation_with_jwt(mock_decode):
    jwt_token = "encoded.jwt.token"  # noqa: S105
    expected_payload = {"exp": datetime.now(UTC) + timedelta(hours=12)}
    mock_decode.return_value = expected_payload

    token = RefreshToken(jwt_token=jwt_token)

    assert token._payload == expected_payload
    mock_decode.assert_called_once_with(
        jwt_token,
        "shh",
        algorithms=["HS256"],
        options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
    )


@patch("jwt.decode")
def test_refresh_token_with_invalid_jwt(mock_decode):
    mock_decode.side_effect = BadJWTError
    with pytest.raises(BadJWTError):
        RefreshToken(jwt_token="invalid.jwt.token")  # noqa: S106


@patch("fia_auth.tokens.datetime")
def test_generate_access_token(mock_datetime):
    user = User(user_number=12345)
    fixed_time = datetime(2000, 12, 12, 12, 0, tzinfo=UTC)
    mock_datetime.now.return_value = fixed_time
    access_token = generate_access_token(user)

    expected_payload = {
        "usernumber": 12345,
        "role": "user",
        "username": "foo",
        "exp": fixed_time + timedelta(minutes=10),
    }

    assert access_token._payload == expected_payload
