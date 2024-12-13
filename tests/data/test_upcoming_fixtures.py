import pytest
from unittest.mock import patch
import pandas as pd
from src.data.upcoming_fixtures import (
    get_upcoming_fixtures,
    get_next_gameweek_id,
    get_raw_fixtures,
    get_team_abbreviations,
    apply_team_abbreviations,
)

# Mock data for testing
MOCK_BOOTSTRAP_DATA = {
    "events": [
        {"id": 1, "finished": True},
        {"id": 2, "finished": True},
        {"id": 3, "finished": False},
        {"id": 4, "finished": False},
        {"id": 5, "finished": False},
    ],
    "teams": [
        {"id": 1, "short_name": "ARS"},
        {"id": 2, "short_name": "AVL"},
        {"id": 3, "short_name": "BOU"},
        {"id": 4, "short_name": "BRE"},
        {"id": 5, "short_name": "BHA"},
        {"id": 6, "short_name": "CHE"},
    ],
}

MOCK_FIXTURES_DATA = [
    # Past gameweeks
    {"event": 1, "team_h": 1, "team_a": 2},
    {"event": 1, "team_h": 3, "team_a": 4},
    {"event": 2, "team_h": 5, "team_a": 6},
    # Current and future gameweeks
    {"event": 3, "team_h": 1, "team_a": 3},
    {"event": 3, "team_h": 2, "team_a": 4},
    {"event": 3, "team_h": 5, "team_a": 6},
    {"event": 4, "team_h": 3, "team_a": 1},
    {"event": 4, "team_h": 4, "team_a": 2},
    {"event": 5, "team_h": 1, "team_a": 4},
    {"event": 5, "team_h": 2, "team_a": 5},
    {"event": None, "team_h": 5, "team_a": 4},  # Postponed game
]


def test_get_next_gameweek_id():
    """Test getting next gameweek ID"""
    result = get_next_gameweek_id(MOCK_BOOTSTRAP_DATA)
    assert result == 3  # First non-finished gameweek


def test_get_next_gameweek_id_no_upcoming():
    """Test getting next gameweek ID when all games are finished"""
    data = {"events": [{"id": 1, "finished": True}, {"id": 2, "finished": True}]}

    with pytest.raises(Exception) as exc_info:
        get_next_gameweek_id(data)

    assert "come back next season" in str(exc_info.value)


@patch("src.data.upcoming_fixtures.get_fixtures_json")
def test_get_raw_fixtures(mock_fixtures_json):
    """Test getting raw fixtures within horizon"""
    # Setup mock
    mock_fixtures_json.return_value = MOCK_FIXTURES_DATA

    result = get_raw_fixtures(3, 4)

    # Verify mock was called
    mock_fixtures_json.assert_called_once()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5  # 3 fixtures from GW3 + 2 from GW4
    assert set(result["gameweek"].unique()) == {3, 4}

    # Check fixture counts per gameweek
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3
    assert gw_counts[4] == 2


def test_get_team_abbreviations():
    """Test getting team abbreviations mapping"""
    result = get_team_abbreviations(MOCK_BOOTSTRAP_DATA)

    assert isinstance(result, dict)
    expected = {1: "ARS", 2: "AVL", 3: "BOU", 4: "BRE", 5: "BHA", 6: "CHE"}
    assert result == expected


def test_apply_team_abbreviations():
    """Test applying team abbreviations to fixtures"""
    fixtures = pd.DataFrame(
        {"gameweek": [3, 3, 3], "home": [1, 2, 5], "away": [3, 4, 6]}
    )

    team_abbreviations = {1: "ARS", 2: "AVL", 3: "BOU", 4: "BRE", 5: "BHA", 6: "CHE"}

    result = apply_team_abbreviations(fixtures, team_abbreviations)

    assert isinstance(result, pd.DataFrame)
    assert result["home"].tolist() == ["ARS", "AVL", "BHA"]
    assert result["away"].tolist() == ["BOU", "BRE", "CHE"]


@patch("src.data.upcoming_fixtures.get_fixtures_json")
@patch("src.data.upcoming_fixtures.get_bootstrap_json")
def test_get_upcoming_fixtures_integration(mock_bootstrap, mock_fixtures):
    """Integration test for get_upcoming_fixtures"""
    # Setup mocks
    mock_bootstrap.return_value = MOCK_BOOTSTRAP_DATA
    mock_fixtures.return_value = MOCK_FIXTURES_DATA

    # Test with horizon=2 (should get GW3 and GW4 fixtures)
    result = get_upcoming_fixtures(horizon=2)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5  # 3 fixtures from GW3 + 2 fixtures from GW4
    assert set(result["gameweek"].unique()) == {3, 4}

    # Verify exact fixture counts per gameweek
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3
    assert gw_counts[4] == 2

    # Check team names are properly mapped
    assert set(result["home"].unique()) | set(result["away"].unique()) <= {
        "ARS",
        "AVL",
        "BOU",
        "BRE",
        "BHA",
        "CHE",
    }


@patch("src.data.upcoming_fixtures.get_fixtures_json")
@patch("src.data.upcoming_fixtures.get_bootstrap_json")
def test_get_upcoming_fixtures_larger_horizon(mock_bootstrap, mock_fixtures):
    """Test getting fixtures with a larger horizon"""
    mock_bootstrap.return_value = MOCK_BOOTSTRAP_DATA
    mock_fixtures.return_value = MOCK_FIXTURES_DATA

    result = get_upcoming_fixtures(horizon=3)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 7  # All fixtures from GW3-5
    assert set(result["gameweek"].unique()) == {3, 4, 5}

    # Verify fixture counts per gameweek
    gw_counts = result["gameweek"].value_counts().to_dict()
    assert gw_counts[3] == 3
    assert gw_counts[4] == 2
    assert gw_counts[5] == 2
