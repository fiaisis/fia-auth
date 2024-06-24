"""
Module containing code to authenticate with the UOWS
"""

from http import HTTPStatus

import requests

from fia_auth.exceptions import BadCredentialsError, UOWSError
from fia_auth.model import User, UserCredentials


def authenticate(credentials: UserCredentials) -> User:
    """
    Authenticate the user based on the given credentials
    :param credentials: The user credentials
    :return: UserNumber
    """
    data = ({"username": credentials.username, "password": credentials.password},)
    response = requests.post(
        "https://devapi.facilities.rl.ac.uk/users-service/v0/sessions",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code == HTTPStatus.CREATED:
        return User(user_number=response.json()["userId"])
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise BadCredentialsError("Invalid user credentials provided to authenticate with the user office web service.")

    raise UOWSError("An unexpected error occurred when authenticating with the user office web service")
