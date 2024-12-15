from scipy.stats import poisson
import pandas as pd


def predict_xg(attack_rating: float, defence_rating: float, is_home: bool) -> float:
    """
    Predicts the xG of a team based on their attack rating and defence rating.
    :param attack_rating: The attack rating of the team.
    :param defence_rating: The defence rating of the team.
    :param is_home: Whether the team is at home or away.
    :return: The predicted xG of the team.
    """
    # average xG for home/away teams obtained from FBref: https://fbref.com
    HOME_XG = 1.712665406
    AWAY_XG = 1.351606805
    average_xg = HOME_XG + AWAY_XG / 2
    if is_home:
        home_away_scale = HOME_XG / average_xg
    else:
        home_away_scale = AWAY_XG / average_xg

    return home_away_scale * attack_rating * defence_rating


def discrete_goal_distribution(xg: float, max_number_of_goals: int = 7) -> [float]:
    """
    Calculates the probability of each number of goals scored for a given xG.
    Assumes that goals are scored independently and that they are Poisson distributed.
    :param xg: The predicted xG of the team.
    :param max_number_of_goals: The maximum number of goals to consider.
    :return: A list of probabilities for each number of goals scored, starting from 0.
    """
    probabilities = [poisson.pmf(k=k, mu=xg) for k in range(0, max_number_of_goals + 1)]
    return probabilities


def add_goal_proba_distributions(
    fixtures: pd.DataFrame, ratings: pd.DataFrame
) -> pd.DataFrame:
    home_goal_distributions = []
    away_goal_distributions = []
    for fixture in fixtures.itertuples():
        teams = [fixture.home, fixture.away]
        for idx, (team, oppo) in enumerate(zip(teams, reversed(teams))):
            attack_rating = ratings.loc[team, "Attack Strength"]
            defence_rating = ratings.loc[oppo, "Defence Strength"]
            is_home = idx == 0

            xg = predict_xg(attack_rating, defence_rating, is_home)
            goal_probabilities = discrete_goal_distribution(xg)

            if is_home:
                home_goal_distributions.append(goal_probabilities)
            else:
                away_goal_distributions.append(goal_probabilities)

    fixtures["home_goal_distribution"] = home_goal_distributions
    fixtures["away_goal_distribution"] = away_goal_distributions
    return fixtures
