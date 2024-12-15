import random
from typing import Tuple

import pandas as pd

random.seed(0)


def simulate_match(
    home_goal_distribution: [float], away_goal_distribution: [float]
) -> Tuple[int, int]:
    """
    Simulates a match between two teams based on their goal distributions.
    :param home_goal_distribution: The goal distribution for the home team.
    :param away_goal_distribution: The goal distribution for the away team.
    :return: The number of goals scored by the home team and the number of goals scored by the away team.
    """
    home_goals = random.choices(
        population=range(len(home_goal_distribution)),
        weights=home_goal_distribution,
        k=1,
    )[0]
    away_goals = random.choices(
        population=range(len(away_goal_distribution)),
        weights=away_goal_distribution,
        k=1,
    )[0]
    return home_goals, away_goals


def update_table(
    table: pd.DataFrame,
    home_team: str,
    home_goals: int,
    away_team: str,
    away_goals: int,
) -> pd.DataFrame:
    for team, gf, ga in zip(
        [home_team, away_team], [home_goals, away_goals], [away_goals, home_goals]
    ):
        table.at[team, "GF"] += gf
        table.at[team, "GD"] += gf - ga

    if home_goals > away_goals:
        table.at[home_team, "points"] += 3
    elif home_goals < away_goals:
        table.at[away_team, "points"] += 3
    else:
        table.at[home_team, "points"] += 1
        table.at[away_team, "points"] += 1

    return table
