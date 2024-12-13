import requests
from typing import Any


def get_bootstrap_json() -> dict[str, list | dict]:
    """
    Fetches the bootstrap data from the FPL API.
    :return: The bootstrap data json.
    """
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    data = make_request(url)
    return data


def get_fixtures_json() -> list[dict]:
    """
    Fetches the fixtures from the FPL API.
    :return: The fixtures list json.
    """
    url = "https://fantasy.premierleague.com/api/fixtures/"
    data = make_request(url)
    return data


def make_request(url: str) -> Any:
    """
    Makes a request to the FPL API with error handling.
    :param url: The URL to make the request to.
    :return: The json response from the API.
    """
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f'Error fetching "{url}": {res.status_code}')
    return res.json()
