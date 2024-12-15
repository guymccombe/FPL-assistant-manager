import pandas as pd


def read_ratings() -> pd.DataFrame:
    ratings = pd.read_csv("../../data/ratings.csv", index_col=0)
    return ratings
