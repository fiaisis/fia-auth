"""
Module containing token classes, creation, and loading functions
"""

from __future__ import annotations

import logging
import os
from abc import ABC
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import jwt

from fia_auth.exceptions import BadJWTError

if TYPE_CHECKING:
    from fia_auth.model import User


PRIVATE_KEY = os.environ.get("JWT_SECRET", "shh")
ACCESS_TOKEN_LIFETIME_MINUTES = os.environ.get("ACCESS_TOKEN_LIFETIME_MINUTES", 10)

logger = logging.getLogger(__name__)


class Token(ABC):
    """
    Abstract token class defines verify method
    """

    jwt: str

    def verify(self) -> None:
        """
        Verifies the token, ensuring that it has a valid format, signature, and has not expired. Will raise a
        BadJWTError if verification fails
        :return: None
        """
        try:
            # class is abstract and all subclasses define payload within the init
            self._payload = jwt.decode(
                self.jwt,
                PRIVATE_KEY,
                algorithms=["HS256"],
                options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
            )

            return
        except jwt.InvalidSignatureError:
            logger.warning("token has bad signature - %s", self.jwt)
        except jwt.ExpiredSignatureError:
            logger.warning("token signature is expired - %s", self.jwt)
        except jwt.InvalidTokenError:
            logger.warning("Issue decoding token - %s", self.jwt)
        except Exception:
            logger.exception("JWT verification Failed for unknown reason")

        raise BadJWTError("jwt token verification failed")

    def _encode(self) -> None:
        bytes_key = bytes(PRIVATE_KEY, encoding="utf8")

        self.jwt = jwt.encode(self._payload, bytes_key, algorithm="HS256")


class AccessToken(Token):
    """
    Access Token is a short-lived (5 minute) token that stores user information
    """

    def __init__(self, jwt_token: str | None = None, payload: dict[str, Any] | None = None) -> None:
        if payload and not jwt_token:
            self._payload = payload
            self._payload["exp"] = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
            self._encode()
        elif jwt_token and not payload:
            try:
                self._payload = jwt.decode(
                    jwt_token,
                    PRIVATE_KEY,
                    algorithms=["HS256"],
                    options={"verify_signature": True, "require": ["exp"], "verify_exp": False},
                )
                self.jwt = jwt_token
            except jwt.DecodeError as e:
                raise BadJWTError("Token could not be decoded") from e
        else:
            raise BadJWTError("Access token creation requires jwt_token string XOR a payload")

    def refresh(self) -> None:
        """
        Refresh the access token by extending the expiry time by 10 minutes and resigning
        :return: None
        """
        self.verify()
        self._payload["exp"] = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
        self._encode()


class RefreshToken(Token):
    """
    Refresh token is a long-lived (12 hour) token that is required to refresh an access token
    """

    def __init__(self, jwt_token: str | None = None) -> None:
        if jwt_token is None:
            self._payload = {"exp": datetime.now(UTC) + timedelta(hours=12)}
            self._encode()
        else:
            self.jwt = jwt_token
            try:
                self._payload = jwt.decode(
                    self.jwt,
                    PRIVATE_KEY,
                    algorithms=["HS256"],
                    options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
                )
            except jwt.DecodeError as e:
                raise BadJWTError("Badly formed JWT given") from e
            except jwt.ExpiredSignatureError as e:
                raise BadJWTError("Token signature has expired") from e
            except Exception as e:
                raise BadJWTError("Problem decoding JWT") from e


def generate_access_token(user: User) -> AccessToken:
    """
    Given a user, generate an AccessToken for them
    :param user: The user
    :return: The generated Access Token
    """
    payload = {"usernumber": user.user_number, "role": user.role.value, "username": "foo"}
    return AccessToken(payload=payload)


def load_access_token(token: str) -> AccessToken:
    """
    Given a jwt string, return an access token object for it
    :param token: the jwt string
    :return: The access token object
    """
    return AccessToken(jwt_token=token)


def load_refresh_token(token: str | None) -> RefreshToken:
    """
    Given a jwt string, return a refresh token object for it
    :param token: the jwt string
    :return: The refresh token object
    """
    if token is None:
        raise BadJWTError("Token is None")
    return RefreshToken(jwt_token=token)


def generate_refresh_token() -> RefreshToken:
    """
    Generate a new Refresh Token
    :return: The refresh token object
    """
    return RefreshToken()
