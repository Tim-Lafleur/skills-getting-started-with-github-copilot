"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database before each test."""
    # Clear and repopulate activities with initial state
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)
