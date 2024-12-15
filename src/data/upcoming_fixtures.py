import pandas as pd
from src.data.fpl_api import (
    get_bootstrap_json,
    get_fixtures_json,
    get_team_abbreviations_map,
)


def get_upcoming_fixtures(horizon: int = 12) -> pd.DataFrame:
    """
    Fetches the upcoming fixtures from the FPL API.
    :param horizon: The number of gameweeks to fetch.
    :return: The upcoming fixtures.
    """
    bootstrap_data = get_bootstrap_json()
    horizon_start_id = get_next_gameweek_id(bootstrap_data)
    horizon_end_id = horizon_start_id + horizon - 1
    raw_fixtures = get_raw_fixtures(horizon_start_id, horizon_end_id)

    team_abbreviations = get_team_abbreviations_map(bootstrap_data)
    fixtures = apply_team_abbreviations(raw_fixtures, team_abbreviations)

    return fixtures


def get_next_gameweek_id(bootstrap_data: dict[str, list | dict]) -> int:
    """
    Gets the ID of the next upcoming gameweek by iterating through the bootstrap data and finding the first event that is not finished.
    :param bootstrap_data: The bootstrap data.
    :return: The ID of the next upcoming gameweek.
    """
    next_gameweek_id = -1
    for event in bootstrap_data["events"]:
        if not event["finished"]:
            next_gameweek_id = event["id"]
            break

    if next_gameweek_id == -1:
        raise Exception("No upcoming gameweek found, come back next season!")

    return next_gameweek_id


def get_raw_fixtures(horizon_start: int, horizon_end: int) -> pd.DataFrame:
    """
    Fetches the raw fixtures from the FPL API.
    :param horizon_start: The ID of the first gameweek to fetch.
    :param horizon_end: The ID of the last gameweek to fetch.
    :return: The raw fixtures.
    """
    data = get_fixtures_json()
    fixtures = []
    for fixture in data:
        if fixture["event"] is None:  # unscheduled postponed game
            continue

        if fixture["event"] < horizon_start:
            continue

        if fixture["event"] <= horizon_end:
            if fixture["finished"]:
                continue
            fixture_details = {
                "gameweek": fixture["event"],
                "home": fixture["team_h"],
                "away": fixture["team_a"],
            }
            fixtures.append(fixture_details)

        else:
            break

    df = pd.DataFrame(fixtures)
    return df


def apply_team_abbreviations(
    fixtures: pd.DataFrame, team_abbreviations: dict[int, str]
) -> pd.DataFrame:
    """
    Converts the team IDs to team abbreviations for the fixtures.
    :param fixtures: The fixtures.
    :param team_abbreviations: The team abbreviations.
    :return: The fixtures with team abbreviations.
    """
    fixtures["home"] = fixtures["home"].map(team_abbreviations)
    fixtures["away"] = fixtures["away"].map(team_abbreviations)
    return fixtures
