import pandas as pd
from typing import Tuple

from src.data.upcoming_fixtures import get_upcoming_fixtures
from src.data.league_table import construct_league_table
from src.data.read_csv import read_ratings
from src.data.read_csv import read_manager_prices


def get_data(
    horizon: int = 12,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads data from the FPL API and other sources.
    :param horizon: The number of gameweeks to simulate.
    :return: A tuple of fixtures, league table, ratings, and manager prices.
    """
    fixtures = get_upcoming_fixtures(horizon=horizon)
    league_table = construct_league_table()
    ratings = read_ratings()
    manager_prices = read_manager_prices()
    return fixtures, league_table, ratings, manager_prices
