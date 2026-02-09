# IMDB Movie Browser - Architecture Documentation

## Overview

This is a Flask web application that provides a searchable interface for IMDB movie data. It converts the desktop GUI (`imdb_gui_gpt.py`) into a web-based application.

## Technology Stack

- **Backend:** Python 3.11+ with Flask 3.0
- **Database:** SQLite with WAL mode and performance optimizations
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 (no frameworks)
- **Deployment:** Render.com (or Railway, PythonAnywhere)
- **Server:** Gunicorn WSGI server for production

## Directory Structure

```
imdb_web_app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── .gitignore             # Git ignore rules
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Base template with nav/footer
│   ├── index.html         # Search page
│   ├── movie_detail.html  # Individual movie page
│   ├── about.html         # About/attribution page
│   ├── 404.html          # Not found error
│   └── 500.html          # Server error
└── static/               # Static assets
    ├── css/
    │   └── style.css     # All styles (responsive)
    └── js/
        └── main.js       # Shared JavaScript

```

## Database Schema

Uses the same SQLite database as the desktop GUI (`imdb_dataset.db`):

```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imdb_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    original_title TEXT,
    year INTEGER NOT NULL,
    rating REAL NOT NULL,
    votes INTEGER NOT NULL,
    duration_mins INTEGER NOT NULL,
    duration_text TEXT NOT NULL,
    genres TEXT NOT NULL,
    directors TEXT,
    writers TEXT,
    cast TEXT,
    language TEXT,
    country TEXT
)
```

**Indexes (for performance):**
- `idx_title` on `title COLLATE NOCASE`
- `idx_year` on `year`
- `idx_rating` on `rating`
- `idx_votes` on `votes`
- `idx_genres` on `genres`
- `idx_language` on `language`
- `idx_country` on `country`

## Application Architecture

### 1. Flask Routes (`app.py`)

#### Homepage `/`
- **Method:** GET
- **Template:** `index.html`
- **Function:** `index()`
- **Purpose:** Display search form with all filters
- **Data:** Loads genres, languages, countries from database

#### Search API `/api/search`
- **Methods:** GET, POST
- **Returns:** JSON
- **Function:** `api_search()`
- **Purpose:** Execute filtered movie query
- **Parameters:**
  - `title` - Title search (LIKE)
  - `year_from`, `year_to` - Year range
  - `rating_min`, `rating_max` - Rating range
  - `votes_min` - Minimum votes (logarithmic thresholds)
  - `genres_include` - Array of genres to include
  - `genre_mode` - "AND" or "OR"
  - `director` - Director name search
  - `cast` - Cast member search
  - `language` - Language code
  - `country` - Country code
  - `sort_by` - Column to sort by
  - `sort_order` - "ASC" or "DESC"
  - `limit` - Max results (default: 100)

#### Movie Detail `/movie/<imdb_id>`
- **Method:** GET
- **Template:** `movie_detail.html`
- **Function:** `movie_detail(imdb_id)`
- **Purpose:** Show detailed movie information
- **Data:** Single movie record

#### Director Filmography `/api/director/<name>`
- **Method:** GET
- **Returns:** JSON
- **Function:** `api_director_filmography(name)`
- **Purpose:** Get top 20 movies by director
- **Data:** Array of movies

#### About Page `/about`
- **Method:** GET
- **Template:** `about.html`
- **Function:** `about()`
- **Purpose:** IMDB attribution and project info

### 2. Database Functions

#### `get_db_connection()`
Creates optimized SQLite connection with:
- WAL mode for better concurrency
- 64MB cache (vs 2MB default)
- Memory temp storage
- Normal synchronous mode
- 256MB memory-mapped I/O

#### `get_database_stats()`
Loads metadata for homepage:
- Total movie count
- Available genres
- Available languages (with full names)
- Available countries (with full names)
- Year range (min/max)

#### `build_query(filters)`
Constructs SQL query from filter parameters:
- Handles optional columns (language/country)
- Builds WHERE conditions dynamically
- Returns `(query_string, params_list)` tuple
- Supports LIKE queries with `%` wildcards
- Implements AND/OR genre logic

### 3. Frontend Architecture

#### HTML Templates (Jinja2)
- **Inheritance:** All pages extend `base.html`
- **Blocks:** `title`, `content`, `extra_css`, `extra_js`
- **Variables:** Passed from Flask routes
- **Filters:** `format()`, `escapeHtml()`

#### CSS (`style.css`)
- **Responsive:** Mobile-first design with breakpoints
- **CSS Variables:** Consistent theming
- **Grid Layout:** Flexbox and CSS Grid
- **Components:** Modular, reusable classes
- **Breakpoints:**
  - Desktop: 1200px+ (default)
  - Tablet: 768px-1199px
  - Mobile: <768px
  - Small mobile: <480px (stacked table)

#### JavaScript (Inline in `index.html`)
- **Vanilla JS:** No framework dependencies
- **Features:**
  - Form submission with Fetch API
  - Genre button state management
  - Vote slider logarithmic scale
  - Dynamic table rendering
  - AJAX search requests
  - HTML escaping for XSS protection

## Data Flow

