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
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    data = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in data[activity_name]["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "unknown@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_rejects_when_activity_is_full():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    app_module.activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]
    app_module.activities[activity_name]["max_participants"] = 2

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
