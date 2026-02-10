#!/usr/bin/env python3
"""
IMDB Movie Browser - Flask Web Application
Based on imdb_gui_gpt.py

ARCHITECTURE:
- Flask web server with SQLite backend
- RESTful API for movie filtering
- Responsive HTML/CSS interface
- Uses same database as desktop GUI (imdb_dataset.db)

LICENSE NOTE:
This app uses IMDB's non-commercial datasets.
IMDB Attribution: Information courtesy of IMDb (https://www.imdb.com). Used with permission.
For commercial use, contact: licensing@imdb.com

TO ADD NEW FEATURES:
1. Add route function below (search for "# Routes")
2. Update build_query() if filtering movies
3. Add HTML template in templates/
4. Update static/css/style.css for styling
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from typing import Dict, List, Tuple

app = Flask(__name__)

# Configuration
# Check if database is in same directory (production) or parent directory (development)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'imdb_dataset.db')
if not os.path.exists(DATABASE_PATH):
    # Try parent directory (for local development)
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'imdb_dataset.db')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# ============================================================================
# Language and Country Code Mappings (same as GUI)
# ============================================================================

# ISO 639-1 language codes (abbreviated for web - full list in GUI)
LANGUAGE_NAMES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'it': 'Italian',
    'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ru': 'Russian', 'pt': 'Portuguese',
    'hi': 'Hindi', 'ar': 'Arabic', 'tr': 'Turkish', 'pl': 'Polish', 'nl': 'Dutch',
    'sv': 'Swedish', 'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish', 'cs': 'Czech',
    'hu': 'Hungarian', 'ro': 'Romanian', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian',
}

# ISO 3166-1 country codes
COUNTRY_NAMES = {
    'US': 'United States', 'GB': 'United Kingdom', 'IN': 'India', 'FR': 'France', 'DE': 'Germany',
    'JP': 'Japan', 'IT': 'Italy', 'ES': 'Spain', 'CA': 'Canada', 'AU': 'Australia',
    'KR': 'South Korea', 'CN': 'China', 'RU': 'Russia', 'BR': 'Brazil', 'MX': 'Mexico',
    'NL': 'Netherlands', 'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland',
}

def get_language_name(code: str) -> str:
    """Convert language code to full name"""
    if not code:
        return ""
    return LANGUAGE_NAMES.get(code.lower(), code.upper())

def get_country_name(code: str) -> str:
    """Convert country code to full name"""
    if not code:
        return ""
    return COUNTRY_NAMES.get(code.upper(), code.upper())

# ============================================================================
# Database Functions
# ============================================================================

def get_db_connection():
    """
    Create optimized SQLite connection
    Same optimizations as GUI version
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    # Performance optimizations (same as GUI)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA cache_size=-64000")  # 64MB cache
    cur.execute("PRAGMA temp_store=MEMORY")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.execute("PRAGMA mmap_size=268435456")  # 256MB mmap

    return conn

def get_database_stats() -> Dict:
    """Get database statistics for homepage"""
    conn = get_db_connection()
    cur = conn.cursor()

    stats = {}

    # Total movies
    cur.execute("SELECT COUNT(*) FROM movies")
    stats['total_movies'] = cur.fetchone()[0]

    # Unique genres
    cur.execute("SELECT DISTINCT genres FROM movies")
    genre_set = set()
    for row in cur.fetchall():
        if row[0]:
            genre_set.update(row[0].split("|"))
    stats['genres'] = sorted(g for g in genre_set if g)

    # Check if language/country columns exist
    try:
        cur.execute("SELECT DISTINCT language FROM movies WHERE language IS NOT NULL AND language != ''")
        language_codes = [r[0] for r in cur.fetchall()]
        stats['languages'] = [(code, get_language_name(code)) for code in language_codes]
        stats['languages'].sort(key=lambda x: x[1])
        stats['has_language'] = True
    except sqlite3.OperationalError:
        stats['languages'] = []
        stats['has_language'] = False

    try:
        cur.execute("SELECT DISTINCT country FROM movies WHERE country IS NOT NULL AND country != ''")
        country_codes = [r[0] for r in cur.fetchall()]
        stats['countries'] = [(code, get_country_name(code)) for code in country_codes]
        stats['countries'].sort(key=lambda x: x[1])
        stats['has_country'] = True
    except sqlite3.OperationalError:
        stats['countries'] = []
        stats['has_country'] = False

    # Year range
    cur.execute("SELECT MIN(year), MAX(year) FROM movies")
    min_year, max_year = cur.fetchone()
    stats['year_range'] = (min_year or 1900, max_year or 2030)

    conn.close()
    return stats

