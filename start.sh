#!/bin/bash
# Build the database in the background if it doesn't exist, then start gunicorn.
# The app will show a "preparing" page until the database is ready.

if [ ! -f "imdb_dataset.db" ]; then
    echo "[start.sh] Database not found — building in background..."
    (python3 download_imdb_data_auto.py && python3 convert_to_sqlite.py && echo "[start.sh] Database ready.") &
else
    echo "[start.sh] Database found, starting normally."
fi

exec gunicorn app:app --timeout 120
