from http import HTTPStatus
from flask import Flask, request, jsonify, abort
import os
import logging
import requests
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

db = firestore.Client(database="bdmovies", project="vocal-tempo-450318-s8")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


@app.route("/movies", methods=["GET"])
def get_movies():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    offset = (page - 1) * limit

    movies_ref = db.collection("movies").order_by("Title").limit(limit).offset(offset)
    movies = [doc.to_dict() for doc in movies_ref.stream()]

    return jsonify(movies)


@app.route("/movies/<string:title>", methods=["GET"])
def get_movie_by_title(title):
    movies_ref = db.collection("movies").where("Title", "==", title).limit(1)
    movie = next(movies_ref.stream(), None)
    if movie:
        return jsonify(movie.to_dict())
    else:
        abort(404, description="Movie not found")


@app.route("/movies", methods=["POST"])
def add_movie():
    data = request.json
    title = data.get("title")
    if not title:
        abort(HTTPStatus.BAD_REQUEST, description="The 'title' field is required")

    response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}")
    movie = response.json()
    if movie.get("Response") == "True":
        db.collection("movies").document(movie["imdbID"]).set(movie)
        return jsonify(movie), HTTPStatus.CREATED
    else:
        abort(404, description="Movie not found in OMDB")


@app.route("/movies/<string:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), HTTPStatus.UNAUTHORIZED

    db.collection("movies").document(movie_id).delete()
    return jsonify({"success": True})


def authenticate(request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_type, _ = auth_header.split(" ")
        if auth_type.lower() == "basic":
            return True
    return False


if __name__ == "__main__":
    from waitress import serve

    port = int(os.environ.get("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)
