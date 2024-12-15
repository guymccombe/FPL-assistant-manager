import pytest
import pandas as pd
from unittest.mock import patch, Mock

from src.data.league_table import construct_league_table, construct_raw_table


@pytest.fixture
def sample_fixtures():
    return [
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 2,
            "team_h_score": 2,
            "team_a_score": 0,
        },
        {
            "event": 1,
            "finished": True,
            "team_h": 3,
            "team_a": 4,
            "team_h_score": 1,
            "team_a_score": 1,
        },
        {
            "event": 2,
            "finished": False,  # Upcoming match
            "team_h": 1,
            "team_a": 3,
            "team_h_score": 0,
            "team_a_score": 0,
        },
        {
            "event": None,  # Postponed match
            "finished": False,
            "team_h": 2,
            "team_a": 4,
            "team_h_score": 0,
            "team_a_score": 0,
        },
    ]


@pytest.fixture
def postponed_fixtures():
    return [
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 2,
            "team_h_score": 2,
            "team_a_score": 0,
        },
        {
            "event": None,  # Postponed match
            "finished": False,
            "team_h": 3,
            "team_a": 4,
            "team_h_score": 0,
            "team_a_score": 0,
        },
        {
            "event": None,  # Another postponed match
            "finished": True,  # Even if finished is True, event=None means postponed
            "team_h": 3,
            "team_a": 5,
            "team_h_score": 2,
            "team_a_score": 1,
        },
    ]


@pytest.fixture
def team_abbreviations():
    return {
        1: "ARS",
        2: "AVL",
        3: "BOU",
        4: "BRE",
        5: "BHA",  # Additional team for testing
    }


def test_construct_raw_table_basic(sample_fixtures):
    """Test basic functionality of construct_raw_table"""
    table = construct_raw_table(sample_fixtures)

    # Check table structure
    assert isinstance(table, pd.DataFrame)
    expected_columns = [
        "played",
        "points",
        "GD",
        "GF",
        "GA",
        "W",
        "D",
        "L",
        "rank",
    ]
    assert all(col in table.columns for col in expected_columns)

    # Check team 1 (won match)
    team_1 = table[table.index == 1].iloc[0]
    assert team_1["played"] == 1
    assert team_1["points"] == 3
    assert team_1["W"] == 1
    assert team_1["D"] == 0
    assert team_1["L"] == 0
    assert team_1["GF"] == 2
    assert team_1["GA"] == 0
    assert team_1["GD"] == 2

    # Check team 3 and 4 (drew match)
    team_3 = table[table.index == 3].iloc[0]
    assert team_3["points"] == 1
    assert team_3["D"] == 1


def test_construct_raw_table_postponed_matches(postponed_fixtures):
    """Test handling of postponed matches"""
    table = construct_raw_table(postponed_fixtures)

    # Check team 3 (has two postponed matches)
    team_3 = table[table.index == 3].iloc[0]
    assert team_3["played"] == 0  # Should not count postponed matches
    assert team_3["points"] == 0
    assert team_3["GF"] == 0
    assert team_3["GA"] == 0

    # Check team 4 (has one postponed match)
    team_4 = table[table.index == 4].iloc[0]
    assert team_4["played"] == 0
    assert team_4["points"] == 0

    # Check team 1 (has one normal match)
    team_1 = table[table.index == 1].iloc[0]
    assert team_1["played"] == 1
    assert team_1["points"] == 3


def test_construct_raw_table_mixed_postponed_and_played(postponed_fixtures):
    """Test table construction with a mix of played and postponed matches"""
    table = construct_raw_table(postponed_fixtures)

    total_played_matches = sum(table["played"])
    assert (
        total_played_matches == 2
    )  # Only one match should be counted (team 1 vs team 2)

    # Verify that postponed matches don't affect rankings
    assert table.iloc[0]["team"] == 1  # Team 1 should be first with 3 points
    assert table.iloc[0]["points"] == 3

    # Check that teams with postponed matches are ranked by default order
    teams_with_postponed = [3, 4, 5]
    for team_id in teams_with_postponed:
        team_row = table[table["team"] == team_id].iloc[0]
        assert team_row["played"] == 0
        assert team_row["points"] == 0


def test_construct_raw_table_all_teams_included():
    """Test that all 20 teams are included in the table even if they haven't played"""
    empty_fixtures = []
    table = construct_raw_table(empty_fixtures)

    assert len(table) == 20
    assert all(table["played"] == 0)
    assert all(table["points"] == 0)


def test_construct_raw_table_sorting(sample_fixtures):
    """Test that teams are correctly sorted by points, then GD, then GF"""
    table = construct_raw_table(sample_fixtures)

    # Verify sorting
    assert table.iloc[0]["team"] == 1  # Team 1 should be first (3 points)
    assert table.iloc[1]["team"] in [
        3,
        4,
    ]  # Teams 3 and 4 should be next (1 point each)

    # Check rank assignment
    assert all(table["rank"] == range(1, 21))


def test_construct_raw_table_multiple_matches():
    """Test accumulation of stats over multiple matches"""
    fixtures = [
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 2,
            "team_h_score": 2,
            "team_a_score": 0,
        },
        {
            "event": 2,
            "finished": True,
            "team_h": 1,
            "team_a": 3,
            "team_h_score": 1,
            "team_a_score": 1,
        },
    ]

    table = construct_raw_table(fixtures)
    team_1 = table[table.index == 1].iloc[0]

    assert team_1["played"] == 2
    assert team_1["points"] == 4  # 3 for win + 1 for draw
    assert team_1["GF"] == 3  # 2 + 1 goals
    assert team_1["GA"] == 1  # 0 + 1 goals
    assert team_1["W"] == 1
    assert team_1["D"] == 1


@patch("src.data.league_table.get_fixtures_json")
@patch("src.data.league_table.get_team_abbreviations_map")
def test_construct_league_table_integration(
    mock_abbreviations, mock_fixtures, sample_fixtures, team_abbreviations
):
    """Test the full integration of construct_league_table"""
    mock_fixtures.return_value = sample_fixtures
    mock_abbreviations.return_value = team_abbreviations

    table = construct_league_table()

    # Check team name mapping
    assert "ARS" in table.index
    assert "AVL" in table.index

    # Verify top team stats
    top_team = table.iloc[0]
    assert top_team.name == "ARS"
    assert top_team["points"] == 3
    assert top_team["rank"] == 1


def test_construct_raw_table_edge_cases():
    """Test edge cases and unusual scenarios"""
    edge_fixtures = [
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 2,
            "team_h_score": 0,
            "team_a_score": 0,
        },
        {
            "event": 1,
            "finished": True,
            "team_h": 3,
            "team_a": 4,
            "team_h_score": 9,  # High score
            "team_a_score": 0,
        },
    ]

    table = construct_raw_table(edge_fixtures)

    # Check high-scoring team
    team_3 = table[table.index == 3].iloc[0]
    assert team_3["GF"] == 9
    assert team_3["GD"] == 9

    # Check 0-0 draw teams
    team_1 = table[table.index == 1].iloc[0]
    assert team_1["points"] == 1
    assert team_1["GF"] == 0
    assert team_1["GA"] == 0
    assert team_1["D"] == 1


def test_construct_raw_table_validation():
    """Test input validation and error handling"""
    invalid_fixtures = [
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 2,
            # Missing scores
        }
    ]

    with pytest.raises(KeyError):
        construct_raw_table(invalid_fixtures)
