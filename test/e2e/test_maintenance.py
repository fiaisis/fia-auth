# ruff: noqa: D100, D103

from http import HTTPStatus

from starlette.testclient import TestClient

from fia_auth.fia_auth import app

client = TestClient(app)

def test_maintenance_state():
    response = client.get("/maintenance")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["show"] is False
    assert data["message"] == "Maintenance mode is not supported by this API."
