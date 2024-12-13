import pytest
from unittest.mock import patch, Mock
from src.data.fpl_api import (
    get_bootstrap_json,
    get_fixtures_json,
    make_request,
    get_team_abbreviations_map,
)

# Mock data
MOCK_BOOTSTRAP_DATA = {
    "teams": [
        {"id": 1, "short_name": "ARS"},
        {"id": 2, "short_name": "AVL"},
        {"id": 3, "short_name": "BOU"},
    ]
}


@pytest.fixture
def mock_successful_response():
    """Creates a mock response object with success status code"""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"test": "data"}
    return mock


def test_make_request_success(mock_successful_response):
    """Test successful API request"""
    with patch("requests.get", return_value=mock_successful_response):
        result = make_request("https://test-url.com")

    assert result == {"test": "data"}


def test_make_request_failure():
    """Test failed API request"""
    mock_failed_response = Mock()
    mock_failed_response.status_code = 404

    with patch("requests.get", return_value=mock_failed_response):
        with pytest.raises(Exception) as exc_info:
            make_request("https://test-url.com")

        assert 'Error fetching "https://test-url.com": 404' in str(exc_info.value)


def test_get_bootstrap_json(mock_successful_response):
    """Test bootstrap JSON endpoint"""
    expected_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

    with patch("requests.get", return_value=mock_successful_response) as mock_get:
        result = get_bootstrap_json()

        mock_get.assert_called_once_with(expected_url)
        assert result == {"test": "data"}


def test_get_fixtures_json(mock_successful_response):
    """Test fixtures JSON endpoint"""
    expected_url = "https://fantasy.premierleague.com/api/fixtures/"

    with patch("requests.get", return_value=mock_successful_response) as mock_get:
        result = get_fixtures_json()

        mock_get.assert_called_once_with(expected_url)
        assert result == {"test": "data"}


def test_get_team_abbreviations_map_with_data():
    """Test getting team abbreviations with provided bootstrap data"""
    result = get_team_abbreviations_map(MOCK_BOOTSTRAP_DATA)

    expected = {1: "ARS", 2: "AVL", 3: "BOU"}
    assert result == expected


@patch("src.data.fpl_api.get_bootstrap_json")
def test_get_team_abbreviations_map_without_data(mock_bootstrap):
    """Test getting team abbreviations when bootstrap data is not provided"""
    mock_bootstrap.return_value = MOCK_BOOTSTRAP_DATA

    result = get_team_abbreviations_map()

    mock_bootstrap.assert_called_once()
    expected = {1: "ARS", 2: "AVL", 3: "BOU"}
    assert result == expected
