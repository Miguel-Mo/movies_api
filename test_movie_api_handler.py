from unittest.mock import patch, MagicMock

fake_movies_db = [
    {"imdbID": "tt1111111", "Title": "Inception 1", "Year": 2020},
    {"imdbID": "tt2222222", "Title": "Inception 2", "Year": 2030},
]

mock_firestore = MagicMock()
mock_collection = MagicMock()
mock_doc = MagicMock()
mock_firestore.collection.return_value = mock_collection

mock_collection.order_by.return_value = mock_collection
mock_collection.limit.return_value = mock_collection
mock_collection.offset.return_value = mock_collection

mock_movie_docs = [MagicMock(to_dict=MagicMock(return_value=movie)) for movie in fake_movies_db]
mock_collection.stream.return_value = mock_movie_docs


with patch("google.cloud.firestore.Client", return_value=mock_firestore):
    from api_flask.main import app  

with app.test_client() as client:

    def verify_movies(expected_movies):
        response = client.get("/movies")
        assert response.status_code == 200

        movies = response.get_json()
        print (movies)
        assert len(movies) == len(expected_movies)

        for i, expected in enumerate(expected_movies):
            assert movies[i]["Title"] == expected["Title"]

    def test_get_movies():
        verify_movies(fake_movies_db)  


if __name__ == "__main__":
    test_get_movies()
    # TO DO I need to investigate how to mock the API responses or even if 
    # the code is written well so that unit testing can be done. I ran out of time 
    # and this is what I have achieved.
    # test_post_movie() 
    # test_delete_movie()
    print("Tests passed!")
