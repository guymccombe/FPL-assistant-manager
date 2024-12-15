import pandas as pd


def read_ratings() -> pd.DataFrame:
    ratings = pd.read_csv("../../data/ratings.csv", index_col=0)
    return ratings


def read_manager_prices() -> pd.DataFrame:
    manager_prices = pd.read_csv("../../data/manager_prices.csv", index_col=0)
    return manager_prices
