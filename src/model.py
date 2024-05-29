"""
Internal Models to help abstract and encapsulate the authentication process
"""

import enum
from dataclasses import dataclass

from pydantic import BaseModel


class UserCredentials(BaseModel):
    """
    Pydantic model for user credentials. Allows FastAPI to validate the object recieved in the login endpoint
    """

    username: str
    password: str


class Role(enum.Enum):
    """
    Role Enum to differentiate between user and staff. It is assumed staff will see all data
    """

    STAFF = "staff"
    USER = "user"


@dataclass
class User:
    """
    Internal User Model for packing JWTs
    """

    user_number: int

    @property
    def role(self) -> Role:
        # TODO: Actually assign a role
        return Role.USER
