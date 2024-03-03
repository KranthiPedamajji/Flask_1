from flask import Flask, render_template, redirect, Response, request
import Models.MovieDatabase as MovieDatabase
from functools import wraps
import time
import matplotlib.pyplot as plt
from io import BytesIO
import json
import mplcursors

# Create an instance of the Flask application
app = Flask(__name__)

# Create an instance of the MovieDatabase class
movie_db = MovieDatabase.MovieDatabase()

# Variable to store timing information
timing_info = {"get_and_store_movies": 0.0}

def timing_decorator(func):
    """Decorator to measure the execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        timing_info[func.__name__] = elapsed_time
        return result
    return wrapper

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/load_movies', methods=['POST'])
def load_movies():
    """Handle the POST request to load all movies into Redis."""
    load_all_movies()  # Load movies into Redis
    return redirect('/')

def load_all_movies():
    """Load movies into Redis for the years 2010 to 2024."""
    for year in range(2010, 2025):
        movies_data = movie_db.get_movies_by_year(str(year))
        movie_db.store_movies_in_redis(str(year), movies_data)

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
    movie_counts = [669, 687, 701, 708, 737, 742, 873, 792, 334, 406, 449]

    # Plotting
    plt.figure(figsize=(12, 8))
    plt.plot(years, movie_counts, marker='o')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.title('Movies by Year')
    plt.grid(True)
    plt.tight_layout()

    # Set tick positions for each year
    plt.xticks(years)

    # Add tooltips using mplcursors
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f"Year: {sel.target[0]}\nMovies: {sel.target[1]}"))

    # Save the plot to a BytesIO object
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

# Run the application if executed as the main script
if __name__ == '__main__':
    app.run(debug=True)
