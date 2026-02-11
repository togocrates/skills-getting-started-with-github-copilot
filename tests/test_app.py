"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Music Orchestra",
            "Debate Team",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"


class TestSignupEndpoint:
    """Test the signup endpoint"""

    def test_signup_for_activity_returns_200(self):
        """Test that signup returns a 200 status code"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_for_activity_returns_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=unique_test_1@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "unique_test_1@mergington.edu" in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_returns_400(self):
        """Test that duplicate signup returns 400"""
        test_email = "duplicate_test@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Tennis%20Club/signup?email={test_email}"
        )
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(
            f"/activities/Tennis%20Club/signup?email={test_email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_participant_added_to_activity(self):
        """Test that a participant is actually added to the activity"""
        test_email = "verify_add@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Drama%20Club/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Verify participant is in the list
        activities_response = client.get("/activities")
        drama_club = activities_response.json()["Drama Club"]
        assert test_email in drama_club["participants"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""

    def test_unregister_from_activity_returns_200(self):
        """Test that unregister returns a 200 status code"""
        test_email = "unregister_test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Music%20Orchestra/signup?email={test_email}")
        
        # Then unregister
        response = client.post(
            f"/activities/Music%20Orchestra/unregister?email={test_email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_message(self):
        """Test that unregister returns a success message"""
        test_email = "unregister_msg_test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Debate%20Team/signup?email={test_email}")
        
        # Then unregister
        response = client.post(
            f"/activities/Debate%20Team/unregister?email={test_email}"
        )
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]

    def test_unregister_from_nonexistent_activity_returns_404(self):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_removes_participant(self):
        """Test that a participant is actually removed from the activity"""
        test_email = "verify_remove@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Science%20Club/signup?email={test_email}")
        
        # Verify participant is in the list
        activities_response = client.get("/activities")
        science_club = activities_response.json()["Science Club"]
        assert test_email in science_club["participants"]
        
        # Unregister
        client.post(f"/activities/Science%20Club/unregister?email={test_email}")
        
        # Verify participant is removed
        activities_response = client.get("/activities")
        science_club = activities_response.json()["Science Club"]
        assert test_email not in science_club["participants"]

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test that unregistering a non-existent participant returns 400"""
        response = client.post(
            "/activities/Programming%20Class/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_endpoint_redirects(self):
        """Test that the root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
