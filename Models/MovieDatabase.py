import requests
import json
import redis

class MovieDatabase:
    """
    MovieDatabase class for interacting with a movie database API and Redis.

    Attributes:
    - api_url (str): The base URL of the movie database API.
    - headers (dict): Headers for making requests to the movie database API.
    - redis_client (StrictRedis): Redis client for interacting with a Redis database.
    """

    def __init__(self):
        """
        Initializes a MovieDatabase object.

        Sets up the API URL, headers, and connects to the local Redis database.
        """
        self.api_url = "https://movies-tv-shows-database.p.rapidapi.com/"
        self.headers = {
            "Type": "get-movies-byyear",
            "X-RapidAPI-Key": "202fdfb8c7mshef5d2122d4c5d9ap1210b4jsn91783e932c90",
            "X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
        }
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_movies_by_year(self, year):
        """
        Retrieves movies for a specific year from the movie database API.

        Args:
        - year (str): The year for which movies are requested.

        Returns:
        - dict: JSON response containing movie data.
        """
        querystring = {"year": str(year), "page": "1"}
        response = requests.get(self.api_url, headers=self.headers, params=querystring)
        return response.json()

    def store_movies_in_redis(self, year, movies_data):
        """
        Stores movie data in Redis for a specific year.

        Args:
        - year (str): The year for which movies are stored.
        - movies_data (dict): Movie data to be stored in Redis.
        """
        key = f'movies_{year}'
        json_data = json.dumps(movies_data)
        print(f"Storing JSON data in Redis: {json_data}")
        self.redis_client.set(key, json_data)
