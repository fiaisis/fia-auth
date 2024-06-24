"""
Module containing code to authenticate with the UOWS
"""

import logging
import os
from http import HTTPStatus

import requests

from fia_auth.exceptions import BadCredentialsError, UOWSError
from fia_auth.model import User, UserCredentials

logger = logging.getLogger(__name__)
UOWS_URL = os.environ.get("UOWS_URL", "https://devapi.facilities.rl.ac.uk/users-service")


def authenticate(credentials: UserCredentials) -> User:
    """
    Authenticate the user based on the given credentials
    :param credentials: The user credentials
    :return: UserNumber
    """
    data = ({"username": credentials.username, "password": credentials.password},)
    logger.info("Posting to UOWS")
    response = requests.post(
        f"{UOWS_URL}/v0/sessions",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code == HTTPStatus.CREATED:
        logger.info("Session created with UOWS")
        return User(user_number=response.json()["userId"])
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        logger.info("Bad credentials given to UOWS")
        raise BadCredentialsError("Invalid user credentials provided to authenticate with the user office web service.")
    logger.warning("Unexpected error occured when authentication with the UOWS")
    raise UOWSError("An unexpected error occurred when authenticating with the user office web service")
