# ruff: noqa: D100, D103
import os
import random
from http import HTTPStatus
from unittest import mock

from fia_auth.roles import is_instrument_scientist


@mock.patch("fia_auth.roles.requests")
def test_is_instrument_scientist_true(requests):
    uows_url = str(mock.MagicMock())
    uows_api_key = str(mock.MagicMock())
    os.environ["UOWS_URL"] = uows_url
    os.environ["UOWS_API_KEY"] = uows_api_key
    user_number = random.randint(0, 100000)  # noqa: S311
    requests.get.return_value.status_code = HTTPStatus.OK
    requests.get.return_value.json.return_value = [{"name": "ISIS Instrument Scientist"}]

    result = is_instrument_scientist(user_number)

    requests.get.assert_called_once_with(
        url=f"{uows_url}/v1/role/{user_number}",
        headers={"Authorization": f"Api-key {uows_api_key}", "accept": "application/json"},
        timeout=5,
    )
    assert result
    os.environ.pop("UOWS_URL")
    os.environ.pop("UOWS_API_KEY")


@mock.patch("fia_auth.roles.requests")
def test_is_instrument_scientist_false(requests):
    uows_url = str(mock.MagicMock())
    uows_api_key = str(mock.MagicMock())
    os.environ["UOWS_URL"] = uows_url
    os.environ["UOWS_API_KEY"] = uows_api_key
    user_number = random.randint(0, 100000)  # noqa: S311
    requests.get.return_value.status_code = HTTPStatus.OK
    requests.get.return_value.json.return_value = [{"name": "Not ISIS Instrument Scientist"}]

    result = is_instrument_scientist(user_number)

    requests.get.assert_called_once_with(
        url=f"{uows_url}/v1/role/{user_number}",
        headers={"Authorization": f"Api-key {uows_api_key}", "accept": "application/json"},
        timeout=5,
    )
    assert not result
    os.environ.pop("UOWS_URL")
    os.environ.pop("UOWS_API_KEY")


@mock.patch("fia_auth.roles.requests")
def test_is_instrument_scientist_false_when_forbidden(requests):
    uows_url = str(mock.MagicMock())
    uows_api_key = str(mock.MagicMock())
    os.environ["UOWS_URL"] = uows_url
    os.environ["UOWS_API_KEY"] = uows_api_key
    user_number = random.randint(0, 100000)  # noqa: S311
    requests.get.return_value.status_code = HTTPStatus.FORBIDDEN
    result = is_instrument_scientist(user_number)

    requests.get.assert_called_once_with(
        url=f"{uows_url}/v1/role/{user_number}",
        headers={"Authorization": f"Api-key {uows_api_key}", "accept": "application/json"},
        timeout=5,
    )
    assert not result
    os.environ.pop("UOWS_URL")
    os.environ.pop("UOWS_API_KEY")
