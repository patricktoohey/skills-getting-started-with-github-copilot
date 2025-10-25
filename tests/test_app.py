import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200  # The static file middleware returns 200, not 307

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity_success(client):
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_for_activity_not_found(client):
    response = client.post("/activities/NonExistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"

def test_signup_for_activity_full(client):
    # First, fill up the Chess Club
    activity = activities["Chess Club"]
    original_participants = activity["participants"].copy()
    
    # Fill the activity to maximum
    while len(activity["participants"]) < activity["max_participants"]:
        email = f"student{len(activity['participants'])}@mergington.edu"
        activity["participants"].append(email)
    
    # Try to add one more participant
    response = client.post("/activities/Chess Club/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "full" in data["detail"].lower()
    
    # Restore original participants
    activity["participants"] = original_participants

def test_signup_for_activity_duplicate(client):
    # Try to sign up with an email that's already registered
    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess Club/signup?email={existing_email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()