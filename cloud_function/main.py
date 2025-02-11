import requests
import os
import logging
from google.cloud import firestore

db = firestore.Client(database="bdmovies", project="vocal-tempo-450318-s8")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

logging.basicConfig(level=logging.INFO)


def fetch_movies(request):
    """Cloud Function to fetch movies from OMDB API and store in Firestore."""
    logging.info("Starting function...")
    url = f"http://www.omdbapi.com/?s=movie&type=movie&apikey={OMDB_API_KEY}&page="

    try:
        # Check if Firestore already has movies
        movies_ref = db.collection("movies")
        if len(list(movies_ref.limit(1).get())) > 0:
            logging.info("Database already contains movies.")
            return ("The database already contains movies. No need to fetch more.", 200)

        # Fetch 100 movies (10 pages of 10 movies each)
        for page in range(1, 11):
            logging.info(f"Fetching page {page}...")
            response = requests.get(url + str(page))
            movies = response.json().get("Search", [])

            for movie in movies:
                # Save each movie to Firestore
                movies_ref.document(movie["imdbID"]).set(movie)
                logging.info(f'Movie saved: {movie["Title"]}')

        return ("Movies fetched and stored in Firestore.", 200)

    except Exception as e:
        logging.error(f"Error in function: {str(e)}")
        return (f"Internal server error: {str(e)}", 500)
