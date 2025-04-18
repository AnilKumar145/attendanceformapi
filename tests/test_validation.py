import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.setenv('CAMPUS_LATITUDE', '40.7128')
    monkeypatch.setenv('CAMPUS_LONGITUDE', '-74.0060')
    monkeypatch.setenv('ALLOWED_RADIUS_METERS', '100')

def test_validate_location_within_radius(mock_env_variables):
    response = client.post(
        "/api/validation/location",
        json={
            "latitude": 40.7128,  # Same as campus location
            "longitude": -74.0060
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert data["distance"] == 0
    assert data["unit"] == "meters"

def test_validate_location_outside_radius(mock_env_variables):
    response = client.post(
        "/api/validation/location",
        json={
            "latitude": 40.7228,  # Far from campus
            "longitude": -74.0160
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert "distance" in data
    assert data["unit"] == "meters"

def test_validate_location_invalid_coordinates():
    response = client.post(
        "/api/validation/location",
        json={
            "latitude": 91,  # Invalid latitude
            "longitude": -74.0060
        }
    )
    assert response.status_code == 422  # Validation error

@patch('app.utils.security.SecurityValidator.check_vpn')
@patch('app.utils.security.SecurityValidator.validate_user_agent')
def test_validate_security_valid(mock_validate_agent, mock_check_vpn):
    # Mock the security checks to return valid results
    mock_check_vpn.return_value = False
    mock_validate_agent.return_value = True

    response = client.post(
        "/api/validation/security",
        json={
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"valid": True}

@patch('app.utils.security.SecurityValidator.check_vpn')
@patch('app.utils.security.SecurityValidator.validate_user_agent')
def test_validate_security_vpn_detected(mock_validate_agent, mock_check_vpn):
    # Mock VPN detection
    mock_check_vpn.return_value = True
    mock_validate_agent.return_value = True

    response = client.post(
        "/api/validation/security",
        json={
            "ip_address": "10.8.0.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "VPN usage detected"}

@patch('app.utils.security.SecurityValidator.check_vpn')
@patch('app.utils.security.SecurityValidator.validate_user_agent')
def test_validate_security_invalid_agent(mock_validate_agent, mock_check_vpn):
    # Mock invalid user agent
    mock_check_vpn.return_value = False
    mock_validate_agent.return_value = False

    response = client.post(
        "/api/validation/security",
        json={
            "ip_address": "192.168.1.1",
            "user_agent": "Invalid Agent"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid user agent"}

def test_validate_security_invalid_ip():
    response = client.post(
        "/api/validation/security",
        json={
            "ip_address": "invalid-ip",
            "user_agent": "Mozilla/5.0"
        }
    )
    assert response.status_code == 422  # Validation error