def build_query(filters: Dict) -> Tuple[str, List]:
    """
    Build SQL query from filter parameters

    TO ADD NEW FILTER:
    1. Add parameter to filters dict
    2. Add SQL condition below
    3. Update HTML form in templates/index.html

    Args:
        filters: Dictionary of filter parameters from request

    Returns:
        (query_string, params_list)
    """
    # Determine which columns are available
    conn = get_db_connection()
    cur = conn.cursor()

    # Check column availability (same as GUI)
    has_language = False
    has_country = False
    try:
        cur.execute("SELECT language FROM movies LIMIT 1")
        has_language = True
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("SELECT country FROM movies LIMIT 1")
        has_country = True
    except sqlite3.OperationalError:
        pass

    conn.close()

    # Build SELECT statement
    base_cols = 'imdb_id, title, year, rating, votes, duration_mins, duration_text'
    optional_cols = []
    if has_language:
        optional_cols.append('language')
    if has_country:
        optional_cols.append('country')
    optional_cols.extend(['genres', 'directors', 'writers', '"cast"'])

    query = f'SELECT {base_cols}, {", ".join(optional_cols)} FROM movies WHERE 1=1'
    params = []

    # Title search
    title = filters.get('title', '').strip()
    if title:
        query += " AND title LIKE ? COLLATE NOCASE"
        params.append(f"%{title}%")

    # Year range
    year_from = filters.get('year_from')
    if year_from:
        query += " AND year >= ?"
        params.append(int(year_from))

    year_to = filters.get('year_to')
    if year_to:
        query += " AND year <= ?"
        params.append(int(year_to))

    # Rating range
    rating_min = filters.get('rating_min')
    if rating_min:
        query += " AND rating >= ?"
        params.append(float(rating_min))

    rating_max = filters.get('rating_max')
    if rating_max:
        query += " AND rating <= ?"
        params.append(float(rating_max))

    # Votes minimum
    votes_min = filters.get('votes_min')
    if votes_min and int(votes_min) > 0:
        query += " AND votes >= ?"
        params.append(int(votes_min))

    # Genres (include/exclude)
    genres_include = filters.get('genres_include', [])
    if isinstance(genres_include, str):
        genres_include = [genres_include]

    genres_exclude = filters.get('genres_exclude', [])
    if isinstance(genres_exclude, str):
        genres_exclude = [genres_exclude]

    genre_mode = filters.get('genre_mode', 'OR')

    # Include genres
    if genres_include:
        if genre_mode in ('AND', 'ONLY'):
            # All selected genres must be present (ONLY also post-filters in api_search)
            for g in genres_include:
                query += " AND genres LIKE ?"
                params.append(f"%{g}%")
        else:  # OR
            placeholders = " OR ".join(["genres LIKE ?"] * len(genres_include))
            query += f" AND ({placeholders})"
            params.extend([f"%{g}%" for g in genres_include])

    # Exclude genres
    if genres_exclude:
        for g in genres_exclude:
            query += " AND genres NOT LIKE ?"
            params.append(f"%{g}%")

    # Director search - supports wildcards (*), comma-separated names, minus (-) exclude
    director = filters.get('director', '').strip()
    if director:
        for term in [t.strip() for t in director.split(',') if t.strip()]:
            if term.startswith('-'):
                name_sql = term[1:].strip().replace('*', '%')
                if '%' not in name_sql:
                    name_sql = f'%{name_sql}%'
                query += " AND directors NOT LIKE ?"
                params.append(name_sql)
            else:
                name_sql = term.replace('*', '%')
                if '%' not in name_sql:
                    name_sql = f'%{name_sql}%'
                query += " AND directors LIKE ?"
                params.append(name_sql)

    # Cast search - supports wildcards (*), comma-separated names, minus (-) exclude
    # e.g.: "Tom Hanks, *Sara, Sar*, -Brad Pitt"
    cast = filters.get('cast', '').strip()
    if cast:
        for term in [t.strip() for t in cast.split(',') if t.strip()]:
            if term.startswith('-'):
                name_sql = term[1:].strip().replace('*', '%')
                if '%' not in name_sql:
                    name_sql = f'%{name_sql}%'
                query += ' AND "cast" NOT LIKE ?'
                params.append(name_sql)
            else:
                name_sql = term.replace('*', '%')
                if '%' not in name_sql:
                    name_sql = f'%{name_sql}%'
                query += ' AND "cast" LIKE ?'
                params.append(name_sql)

    # Language filter
    if has_language:
        language = filters.get('language', '').strip()
        if language and language != '(All)':
            query += " AND language = ?"
            params.append(language)

    # Country filter
    if has_country:
        country = filters.get('country', '').strip()
        if country and country != '(All)':
            query += " AND country = ?"
            params.append(country)

    # Sorting
    sort_by = filters.get('sort_by', 'rating')
    sort_order = filters.get('sort_order', 'DESC')

    # Map frontend column names to database columns
    sort_map = {
        'title': 'title',
        'year': 'year',
        'rating': 'rating',
        'votes': 'votes',
        'duration': 'duration_mins'
    }

    sort_column = sort_map.get(sort_by, 'rating')
    query += f" ORDER BY {sort_column} {sort_order}"

    # Limit results for web (prevent huge responses)
    limit = filters.get('limit', 100)
    query += f" LIMIT {limit}"

    return query, params

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """
    Homepage with search form
    """
    stats = get_database_stats()
    return render_template('index.html', **stats)

