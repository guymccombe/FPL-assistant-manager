def calculate_manager_points(
    team_rank: int, oppo_rank: int, goals_for: int, goals_against: int
) -> int:
    """
    Calculates the manager points for a match between two teams.
    :param team_rank: The rank of the home team.
    :param oppo_rank: The rank of the away team.
    :param goals_for: The number of goals scored by the home team.
    :param goals_against: The number of goals scored by the away team.
    :return: The manager points for the match.
    """
    points = goals_for  # 1 point per goal
    if goals_against == 0:
        points += 2  # 2 points for a clean sheet

    if goals_for > goals_against:
        points += 6  # 6 points for a win
        if team_rank >= oppo_rank + 5:
            points += 10  # 10 bonus points if the team is 5 places behind the opponent

    elif goals_for == goals_against:
        points += 3  # 3 points for a draw
        if team_rank >= oppo_rank + 5:
            points += 5  # 5 bonus points if the team is 5 places behind the opponent

    # no points for a loss

    return points
