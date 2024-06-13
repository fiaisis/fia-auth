"""
e2e test cases
"""

from unittest.mock import patch

from starlette.testclient import TestClient

from src.app import app

client = TestClient(app)

ALLOCATIONS_EMPTY_RESPONSE = {"proposals": []}
ALLOCATIONS_RESPONSE = {
    "proposals": [
        {"referenceNumber": "9723"},
        {"referenceNumber": "2200087"},
        {"referenceNumber": "2200084"},
        {"referenceNumber": "2200081"},
        {"referenceNumber": "2200083"},
        {"referenceNumber": "2200085"},
        {"referenceNumber": "2200086"},
        {"referenceNumber": "2200082"},
        {"referenceNumber": "1620354"},
    ]
}


def test_get_experiments_with_missing_api_key_returns_403():
    response = client.get("/experiments?user_number=123")
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_experiments_with_bad_api_key_returns_403():
    response = client.get("/experiments?user_number=123", headers={"Authorization": "Bearer 123"})
    assert response.status_code == HTTPStatus.FORBIDDEN


@patch("src.experiments.Client.execute_async")
def test_get_experiments_none_exist_for_user_returns_empty(mock_exec):
    mock_exec.return_value = ALLOCATIONS_EMPTY_RESPONSE
    response = client.get("/experiments?user_number=123", headers={"Authorization": "Bearer shh"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@patch("src.experiments.Client.execute_async")
def test_get_experiments_for_user(mock_exec):
    mock_exec.return_value = ALLOCATIONS_RESPONSE
    response = client.get("/experiments?user_number=123", headers={"Authorization": "Bearer shh"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [9723, 2200087, 2200084, 2200081, 2200083, 2200085, 2200086, 2200082, 1620354]
