from http import HTTPStatus
import http.server
import json
import os
import logging
import requests
from urllib.parse import unquote, urlparse, parse_qs
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)

# Configure the Firestore client
db = firestore.Client(database="bdmovies", project="vocal-tempo-450318-s8")

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
PORT = int(os.getenv("PORT", 8080))


class MovieAPIHandler(http.server.BaseHTTPRequestHandler):

    # Endpoint: GET /movies
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/movies":
            query_params = parse_qs(parsed_path.query)

            # Default values
            page = int(query_params.get("page", ["1"])[0])
            limit = int(query_params.get("limit", ["10"])[0])
            offset = (page - 1) * limit 

            # Order movies by title
            movies_ref = (
                db.collection("movies").order_by("Title").limit(limit).offset(offset)
            )
            movies = [doc.to_dict() for doc in movies_ref.stream()]

            self._send_response(HTTPStatus.OK, movies)
        elif parsed_path.path.startswith("/movies/"):
            # Get movie by title
            title = unquote(
                parsed_path.path.split("/")[2]
            )  # Decode spaces (%20 -> " ")
            print(title)
            movies_ref = db.collection("movies").where("Title", "==", title).limit(1)
            try:
                movie = next(movies_ref.stream(), None)
            except Exception as e:
                logging.error(f"Error fetching movie: {e}")
                self._send_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Error fetching movie"})
                return
            if movie:
                self._send_response(HTTPStatus.OK, movie.to_dict())
            else:
                self._send_response(HTTPStatus.BAD_REQUEST, ErrorMessages.NO_MOVIE_MESSAGE)
        else:
            self._send_response(HTTPStatus.BAD_REQUEST, ErrorMessages.NO_ENDPOINT_MESSAGE)

    # Endpoint: POST /movies
    def do_POST(self):
        if self.path == "/movies":
            # Read request body
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            # Get movie title
            title = data.get("title")
            if not title:
                self._send_response(HTTPStatus.BAD_REQUEST, ErrorMessages.NO_TITLE_MESSAGE)
                return

            # Fetch movie details from OMDB API
            response = requests.get(
                f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
            )
            movie = response.json()
            if movie.get("Response") == "True":
                # Save movie to Firestore
                db.collection("movies").document(movie["imdbID"]).set(movie)
                self._send_response(HTTPStatus.CREATED, movie)
            else:
                self._send_response(HTTPStatus.BAD_REQUEST, ErrorMessages.NO_MOVIE_MESSAGE)
        else:
            self._send_response(HTTPStatus.BAD_REQUEST, ErrorMessages.NO_ENDPOINT_MESSAGE)

    # Endpoint: DELETE /movies/{id}
    def do_DELETE(self):
        if self.path.startswith("/movies/"):
            # Verify basic authentication
            if not self._authenticate():
                self.send_response(HTTPStatus.UNAUTHORIZED)
                self.send_header("WWW-Authenticate", 'Basic realm="Restricted access"')
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(ErrorMessages.UNAUTHORIZED_MESSAGE).encode())
                return

            movie_id = self.path.split("/")[2]

            # Delete movie from Firestore
            movie_ref = db.collection("movies").document(movie_id)
            if not movie_ref.get().exists:
                self._send_response(HTTPStatus.NOT_FOUND, ErrorMessages.NO_MOVIE_MESSAGE)
                return
            movie_ref.delete()
            self._send_response(HTTPStatus.OK, {"success": True})
        else:
            self._send_response(HTTPStatus.NOT_FOUND, ErrorMessages.NO_ENDPOINT_MESSAGE)

    # Basic auth method
    def _authenticate(self):
        auth_header = self.headers.get("Authorization")
        if auth_header:
            auth_type, auth_token = auth_header.split(" ")
            if auth_type.lower() == "basic":
                return True
        return False
    
    def _send_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())


class ErrorMessages:
    NO_ENDPOINT_MESSAGE = {"error": "Endpoint not found"}
    NO_MOVIE_MESSAGE = {"error": "Movie not found"}
    NO_TITLE_MESSAGE = {"error": "The 'title' field is required"}
    UNAUTHORIZED_MESSAGE = {"error": "Unauthorized"}


if __name__ == "__main__":
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, MovieAPIHandler)
    print(f"Servidor iniciado en http://localhost:{PORT}")
    httpd.serve_forever()
