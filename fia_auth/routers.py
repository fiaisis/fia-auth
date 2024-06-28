"""
Module containing the fastapi routers
"""

from __future__ import annotations

import logging
import os
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fia_auth.auth import authenticate
from fia_auth.exceptions import UOWSError
from fia_auth.experiments import get_experiments_for_user_number
from fia_auth.model import UserCredentials  # noqa: TCH001   # Required for fastapi
from fia_auth.tokens import generate_access_token, generate_refresh_token, load_access_token, load_refresh_token

ROUTER = APIRouter()

security = HTTPBearer(scheme_name="APIKey", description="API Key for internal routes")

API_KEY = os.environ.get("FIA_AUTH_API_KEY", "shh")

logger = logging.getLogger(__name__)


@ROUTER.get("/experiments", tags=["internal"])
async def get_experiments(
    user_number: int, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> list[int]:
    """
    Get the experiment (RB) numbers for the given user number provided by query string parameter

    \f
    :param user_number: The user number
    :param credentials: The API Key
    :return: A list of experiment (RB) Numbers for the given user
    """
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await get_experiments_for_user_number(user_number)


@ROUTER.post("/api/jwt/authenticate", tags=["auth"])
async def login(credentials: UserCredentials) -> JSONResponse:
    """
    Login with facilities account
    \f
    :param credentials: username and password
    :return: JSON Response for access token and cookie set for refresh token
    """
    logger.info("Starting login for user %s", (credentials.username[0:3] + "****"))
    try:
        user_number = authenticate(credentials)
        refresh_token = generate_refresh_token().jwt
        access_token = generate_access_token(user_number).jwt
        response = JSONResponse(content={"token": access_token}, status_code=200)
        response.set_cookie(
            "refresh_token",
            value=refresh_token,
            max_age=60 * 60 * 12,
            secure=True,
            httponly=True,
            samesite="lax",
            path="/auth/api/jwt/refresh",
        )  # 12 hours
        return response
    except UOWSError as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc


@ROUTER.post("/api/jwt/checkToken")
def verify(token: dict[str, Any]) -> Literal["ok"]:
    """
    Verify an access token was generated by this auth server and has not expired
    \f
    :param token: The JWT
    :return: "OK"
    """
    logger.info("Verifying token")
    load_access_token(token["token"]).verify()
    logger.info("Token verified successfully")
    return "ok"


@ROUTER.post("/api/jwt/refresh")
def refresh(
    body: dict[str, Any], refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None
) -> JSONResponse:
    """
    Refresh an access token based on a refresh token
    \f
    :param refresh_token:
    :param token: The access token to be refreshed
    :return: The new access token
    """
    logger.warning("hello")
    if refresh_token is None:
        raise HTTPException(500, detail="Refresh")
    logger.info("Loading access token for refresh")
    access_token = load_access_token(body["token"])
    logger.info("Loading refresh token")
    loaded_refresh_token = load_refresh_token(refresh_token)
    logger.info("Verifying refresh token")
    loaded_refresh_token.verify()
    logger.info("refreshing access token")
    access_token.refresh()
    return JSONResponse({"token": access_token.jwt})
