import requests

from src.exceptions import BadCredentialsError, UOWSError
from src.model import User
from src.model import UserCredentials


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
    )
    if response.status_code == 201:
        return User(user_number=response.json()["userId"])
    if response.status_code == 401:
        raise BadCredentialsError("Invalid user credentials provided to authenticate with the user office web service.")
    else:
        raise UOWSError(
            "An unexpected error occurred when authenticating with the user office web service %s", response.json()
        )
