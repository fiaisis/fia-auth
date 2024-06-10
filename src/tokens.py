from __future__ import annotations

import logging
import os
from abc import ABC
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import jwt

from src.exceptions import BadJWTError
from src.model import User

PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "shh")
logger = logging.getLogger(__name__)


class Token(ABC):
    jwt: str

    def verify(self) -> None:
        try:
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
        except Exception as e:
            logger.exception("Oh Dear", e)
        raise BadJWTError("oh dear")

    def _encode(self) -> None:
        bytes_key = bytes(PRIVATE_KEY, encoding="utf8")

        self.jwt = jwt.encode(self._payload, bytes_key, algorithm="HS256")


class AccessToken(Token):
    def __init__(self, jwt_token: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> None:
        if payload and not jwt_token:
            self._payload = payload
            self._payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=1)
            self._encode()
        elif jwt_token and not payload:
            try:
                self._payload = jwt.decode(
                    jwt_token,
                    PRIVATE_KEY,
                    algorithms=["HS256"],
                    options={"verify_signature": True, "require": ["exp"], "verify_exp": True},
                )
                self.jwt = jwt_token
            except jwt.DecodeError as e:
                raise BadJWTError("Token could not be decoded") from e
        else:
            raise BadJWTError("Access token creation requires jwt_token string XOR a payload")

    def refresh(self) -> None:
        self.verify()
        self._payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=1)
        self._encode()


class RefreshToken(Token):
    def __init__(self, jwt_token: Optional[str] = None) -> None:

        if jwt_token is None:
            self._payload = {"exp": datetime.now(timezone.utc) + timedelta(hours=12)}
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
            except Exception:
                raise BadJWTError("Problem decoding JWT")


def generate_access_token(user: User) -> AccessToken:
    payload = {"usernumber": user.user_number, "role": user.role.value, "username": "foo"}
    return AccessToken(payload=payload)


def load_access_token(token: str) -> AccessToken:
    return AccessToken(jwt_token=token)


def load_refresh_token(token: Optional[str]) -> RefreshToken:
    if token is None:
        raise BadJWTError("Token is None")
    return RefreshToken(jwt_token=token)


def generate_refresh_token() -> RefreshToken:
    return RefreshToken()
