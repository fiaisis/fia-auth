"""
Module containing the fastapi routers
"""

import os
from typing import List, Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import JSONResponse

from src.auth import authenticate
from src.exceptions import BadJWTError, UOWSError, BadCredentialsError
from src.experiments import get_experiments_for_user_number
from src.model import UserCredentials
from src.tokens import generate_refresh_token, generate_access_token, load_access_token, load_refresh_token

ROUTER = APIRouter()

security = HTTPBearer(scheme_name="APIKey", description="API Key for internal routes")

API_KEY = os.environ.get("API_KEY", "shh")


@ROUTER.get("/experiments", tags=["internal"])
async def get_experiments(
    user_number: int, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> List[int]:
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
async def login(credentials: UserCredentials):
    try:
        user_number = authenticate(credentials)
        refresh_token = generate_refresh_token().jwt
        access_token = generate_access_token(user_number).jwt
        response = JSONResponse(content={"token": access_token}, status_code=200)
        response.set_cookie(
            "refresh-token", value=refresh_token, max_age=60 * 60 * 12, secure=True, httponly=True, samesite="lax"
        )  # 12 hours
        return response
    except UOWSError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except BadCredentialsError:
        raise HTTPException(status_code=403, detail="Invalid")


@ROUTER.post("/api/jwt/checkToken")
def verify(token: Dict[str, Any]):
    """
    Verify an access token was generated by this auth server and has not expired
    \f
    :param token: The JWT
    :return: "OK"
    """
    try:
        load_access_token(token["token"]).verify()
        return "ok"
    except BadJWTError:
        raise HTTPException(status_code=403, detail="")


@ROUTER.post("/api/jwt/refresh")
def refresh(token: Dict[str, Any], refresh_token: Annotated[str | None, Cookie()] = None):
    """
    Refresh an access token based on a refresh token
    \f
    :param token: The access token to be refreshed
    :return: The new access token
    """
    try:
        access_token = load_access_token(token["token"])
        refresh_token = load_refresh_token(refresh_token)
        refresh_token.verify()
        access_token.refresh()
        return {"token": access_token.jwt}
    except BadJWTError:
        raise HTTPException(status_code=403)
