import pandas as pd
import requests


def get_upcoming_fixtures(horizon: int = 12) -> pd.DataFrame:
    """
    Fetches the upcoming fixtures from the FPL API.
    :param horizon: The number of gameweeks to fetch.
    :return: The upcoming fixtures.
    """
    bootstrap_data = get_bootstrap_data()
    horizon_start_id = get_next_gameweek_id(bootstrap_data)
    horizon_end_id = horizon_start_id + horizon - 1
    raw_fixtures = get_raw_fixtures(horizon_start_id, horizon_end_id)

    team_abbreviations = get_team_abbreviations(bootstrap_data)
    fixtures = apply_team_abbreviations(raw_fixtures, team_abbreviations)

    return fixtures


def get_bootstrap_data() -> dict[str, list | dict]:
    """
    Fetches the bootstrap data from the FPL API.
    :return: The bootstrap data.
    """
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Error fetching {url}: {res.status_code}")

    data = res.json()
    return data


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
    url = "https://fantasy.premierleague.com/api/fixtures/"
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Error fetching {url}: {res.status_code}")

    data = res.json()
    fixtures = []
    for fixture in data:
        if fixture["event"] is None:  # unscheduled postponed game
            continue

        if fixture["event"] < horizon_start:
            continue

        if fixture["event"] <= horizon_end:
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


def get_team_abbreviations(bootstrap_data: dict[str, list | dict]) -> dict[int, str]:
    """
    Fetches the team abbreviations from the FPL API.
    :param bootstrap_data: The bootstrap data.
    :return: The team abbreviations.
    """
    teams = {team["id"]: team["short_name"] for team in bootstrap_data["teams"]}
    return teams


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