@app.route('/api/search', methods=['GET', 'POST'])
def api_search():
    """
    API endpoint for movie search

    Accepts both GET and POST
    Returns JSON array of movies

    Example response:
    {
        "success": true,
        "count": 10,
        "movies": [
            {
                "title": "The Godfather",
                "year": 1972,
                "rating": 9.2,
                ...
            }
        ]
    }
    """
    try:
        # Get filters from request (POST or GET)
        if request.method == 'POST':
            filters = request.get_json() or {}
        else:
            filters = request.args.to_dict()
            # Handle multi-select for genres
            if 'genres_include' in request.args:
                filters['genres_include'] = request.args.getlist('genres_include')

        # Build and execute query
        query, params = build_query(filters)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)

        # Convert rows to dictionaries
        movies = []
        for row in cur.fetchall():
            movie = dict(row)

            # Convert language/country codes to names
            if 'language' in movie and movie['language']:
                movie['language_name'] = get_language_name(movie['language'])
            if 'country' in movie and movie['country']:
                movie['country_name'] = get_country_name(movie['country'])

            # Format genres
            if movie.get('genres'):
                movie['genres_list'] = movie['genres'].split('|')

            movies.append(movie)

        conn.close()

        # Post-filter for ONLY genre mode: movies must have EXACTLY the selected genres
        genre_mode = filters.get('genre_mode', 'OR')
        genres_include = filters.get('genres_include', [])
        if isinstance(genres_include, str):
            genres_include = [genres_include]
        if genre_mode == 'ONLY' and genres_include:
            target = set(genres_include)
            movies = [
                m for m in movies
                if set(g for g in (m.get('genres') or '').split('|') if g) == target
            ]

        return jsonify({
            'success': True,
            'count': len(movies),
            'movies': movies
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/director/<path:director_name>')
def api_director_filmography(director_name):
    """
    Get filmography for a director

    Example: /api/director/Christopher%20Nolan
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT title, year, rating, votes, genres
            FROM movies
            WHERE directors LIKE ?
            ORDER BY rating DESC, votes DESC
            LIMIT 20
        """, (f'%{director_name}%',))

        movies = [dict(row) for row in cur.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'director': director_name,
            'count': len(movies),
            'movies': movies
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/movie/<imdb_id>')
def movie_detail(imdb_id):
    """
    Movie detail page
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM movies WHERE imdb_id = ?", (imdb_id,))
    movie = cur.fetchone()
    conn.close()

    if not movie:
        return "Movie not found", 404

    movie_dict = dict(movie)

    # Add formatted data
    if movie_dict.get('language'):
        movie_dict['language_name'] = get_language_name(movie_dict['language'])
    if movie_dict.get('country'):
        movie_dict['country_name'] = get_country_name(movie_dict['country'])
    if movie_dict.get('genres'):
        movie_dict['genres_list'] = movie_dict['genres'].split('|')

    return render_template('movie_detail.html', movie=movie_dict)

@app.route('/about')
def about():
    """About page with IMDB attribution"""
    return render_template('about.html')

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: Database not found at {DATABASE_PATH}")
        print("Please run convert_to_sqlite.py first to create the database")
        exit(1)

    # Development server (DO NOT use in production)
    # For production, use gunicorn or similar WSGI server
    app.run(debug=True, host='0.0.0.0', port=5000)
