import os
from http import HTTPStatus

import requests


def is_instrument_scientist(user_number: int) -> bool:
    uows_url = os.environ.get("UOWS_URL", "https://devapi.facilities.rl.ac.uk/users-service")
    uows_api_key = os.environ.get("UOWS_API_KEY", "")
    response = requests.get(
        url=f"{uows_url}/v1/role/{user_number}",
        headers={"Authorization": f"Api-key {uows_api_key}", "accept": "application/json"},
        timeout=1,
    )
    if response.status_code != HTTPStatus.OK:
        from fia_auth.auth import logger

        logger.info("User number %s is not an instrument scientist or UOWS API is down", user_number)
        return False
    roles = response.json()
    return {"name": "ISIS Instrument Scientist"} in roles
