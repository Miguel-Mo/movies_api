# Python Programmer Test

This project implements all the requirements of the Python Programmer Test, including fetching movie data from the OMDB API, storing it in a database, and providing a REST API for managing movie records. The application is deployed on Google Cloud Platform (GCP) using Cloud Functions and Cloud Run.

## Features Implemented

### 1. Fetch Test Data via HTTPS from OMDB API

- Retrieves 100 movies from the OMDB API (selection criteria chosen arbitrarily).
- Saves the movies in a database.
- This operation runs only once when the database is empty.

### 2. Implemented API

- Provides an endpoint to retrieve a list of movies from the database.
- Supports pagination with a default limit of 10 movies per response.
- Allows sorting of data by Title.
- Provides an endpoint to retrieve a single movie by its title.
- Supports adding new movies by title, fetching details from the OMDB API, and storing them in the database.
- Includes an endpoint to remove a movie from the database using its ID.
- Ensures the delete operation is restricted to authorized users.

### 3. Unit Tests

- Comprehensive unit tests cover all implemented features to ensure robustness and correctness.
- For the Cloud Run APIs, only the `GET /movies` test was successfully implemented due to challenges in mocking Firestore.

## Deployment

The project is deployed using Google Cloud services:

- **Cloud Function:** Fetches movie data from OMDB API and stores it in the database.
  - [Fetch Movies Cloud Function](https://europe-southwest1-vocal-tempo-450318-s8.cloudfunctions.net/fetch-movies)

- **Cloud Run (Standalone Python Implementation):** An API service implemented purely in Python.
  - [Cloud Run Python API](https://movies-api-1054884846779.europe-southwest1.run.app)

- **Cloud Run (Flask + Waitress Implementation):** A more flexible and scalable solution using Flask and Waitress.
  - [Cloud Run Flask API](https://movies-api-flask-1054884846779.europe-southwest1.run.app/movies?limit=1&page=6)

## Notes

Initially, a Cloud Run service was developed using only Python, as inferred from the interview requirements. However, a second version using Flask and Waitress was implemented to provide a more straightforward and versatile solution.

This project demonstrates proficiency in API development, cloud deployment, and database management within GCP.

