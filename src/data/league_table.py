import pandas as pd

from src.data.fpl_api import get_fixtures_json, get_team_abbreviations_map


def construct_league_table() -> pd.DataFrame:
    """
    Constructs the league table using fixtures from the FPL API.
    :return: the league table with the following columns:
        - team: the team name
        - played: the number of games played
        - points: the number of points
        - GD: goal difference
        - GF: the number of goals for
        - GA: the number of goals against
        - W: the number of wins
        - D: the number of draws
        - L: the number of losses
        - rank: the rank of the team (1 to 20)
    """
    raw_fixtures = get_fixtures_json()
    table = construct_raw_table(raw_fixtures)

    team_abbreviations_map = get_team_abbreviations_map()
    table["team"] = table["team"].map(team_abbreviations_map)

    return table


def construct_raw_table(raw_fixtures: list[dict]) -> pd.DataFrame:
    """
    Constructs the league table from the raw fixtures.
    :param raw_fixtures: the raw fixtures
    :return: the league table
    """
    table = {
        team_id: {
            "team": team_id,
            "played": 0,
            "points": 0,
            "GD": 0,
            "GF": 0,
            "GA": 0,
            "W": 0,
            "D": 0,
            "L": 0,
        }
        for team_id in range(1, 21)
    }
    for fixture in raw_fixtures:
        if fixture["event"] is None:
            continue  # skip postponed games

        if not fixture["finished"]:
            break  # stop when first finished game is found

        for team_id, team_score, opponent_score in zip(
            [fixture["team_h"], fixture["team_a"]],
            [fixture["team_h_score"], fixture["team_a_score"]],
            [fixture["team_a_score"], fixture["team_h_score"]],
        ):
            table_entry = table[team_id]

            table_entry["played"] += 1
            table_entry["GF"] += team_score
            table_entry["GA"] += opponent_score
            table_entry["GD"] = table_entry["GF"] - table_entry["GA"]

            if team_score > opponent_score:
                table_entry["W"] += 1
                table_entry["points"] += 3
            elif team_score == opponent_score:
                table_entry["D"] += 1
                table_entry["points"] += 1
            else:
                table_entry["L"] += 1

            table[team_id] = table_entry

    df = pd.DataFrame(table).T
    df = df.sort_values(by=["points", "GD", "GF"], ascending=False)
    # head to head tiebreaks omitted for simplicity. should hopefully not be necessary

    df["rank"] = range(1, 21)

    return df