### Search Flow
```
User fills form
    ↓
Click "Search Movies"
    ↓
JavaScript captures form data
    ↓
Convert votes slider index → actual value
    ↓
Fetch POST to /api/search (JSON)
    ↓
Flask receives filters
    ↓
build_query() constructs SQL
    ↓
SQLite executes query
    ↓
Convert codes to names (language/country)
    ↓
Return JSON response
    ↓
JavaScript renders table
    ↓
User sees results
```

### Movie Detail Flow
```
User clicks movie title
    ↓
Navigate to /movie/{imdb_id}
    ↓
Flask queries database
    ↓
Render movie_detail.html
    ↓
Show all movie information
```

## Performance Optimizations

### Database Level
1. **WAL Mode:** Allows concurrent reads during writes
2. **Large Cache:** 64MB cache keeps frequently accessed data in memory
3. **Memory Temp Storage:** Temporary tables in RAM
4. **Memory-Mapped I/O:** 256MB mmap for faster reads
5. **Indexes:** 7 indexes on commonly filtered columns

### Application Level
1. **Result Limiting:** Default 100 movies (prevents huge responses)
2. **Row Factory:** `sqlite3.Row` for dict-like access
3. **Connection Reuse:** One connection per request
4. **Lazy Loading:** Database stats loaded only on homepage

### Frontend Level
1. **No Framework Overhead:** Vanilla JavaScript is lightweight
2. **Inline Styles:** Critical CSS in templates
3. **Minimal JavaScript:** Only what's needed
4. **Mobile-First:** Progressive enhancement

## Security Considerations

### SQL Injection Prevention
- **Parameterized Queries:** All user input uses `?` placeholders
- **No String Concatenation:** Never build SQL with f-strings for user input
- **Type Casting:** Convert inputs to correct types (int, float)

### XSS Prevention
- **HTML Escaping:** `escapeHtml()` function in JavaScript
- **Jinja2 Auto-escaping:** Templates escape by default
- **Content-Type Headers:** Proper JSON responses

### Input Validation
- **Limit Values:** Max result limit enforced
- **Type Checking:** Year, rating, votes validated
- **Genre Filtering:** Only allowed genres from database
- **LIKE Sanitization:** Wildcards controlled by application

## Code Comments for Future Updates

### To Add a New Filter:

1. **Update HTML** (`templates/index.html`):
```html
<div class="form-group">
    <label for="new_filter">New Filter:</label>
    <input type="text" id="new_filter" name="new_filter" class="form-control">
</div>
```

2. **Update JavaScript** (inline):
```javascript
// In form submission handler
if (filters.new_filter) {
    // Add to filters object (already done by FormData)
}
```

3. **Update Flask** (`app.py`, `build_query()`):
```python
# In build_query() function
new_filter = filters.get('new_filter', '').strip()
if new_filter:
    query += " AND column_name LIKE ?"
    params.append(f"%{new_filter}%")
```

### To Add a New Route:

```python
@app.route('/new-page')
def new_page():
    """Description of new page"""
    # Query database if needed
    # Return render_template('new_page.html', data=data)
    pass
```

### To Add a New API Endpoint:

```python
@app.route('/api/new-endpoint', methods=['GET', 'POST'])
def api_new_endpoint():
    """API description"""
    try:
        # Process request
        # Query database
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## IMDB Attribution Requirements

**MUST display on every page:**
> Information courtesy of IMDb (https://www.imdb.com). Used with permission.

**Current implementation:**
- Footer in `base.html` (inherited by all pages)
- About page with full attribution
- Links to IMDB datasets and policies

**License:** Non-commercial use only. For commercial use, contact licensing@imdb.com

## Deployment Notes

- Database file (`imdb_dataset.db`) must be copied to production
- Environment variable `DATABASE_PATH` can override default
- Gunicorn recommended for production (included in requirements.txt)
- Development server (`app.run()`) only for testing

## Future Enhancement Ideas

1. **User Accounts:** Save favorite movies, watchlists
2. **Advanced Search:** Complex boolean queries
3. **Recommendations:** Similar movies based on genres/directors
4. **Export:** Download search results as CSV/JSON
5. **Statistics:** Charts and graphs for trends
6. **Pagination:** Load more results dynamically
7. **Caching:** Redis for frequently searched queries
8. **Full-Text Search:** FTS5 extension for better title search
9. **Image Support:** Movie posters from IMDB
10. **API Keys:** Rate limiting for public API

## Troubleshooting

### "Database not found"
- Ensure `imdb_dataset.db` exists in parent directory
- Check `DATABASE_PATH` in `app.py`
- Run `convert_to_sqlite.py` to create database

### "Column not found"
- Old database schema
- Rebuild database with latest `convert_to_sqlite.py`
- Check `has_language`/`has_country` flags

### Slow Queries
- Check indexes: `PRAGMA index_list('movies')`
- Analyze database: `ANALYZE;`
- Reduce result limit

### Memory Errors
- Reduce cache size in `get_db_connection()`
- Lower mmap size
- Add pagination

## Contact & Support

For issues with:
- **IMDB Data:** imdb-data-interest@imdb.com
- **Commercial Licensing:** licensing@imdb.com
- **This Application:** Check documentation first

## Version History

- **v1.0** - Initial Flask conversion from desktop GUI
- Includes all features from `imdb_gui_gpt.py`
- Responsive design for mobile/tablet/desktop
- Production-ready with Gunicorn
