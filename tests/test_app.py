import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_unregister_participant_removes_email():
    client = TestClient(app_module.app)

    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    data = client.get("/activities").json()
    assert "michael@mergington.edu" not in data["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    client = TestClient(app_module.app)

    response = client.delete("/activities/Chess Club/participants/unknown@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
