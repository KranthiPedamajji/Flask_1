import Models.MovieDatabase as MovieDatabase
import json
from flask import Flask, Response, redirect, render_template, request
from functools import wraps
import time
import matplotlib.pyplot as plt
from io import BytesIO
import mplcursors

app = Flask(__name__)
movie_db = MovieDatabase.MovieDatabase()

@app.route('/')
def index():
    """Rendering the index page."""
    return render_template('index.html')

def load_all_movies():
    """Load movies into Redis for the years 2010 to 2024."""
    for year in range(2010, 2025):
        movies_data = movie_db.get_movies_by_year(str(year))
        movie_db.store_movies_in_redis(str(year), movies_data)

@app.route('/load_movies', methods=['POST'])
def load_movies():
    """Handle the POST request to load all movies into Redis."""
    load_all_movies()
    return redirect('/')

timing_info = {"get_and_store_movies": 0.0}

def timing_decorator(func):
    """Decorator to measure the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        timing_info[func.__name__] = elapsed_time
        return result
    return wrapper

@app.route('/movies', methods=['POST'])
@timing_decorator
def get_and_store_movies():
    """Handle the POST request to get and store movies."""
    selected_year = request.form.get('year')
    
    if selected_year:
        key = f'movies_{selected_year}'
        redis_data = movie_db.redis_client.get(key)

        if redis_data:
            movies = json.loads(redis_data)
        else:
            movies_data = movie_db.get_movies_by_year(selected_year)
            movie_db.store_movies_in_redis(selected_year, movies_data)
            redis_data = movie_db.redis_client.get(key)
            movies = json.loads(redis_data)

        return render_template('movies.html', movies=movies, timing_info=timing_info)

    return redirect('/')

def plot_movies_by_year():
    """Plot the number of movies by year."""
    years = list(range(2012, 2023))
    movie_counts = []

    for year in years:
        key = f'movies_{year}'
        redis_data = movie_db.redis_client.get(key)

        if redis_data:
            movies = json.loads(redis_data)
            movie_counts.append(len(movies.get('movie_results', [])))
        else:
            movie_counts.append(0)

    movie_counts1 = [669, 687, 701, 708, 737, 742, 873, 792, 334, 406, 449]

    # Combine the two lists by summing corresponding elements
    combined_counts = [count + count1 for count, count1 in zip(movie_counts, movie_counts1)]

    plt.figure(figsize=(12, 8))
    plt.plot(years, combined_counts, marker='o')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.title('Movies by Year')
    plt.grid(True)
    plt.tight_layout()

    plt.xticks(years)

    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f"Year: {sel.target[0]}\nMovies: {sel.target[1]}"))

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()

    return img_buffer.getvalue()

@app.route('/plot_movies', methods=['GET'])
def plot_movies():
    """Handle the GET request to plot movies by year."""
    img_data = plot_movies_by_year()
    return Response(img_data, content_type='image/png')


def search_movies(search_query):
    """Search movies within the loaded Redis data."""
    search_results = []

    # Iterate through movies for the years 2010 to 2024
    for year in range(2010, 2025):
        key = f'movies_{year}'
        redis_data = movie_db.redis_client.get(key)

        if redis_data:
            movies = json.loads(redis_data)

            # Filter movies based on the search query
            if 'movie_results' in movies:
                year_result = {
                    'year': year,
                    'movies': [
                        movie for movie in movies['movie_results']
                        if search_query.lower() in movie.get('title', '').lower()
                    ]
                }

                # Append the year result only if there are matching movies
                if year_result['movies']:
                    search_results.append(year_result)
    print(search_results)
    return search_results


@app.route('/search_movies', methods=['POST'])
def search_movies_route():
    """Handle the POST request to search for movies."""
    search_query = request.form.get('search_query')

    if search_query:
        search_results = search_movies(search_query)
        return render_template('search_results.html', search_results=search_results, search_query=search_query)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
