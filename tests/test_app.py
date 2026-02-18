import copy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# Keep original snapshot to restore between tests
original_activities = copy.deepcopy(activities)


def setup_function():
    # reset activities to original before each test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister():
    activity = "Basketball"
    email = "test_student@mergington.edu"

    # ensure not present
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # verify present
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]
