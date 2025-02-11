import unittest
from unittest.mock import patch, MagicMock

# Mock Firestore before importing main to avoid some conflicts with google auth
with patch("google.cloud.firestore.Client", autospec=True) as mock_firestore_client:
    from cloud_function.main import fetch_movies


class TestFetchMovies(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_movies_database_already_contains_movies(self, mock_get):
        mock_firestore_client.return_value.collection.return_value.limit.return_value.get.return_value = [
            MagicMock()
        ]

        response, status_code = fetch_movies(None)
        self.assertEqual(status_code, 200)
        self.assertIn("The database already contains movies", response)

        mock_get.assert_not_called()

    @patch("requests.get")
    def test_fetch_movies_fetches_and_stores_movies(self, mock_get):
        mock_firestore_client.return_value.collection.return_value.limit.return_value.get.return_value = (
            []
        )

        mock_get.return_value.json.return_value = {
            "Search": [
                {"Title": "Movie 1", "imdbID": "tt1234567"},
                {"Title": "Movie 2", "imdbID": "tt2345678"},
            ]
        }

        response, status_code = fetch_movies(None)
        self.assertEqual(status_code, 200)
        self.assertIn("Movies fetched and stored in Firestore", response)

        self.assertEqual(mock_get.call_count, 10)
        mock_firestore_client.return_value.collection.return_value.document.return_value.set.assert_any_call(
            {"Title": "Movie 1", "imdbID": "tt1234567"}
        )
        mock_firestore_client.return_value.collection.return_value.document.return_value.set.assert_any_call(
            {"Title": "Movie 2", "imdbID": "tt2345678"}
        )

    @patch("requests.get")
    def test_fetch_movies_handles_exception(self, mock_get):
        mock_get.side_effect = Exception("API Error")

        response, status_code = fetch_movies(None)
        self.assertEqual(status_code, 500)
        self.assertIn("Internal server error", response)


if __name__ == "__main__":
    unittest.main()
