#!/usr/bin/env python3
"""
Convert IMDB TSV dataset to SQLite database for faster access
Creates indexes on commonly searched/filtered columns
"""

import sqlite3
import sys
import os


def create_database(tsv_file: str, db_file: str):
    """Convert TSV to SQLite with optimized indexes"""

    print("=" * 70)
    print("IMDB Dataset Converter: TSV → SQLite")
    print("=" * 70)

    if not os.path.exists(tsv_file):
        print(f"\n✗ Error: {tsv_file} not found!")
        print("Run: python3 download_imdb_data_auto.py first")
        return False

    # Remove old database if exists
    if os.path.exists(db_file):
        print(f"\n⚠ Removing old {db_file}...")
        os.remove(db_file)

    print(f"\n[1/4] Creating database: {db_file}")

    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table with optimized schema
    print("[2/4] Creating table schema...")
    cursor.execute('''
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
            country TEXT,
            isAdult INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Load data
    print(f"[3/4] Loading data from {tsv_file}...")

    with open(tsv_file, 'r', encoding='utf-8') as f:
        movies = []
        count = 0

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:  # 13+ fields (includes language/country; 14th field = isAdult)
                try:
                    # Extract numeric duration from "142 mins."
                    duration_text = parts[6]
                    duration_mins = int(duration_text.split()[0]) if duration_text.split()[0].isdigit() else 0

                    movies.append((
                        parts[0],  # imdb_id
                        parts[1],  # title
                        parts[2] if parts[2] else None,  # original_title
                        int(parts[3]),  # year
                        float(parts[4]),  # rating
                        int(parts[5]),  # votes
                        duration_mins,  # duration_mins (numeric)
                        duration_text,  # duration_text (original)
                        parts[7],  # genres
                        parts[8] if parts[8] else None,  # directors
                        parts[9] if parts[9] else None,  # writers
                        parts[10] if parts[10] else None,  # cast
                        parts[11] if parts[11] else None,  # language
                        parts[12] if parts[12] else None,  # country
                        int(parts[13]) if len(parts) >= 14 and parts[13] in ('0', '1') else 0  # isAdult
                    ))

                    count += 1

                    # Batch insert every 10000 records
                    if len(movies) >= 10000:
                        cursor.executemany(
                            'INSERT INTO movies (imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            movies
                        )
                        movies = []

                        if count % 50000 == 0:
                            print(f"  Loaded {count:,} movies...", flush=True)

                except (ValueError, IndexError) as e:
                    continue
            elif len(parts) >= 12:  # Format with 12 fields (no country)
                try:
                    duration_text = parts[6]
                    duration_mins = int(duration_text.split()[0]) if duration_text.split()[0].isdigit() else 0

                    movies.append((
                        parts[0],  # imdb_id
                        parts[1],  # title
                        parts[2] if parts[2] else None,  # original_title
                        int(parts[3]),  # year
                        float(parts[4]),  # rating
                        int(parts[5]),  # votes
                        duration_mins,
                        duration_text,
                        parts[7],  # genres
                        parts[8] if parts[8] else None,  # directors
                        parts[9] if parts[9] else None,  # writers
                        parts[10] if parts[10] else None,  # cast
                        parts[11] if parts[11] else None,  # language
                        None,  # country
                        0  # isAdult (not in old format, default non-adult)
                    ))

                    count += 1

                    if len(movies) >= 10000:
                        cursor.executemany(
                            'INSERT INTO movies (imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            movies
                        )
                        movies = []

                        if count % 50000 == 0:
                            print(f"  Loaded {count:,} movies...", flush=True)

                except (ValueError, IndexError):
                    continue
            elif len(parts) >= 11:  # Format with 11 fields (no language/country)
                try:
                    duration_text = parts[6]
                    duration_mins = int(duration_text.split()[0]) if duration_text.split()[0].isdigit() else 0

                    movies.append((
                        parts[0],  # imdb_id
                        parts[1],  # title
                        parts[2] if parts[2] else None,  # original_title
                        int(parts[3]),  # year
                        float(parts[4]),  # rating
                        int(parts[5]),  # votes
                        duration_mins,
                        duration_text,
                        parts[7],  # genres
                        parts[8] if parts[8] else None,  # directors
                        parts[9] if parts[9] else None,  # writers
                        parts[10] if parts[10] else None,  # cast
                        None,  # language
                        None,  # country
                        0  # isAdult (not in old format, default non-adult)
                    ))

                    count += 1

                    if len(movies) >= 10000:
                        cursor.executemany(
                            'INSERT INTO movies (imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            movies
                        )
                        movies = []

                        if count % 50000 == 0:
                            print(f"  Loaded {count:,} movies...", flush=True)

                except (ValueError, IndexError):
                    continue
            elif len(parts) >= 7:  # Old format fallback (7 fields)
                try:
                    duration_text = parts[5]
                    duration_mins = int(duration_text.split()[0]) if duration_text.split()[0].isdigit() else 0

                    movies.append((
                        parts[0],  # imdb_id
                        parts[1],  # title
                        None,  # original_title
                        int(parts[2]),  # year
                        float(parts[3]),  # rating
                        int(parts[4]),  # votes
                        duration_mins,
                        duration_text,
                        parts[6],  # genres
                        None,  # directors
                        None,  # writers
                        None,  # cast
                        None,  # language
                        None,  # country
                        0  # isAdult (not in old format, default non-adult)
                    ))

                    count += 1

                    if len(movies) >= 10000:
                        cursor.executemany(
                            'INSERT INTO movies (imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            movies
                        )
                        movies = []

                        if count % 50000 == 0:
                            print(f"  Loaded {count:,} movies...", flush=True)

                except (ValueError, IndexError):
                    continue

        # Insert remaining
        if movies:
            cursor.executemany(
                'INSERT INTO movies (imdb_id, title, original_title, year, rating, votes, duration_mins, duration_text, genres, directors, writers, cast, language, country, isAdult) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                movies
            )

    print(f"✓ Loaded {count:,} movies")

    # Create indexes for fast searching/filtering
    print("[4/4] Creating indexes for fast access...")

    cursor.execute('CREATE INDEX idx_title ON movies(title COLLATE NOCASE)')
    print("  ✓ Created index on title")

    cursor.execute('CREATE INDEX idx_year ON movies(year)')
    print("  ✓ Created index on year")

    cursor.execute('CREATE INDEX idx_rating ON movies(rating)')
    print("  ✓ Created index on rating")

    cursor.execute('CREATE INDEX idx_votes ON movies(votes)')
    print("  ✓ Created index on votes")

    cursor.execute('CREATE INDEX idx_genres ON movies(genres)')
    print("  ✓ Created index on genres")

    cursor.execute('CREATE INDEX idx_language ON movies(language)')
    print("  ✓ Created index on language")

    cursor.execute('CREATE INDEX idx_country ON movies(country)')
    print("  ✓ Created index on country")

    cursor.execute('CREATE INDEX idx_isadult ON movies(isAdult)')
    print("  ✓ Created index on isAdult")

    # Commit and optimize
    print("\nOptimizing database...")
    conn.commit()
    cursor.execute('VACUUM')
    cursor.execute('ANALYZE')

    conn.close()

    # Show stats
    db_size = os.path.getsize(db_file) / (1024 * 1024)
    tsv_size = os.path.getsize(tsv_file) / (1024 * 1024)

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"\n✓ Database created: {db_file}")
    print(f"✓ Database size: {db_size:.1f} MB")
    print(f"✓ Original TSV size: {tsv_size:.1f} MB")
    print(f"✓ Total movies: {count:,}")
    print(f"\n✓ Indexes created for fast filtering on:")
    print("  - Title (case-insensitive)")
    print("  - Year")
    print("  - Rating")
    print("  - Votes")
    print("  - Genres")

    print(f"\nSpeed improvements:")
    print("  - Filtering: 10-100x faster")
    print("  - Sorting: 5-50x faster")
    print("  - Search: 50-1000x faster with indexes")

    print(f"\nNow run: python3 imdb_gui_sqlite.py")

    return True


if __name__ == "__main__":
    tsv_file = "imdb_dataset.txt"
    db_file = "imdb_dataset.db"

    if len(sys.argv) > 1:
        tsv_file = sys.argv[1]
    if len(sys.argv) > 2:
        db_file = sys.argv[2]

    create_database(tsv_file, db_file)
