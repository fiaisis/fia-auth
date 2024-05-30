"""
Module containing the fastapi routers
"""

import os
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.experiments import get_experiments_for_user_number

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
