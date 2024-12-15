import random
import click
import pandas as pd
import numpy as np
from tqdm import tqdm

from src.data import get_data
from src.simulation.goals_probability_distribution import add_goal_proba_distributions
from src.simulation.manager_points import calculate_manager_points
from src.simulation.match_simulation import simulate_match, update_table

random.seed(0)


@click.command()
@click.option("--horizon", default=12, help="The number of gameweeks to simulate.")
@click.option(
    "--num-simulations", default=10_000, help="The number of simulations to run."
)
@click.option("--cpus", default=1, help="The number of CPUs to use.")
def main(horizon: int = 12, num_simulations: int = 100, cpus: int = 1):
    fixtures, table, ratings, manager_prices = get_data(horizon=horizon)
    fixtures = add_goal_proba_distributions(fixtures, ratings)
    results = run_simulations(
        fixtures, table, num_simulations=num_simulations, cpus=cpus
    )
    save_results(results, manager_prices)


def run_simulations(
    fixtures: pd.DataFrame,
    table: pd.DataFrame,
    num_simulations: int,
    cpus: int,
) -> pd.DataFrame:
    initial_result = simulate_horizon(fixtures, table)
    results = np.zeros((num_simulations, *initial_result.shape))
    results[0] = initial_result.values
    # TODO: Parallelize
    for i in tqdm(range(1, num_simulations), initial=1, total=num_simulations):
        result = simulate_horizon(fixtures, table)
        results[i] = result.values

    mean_results = results.mean(axis=0)
    df = pd.DataFrame(
        mean_results, index=initial_result.index, columns=initial_result.columns
    )
    return df


def simulate_horizon(fixtures: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    points = {}
    current_week = -1
    running_table = table.copy()
    start_of_gw_table = table.copy()
    for fixture in fixtures.itertuples():
        if fixture.gameweek != current_week:
            current_week = fixture.gameweek
            running_table = running_table.sort_values(
                by=["points", "GD", "GF"], ascending=False
            )
            running_table["rank"] = range(1, 21)
            start_of_gw_table = running_table.copy()

        home_goals, away_goals = simulate_match(
            fixture.home_goal_distribution, fixture.away_goal_distribution
        )
        running_table = update_table(
            running_table, fixture.home, home_goals, fixture.away, away_goals
        )

        teams = [fixture.home, fixture.away]
        goals = [home_goals, away_goals]
        for idx in range(2):
            team_rank = start_of_gw_table.at[teams[idx], "rank"]
            oppo_rank = start_of_gw_table.at[teams[1 - idx], "rank"]

            manager_points = calculate_manager_points(
                team_rank, oppo_rank, goals[idx], goals[1 - idx]
            )

            points[teams[idx]] = points.get(teams[idx], {})
            points[teams[idx]][current_week] = (
                points[teams[idx]].get(current_week, 0) + manager_points
            )

    df = pd.DataFrame(points).T
    return df


def save_results(results: pd.DataFrame, prices: pd.DataFrame, path="../../data/am_pts.csv") -> None:
    results = results.rename(columns={
        col: f"{col}_Pts"
        for col in results.columns
    })
    prices = prices.join(results)
    prices.to_csv(path)


if __name__ == "__main__":
    main()
