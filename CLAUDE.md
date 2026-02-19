# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run (development)
```bash
python3 app.py
# Serves on http://localhost:5000
```

### Run (production)
```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### First-time database setup
```bash
python3 download_imdb_data_auto.py   # Downloads ~825 MB of IMDB TSV files (~10 min)
python3 convert_to_sqlite.py          # Converts to imdb_dataset.db (~2-3 min)
```

## Architecture

**Flask + SQLite + Vanilla JS** — no ORM, no JS framework, no CSS framework.

- `app.py` — all backend logic: Flask routes, SQL query builder, admin update mechanism
- `convert_to_sqlite.py` — converts merged TSV → SQLite with indexes and PRAGMAs
- `download_imdb_data_auto.py` — downloads 6 IMDB datasets, merges them into a single TSV
- `templates/` — Jinja2 templates (inheriting from `base.html`)
- `static/css/style.css` — all styles (IMDB yellow `#f5c518` / black color scheme)
- `static/js/main.js` — currently a placeholder; all active JS is inline in `index.html`

### Database schema (`imdb_dataset.db`)

Single table `movies` with columns:
`id, imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult`

Genres are pipe-separated (`Drama|Crime`). Directors, writers, and cast are comma-separated names. Language/country are ISO codes.

SQLite is tuned at connection time with WAL mode, 64 MB cache, memory temp store, and 256 MB mmap.

### Search query building

`app.py` builds dynamic SQL using a `WHERE 1=1` pattern, appending conditions and parameters for each active filter. All values go through parameterized queries — never string interpolation.

Genre filtering has three modes:
- **OR** — any selected genre (LIKE conditions OR'd)
- **AND** — all selected genres (LIKE conditions AND'd)
- **ONLY** — exact genre match (fetched with AND, then post-filtered in Python to exclude extra genres)

Director/cast search supports comma-separated names, `*` wildcards (mapped to SQL `%`), and `-` prefix to exclude.

### Frontend (index.html)

All search UI logic is inline JavaScript in `index.html`. Key patterns:
- Vote slider uses a logarithmic lookup table (`voteThresholds` array, index 0–9)
- Genre buttons cycle through 3 states: unselected → include (yellow `+`) → exclude (gray `-`)
- Results table is built dynamically from the `/api/search` JSON response
- In-memory client-side sorting on the rendered table (no second API call)
- `escapeHtml()` is used on all user-derived data inserted into the DOM

### Admin updates

`/admin/update/stream` is an SSE endpoint that streams stdout/stderr from subprocess calls to `download_imdb_data_auto.py` and `convert_to_sqlite.py`. An in-process lock prevents concurrent updates. APScheduler (optional) can schedule nightly updates via the `UPDATE_HOUR` env var.

### Routes

| Route | Purpose |
|---|---|
| `GET /` | Search page with DB stats |
| `GET /movie/<imdb_id>` | Movie detail page |
| `GET,POST /api/search` | JSON search API |
| `GET /api/director/<name>` | Director filmography (top 20) |
| `GET /admin` | Admin panel |
| `GET /admin/update/stream` | SSE update progress stream |
| `GET /about` | Attribution page |

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `imdb_dataset.db` | Override DB file location |
| `UPDATE_HOUR` | `3` | Hour (0–23) for scheduled nightly update |

### Deployment

`render.yaml` configures Render.com deployment (Python 3.11, Gunicorn start command). The SQLite database file must be present in the app directory; it is not auto-created at startup.
