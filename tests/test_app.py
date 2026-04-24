"""Tests for the FastAPI activities management application."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected activities exist
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Gym Class should have participants
        gym_class = data["Gym Class"]
        assert len(gym_class["participants"]) >= 2


class TestRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@test.com"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newemail@test.com" in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newemail@test.com" in activities["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup fails when activity does not exist."""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@test.com"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signup fails when user is already registered."""
        # Try to signup someone already in Gym Class
        response = client.post(
            "/activities/Gym Class/signup?email=john@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Already signed up for this activity"
    
    def test_signup_activity_at_max_capacity(self, client):
        """Test signup fails when activity is at max capacity."""
        # Chess Club has max_participants=12 and already has 2 participants
        # We need to fill it up to max capacity
        
        # First, get current activities to check Chess Club details
        activities_response = client.get("/activities")
        activities = activities_response.json()
        chess_club = activities["Chess Club"]
        
        # Fill remaining spots
        spots_available = chess_club["max_participants"] - len(chess_club["participants"])
        
        # Add participants until full
        for i in range(spots_available):
            client.post(
                f"/activities/Chess Club/signup?email=user{i}@test.com"
            )
        
        # Try to sign up one more person - should fail
        response = client.post(
            "/activities/Chess Club/signup?email=extrauser@test.com"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is at max capacity"


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        # First verify participant is there
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "john@mergington.edu" in activities["Gym Class"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Gym Class/unregister?email=john@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "john@mergington.edu" in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "john@mergington.edu" not in activities["Gym Class"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister fails when activity does not exist."""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=test@test.com"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client):
        """Test unregister fails when student is not registered."""
        response = client.post(
            "/activities/Gym Class/unregister?email=notregistered@test.com"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
