import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import patch
from src.data.ratings import read_ratings


def test_read_ratings_file_exists(tmp_path):
    """Test that the function can successfully read a valid CSV file"""
    # Create a test CSV file
    test_data = """Attack Strength,Defence Strength
    10,20
    30,40
    50,60"""

    test_file = tmp_path / "ratings.csv"
    test_file.write_text(test_data)

    with patch("pandas.read_csv") as mock_read_csv:
        # Create expected DataFrame
        expected_df = pd.DataFrame(
            {"Attack Strength": [10, 30, 50], "Defence Strength": [20, 40, 60]}
        )
        mock_read_csv.return_value = expected_df

        # Call the function
        result = read_ratings()

        # Verify read_csv was called with correct parameters
        mock_read_csv.assert_called_once_with("data/ratings.csv", index_col=0)

        # Verify the returned DataFrame matches expected
        assert_frame_equal(result, expected_df)


def test_read_ratings_file_not_found():
    """Test that appropriate error is raised when file doesn't exist"""
    with patch("pandas.read_csv", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            read_ratings()


def test_read_ratings_invalid_format():
    """Test handling of CSV with invalid format"""
    with patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError):
        with pytest.raises(pd.errors.EmptyDataError):
            read_ratings()


def test_read_ratings_return_type():
    """Test that the function returns a pandas DataFrame"""
    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.return_value = pd.DataFrame()
        result = read_ratings()
        assert isinstance(result, pd.DataFrame)


def test_read_ratings_index():
    """Test that the function correctly uses the first column as index"""
    test_data = pd.DataFrame(
        {"Attack Strength": [10, 30, 50], "Defence Strength": [20, 40, 60]}
    )

    with patch("pandas.read_csv", return_value=test_data) as mock_read_csv:
        read_ratings()
        mock_read_csv.assert_called_with("data/ratings.csv", index_col=0)
