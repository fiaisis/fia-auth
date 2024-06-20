"""
Internal Models to help abstract and encapsulate the authentication process
"""

import enum
from dataclasses import dataclass

from pydantic import BaseModel

from src.db import is_staff_user


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
        """
        Determine and determine the role of the user based on their usernumber
        :return:
        """
        if is_staff_user(self.user_number):
            return Role.STAFF
        return Role.USER
