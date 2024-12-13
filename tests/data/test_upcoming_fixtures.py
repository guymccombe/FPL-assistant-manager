import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.data.upcoming_fixtures import *

# Mock data for testing
MOCK_BOOTSTRAP_DATA = {
    "events": [
        {"id": 1, "finished": True},
        {"id": 2, "finished": True},
        {"id": 3, "finished": False},
        {"id": 4, "finished": False},
        {"id": 5, "finished": False}
    ],
    "teams": [
        {"id": 1, "short_name": "ARS"},
        {"id": 2, "short_name": "AVL"},
        {"id": 3, "short_name": "BOU"},
        {"id": 4, "short_name": "BRE"},
        {"id": 5, "short_name": "BHA"},
        {"id": 6, "short_name": "CHE"}
    ]
}

MOCK_FIXTURES_DATA = [
    # Past gameweeks
    {"event": 1, "team_h": 1, "team_a": 2},
    {"event": 1, "team_h": 3, "team_a": 4},
    {"event": 1, "team_h": 5, "team_a": 6},
    {"event": 2, "team_h": 2, "team_a": 1},
    {"event": 2, "team_h": 4, "team_a": 3},
    {"event": 2, "team_h": 6, "team_a": 5},

    # Current and future gameweeks
    {"event": 3, "team_h": 1, "team_a": 3},  # GW3 - 3 fixtures
    {"event": 3, "team_h": 2, "team_a": 4},
    {"event": 3, "team_h": 5, "team_a": 6},

    {"event": 4, "team_h": 3, "team_a": 1},  # GW4 - 2 fixtures
    {"event": 4, "team_h": 4, "team_a": 2},

    {"event": 5, "team_h": 1, "team_a": 4},  # GW5 - 3 fixtures
    {"event": 5, "team_h": 2, "team_a": 5},
    {"event": 5, "team_h": 3, "team_a": 6},

    {"event": None, "team_h": 5, "team_a": 4},  # Postponed game
]


@pytest.fixture
def mock_response():
    """Creates a mock response object with success status code"""
    mock = Mock()
    mock.status_code = 200
    return mock


def test_get_bootstrap_data_success(mock_response):
    """Test successful bootstrap data fetching"""
    mock_response.json.return_value = MOCK_BOOTSTRAP_DATA

    with patch('requests.get', return_value=mock_response):
        result = get_bootstrap_data()

    assert result == MOCK_BOOTSTRAP_DATA
    assert isinstance(result, dict)
    assert "events" in result
    assert "teams" in result


def test_get_bootstrap_data_failure():
    """Test bootstrap data fetching with error response"""
    mock_failed_response = Mock()
    mock_failed_response.status_code = 404

    with patch('requests.get', return_value=mock_failed_response):
        with pytest.raises(Exception) as exc_info:
            get_bootstrap_data()

        assert "Error fetching" in str(exc_info.value)


def test_get_next_gameweek_id():
    """Test getting next gameweek ID"""
    result = get_next_gameweek_id(MOCK_BOOTSTRAP_DATA)
    assert result == 3  # First non-finished gameweek in mock data


def test_get_next_gameweek_id_no_upcoming():
    """Test getting next gameweek ID when all games are finished"""
    data = {
        "events": [
            {"id": 1, "finished": True},
            {"id": 2, "finished": True}
        ]
    }

    with pytest.raises(Exception) as exc_info:
        get_next_gameweek_id(data)

    assert "come back next season" in str(exc_info.value)


def test_get_raw_fixtures_with_horizon(mock_response):
    """Test fetching raw fixtures respecting the horizon parameter"""
    mock_response.json.return_value = MOCK_FIXTURES_DATA

    with patch('requests.get', return_value=mock_response):
        # Get fixtures for gameweeks 3-4 (horizon = 2)
        result = get_raw_fixtures(3, 4)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5  # Should include 3 fixtures from GW3 and 2 from GW4
    assert list(result.columns) == ["gameweek", "home", "away"]
    assert set(result["gameweek"].unique()) == {3, 4}

    # Check fixture counts per gameweek
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3  # 3 fixtures in GW3
    assert gw_counts[4] == 2  # 2 fixtures in GW4


def test_get_raw_fixtures_larger_horizon(mock_response):
    """Test fetching raw fixtures with a larger horizon"""
    mock_response.json.return_value = MOCK_FIXTURES_DATA

    with patch('requests.get', return_value=mock_response):
        # Get fixtures for gameweeks 3-5 (horizon = 3)
        result = get_raw_fixtures(3, 5)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 8  # Total fixtures across GW3-5
    assert set(result["gameweek"].unique()) == {3, 4, 5}

    # Check fixture counts per gameweek
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3  # 3 fixtures in GW3
    assert gw_counts[4] == 2  # 2 fixtures in GW4
    assert gw_counts[5] == 3  # 3 fixtures in GW5


def test_get_team_abbreviations():
    """Test getting team abbreviations"""
    result = get_team_abbreviations(MOCK_BOOTSTRAP_DATA)

    assert isinstance(result, dict)
    expected_abbrev = {1: "ARS", 2: "AVL", 3: "BOU", 4: "BRE", 5: "BHA", 6: "CHE"}
    assert result == expected_abbrev


def test_apply_team_abbreviations():
    """Test applying team abbreviations to fixtures"""
    fixtures = pd.DataFrame({
        "gameweek": [3, 3, 3],  # Same gameweek, multiple fixtures
        "home": [1, 2, 5],
        "away": [3, 4, 6]
    })

    team_abbreviations = {1: "ARS", 2: "AVL", 3: "BOU", 4: "BRE", 5: "BHA", 6: "CHE"}

    result = apply_team_abbreviations(fixtures, team_abbreviations)

    assert isinstance(result, pd.DataFrame)
    assert result["home"].tolist() == ["ARS", "AVL", "BHA"]
    assert result["away"].tolist() == ["BOU", "BRE", "CHE"]


@patch('requests.get')
def test_get_upcoming_fixtures_integration(mock_get):
    """Integration test for get_upcoming_fixtures"""
    # Setup mock responses
    mock_bootstrap_response = Mock()
    mock_bootstrap_response.status_code = 200
    mock_bootstrap_response.json.return_value = MOCK_BOOTSTRAP_DATA

    mock_fixtures_response = Mock()
    mock_fixtures_response.status_code = 200
    mock_fixtures_response.json.return_value = MOCK_FIXTURES_DATA

    mock_get.side_effect = [mock_bootstrap_response, mock_fixtures_response]

    # Test with horizon=2 (should get GW3 and GW4 fixtures)
    result = get_upcoming_fixtures(horizon=2)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5  # 3 fixtures from GW3 + 2 fixtures from GW4
    assert set(result["gameweek"].unique()) == {3, 4}

    # Check specific fixtures exist
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3  # 3 fixtures in GW3
    assert gw_counts[4] == 2  # 2 fixtures in GW4


def test_get_raw_fixtures_failure():
    """Test fixtures fetching with error response"""
    mock_failed_response = Mock()
    mock_failed_response.status_code = 500

    with patch('requests.get', return_value=mock_failed_response):
        with pytest.raises(Exception) as exc_info:
            get_raw_fixtures(3, 4)

        assert "Error fetching" in str(exc_info.value)