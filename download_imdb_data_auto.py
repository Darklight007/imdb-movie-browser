#!/usr/bin/env python3
"""
Download and process IMDB datasets (automatic mode)
Downloads title.basics.tsv.gz and title.ratings.tsv.gz from IMDB,
then merges them into a single TSV file compatible with imdb_gui.py
"""

import gzip
import urllib.request
import os
from typing import Dict

# IMDB dataset URLs
BASICS_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
CREW_URL = "https://datasets.imdbws.com/title.crew.tsv.gz"
PRINCIPALS_URL = "https://datasets.imdbws.com/title.principals.tsv.gz"
NAMES_URL = "https://datasets.imdbws.com/name.basics.tsv.gz"
AKAS_URL = "https://datasets.imdbws.com/title.akas.tsv.gz"

# Output file
OUTPUT_FILE = "imdb_dataset.txt"

# Temporary files
BASICS_GZ = "title.basics.tsv.gz"
RATINGS_GZ = "title.ratings.tsv.gz"
CREW_GZ = "title.crew.tsv.gz"
PRINCIPALS_GZ = "title.principals.tsv.gz"
NAMES_GZ = "name.basics.tsv.gz"
AKAS_GZ = "title.akas.tsv.gz"


def download_file(url: str, filename: str):
    """Download a file with progress indication"""
    print(f"\n[1/4] Downloading {filename}...")
    print(f"URL: {url}")

    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 / total_size)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='', flush=True)

    urllib.request.urlretrieve(url, filename, progress)
    print()  # New line after progress


def load_ratings(filename: str) -> Dict[str, tuple]:
    """Load ratings data into memory"""
    print(f"\n[2/8] Loading ratings from {filename}...")
    ratings = {}

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        f.readline()  # Skip header
        count = 0

        try:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    tconst = parts[0]
                    try:
                        avg_rating = float(parts[1])
                        num_votes = int(parts[2])
                        ratings[tconst] = (avg_rating, num_votes)
                        count += 1
                        if count % 100000 == 0:
                            print(f"  Loaded {count:,} ratings...", flush=True)
                    except ValueError:
                        continue
        except EOFError:
            print(f"  ⚠ Warning: ratings file truncated after {count:,} rows. Using data so far.")

    print(f"✓ Total ratings loaded: {len(ratings):,}")
    return ratings


def load_crew(filename: str) -> Dict[str, tuple]:
    """Load directors and writers data into memory"""
    print(f"\n[3/8] Loading crew (directors/writers) from {filename}...")
    crew = {}

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        f.readline()  # Skip header
        count = 0

        try:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    tconst = parts[0]
                    directors = parts[1] if parts[1] != '\\N' else ''
                    writers = parts[2] if parts[2] != '\\N' else ''
                    crew[tconst] = (directors, writers)
                    count += 1
                    if count % 100000 == 0:
                        print(f"  Loaded {count:,} crew records...", flush=True)
        except EOFError:
            print(f"  ⚠ Warning: crew file truncated after {count:,} rows. Using data so far.")

    print(f"✓ Total crew loaded: {len(crew):,}")
    return crew


def load_names(filename: str) -> Dict[str, str]:
    """Load name data (nconst -> name) into memory"""
    print(f"\n[4/8] Loading names from {filename}...")
    names = {}

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        f.readline()  # Skip header
        count = 0

        try:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    nconst = parts[0]
                    primary_name = parts[1]
                    names[nconst] = primary_name
                    count += 1
                    if count % 100000 == 0:
                        print(f"  Loaded {count:,} names...", flush=True)
        except EOFError:
            print(f"  ⚠ Warning: names file truncated after {count:,} rows. Using data so far.")

    print(f"✓ Total names loaded: {len(names):,}")
    return names


def load_principals(filename: str, names: Dict[str, str]) -> Dict[str, str]:
    """Load top 3 actors for each title"""
    print(f"\n[5/8] Loading principals (cast) from {filename}...")
    principals = {}

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        f.readline()  # Skip header
        count = 0

        try:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    tconst = parts[0]
                    nconst = parts[2]
                    category = parts[3]

                    # Only actors/actresses
                    if category in ('actor', 'actress'):
                        name = names.get(nconst, 'Unknown')
                        if tconst not in principals:
                            principals[tconst] = []
                        if len(principals[tconst]) < 3:  # Top 3 only
                            principals[tconst].append(name)

                    count += 1
                    if count % 100000 == 0:
                        print(f"  Processed {count:,} principals...", flush=True)

        except EOFError:
            print(f"  ⚠ Warning: principals file appears truncated after {count:,} rows.")
            print(f"  Continuing with {len(principals):,} titles loaded so far.")

    # Convert lists to comma-separated strings
    principals = {k: ', '.join(v) for k, v in principals.items()}
    print(f"✓ Total titles with cast: {len(principals):,}")
    return principals


def load_languages_and_countries(filename: str) -> tuple[Dict[str, str], Dict[str, str]]:
    """Load language and country data from akas (alternative titles) - prefer English/US or original"""
    print(f"\n[6/8] Loading language and country data from {filename}...")
    languages = {}
    original_languages = {}  # Track original title languages
    countries = {}
    original_countries = {}  # Track original title countries

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        f.readline()  # Skip header
        count = 0

        try:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    tconst = parts[0]
                    region = parts[3] if parts[3] != '\\N' else ''  # Country/region code
                    language = parts[4] if parts[4] != '\\N' else ''
                    is_original = parts[7] == '1'

                    # Language priority: 1) English 2) Original title language 3) First language found
                    if language:
                        if language == 'en':
                            languages[tconst] = 'en'
                            if tconst in original_languages:
                                del original_languages[tconst]
                        elif is_original and tconst not in languages:
                            original_languages[tconst] = language
                        elif tconst not in languages and tconst not in original_languages:
                            languages[tconst] = language

                    # Country priority: 1) US 2) Original title region 3) First region found
                    if region:
                        if region == 'US':
                            countries[tconst] = 'US'
                            if tconst in original_countries:
                                del original_countries[tconst]
                        elif is_original and tconst not in countries:
                            original_countries[tconst] = region
                        elif tconst not in countries and tconst not in original_countries:
                            countries[tconst] = region

                    count += 1
                    if count % 500000 == 0:
                        print(f"  Processed {count:,} alternative titles...", flush=True)
        except EOFError:
            print(f"  ⚠ Warning: akas file truncated after {count:,} rows. Using data so far.")

    # Merge original languages/countries for titles without English/US
    for tconst, lang in original_languages.items():
        if tconst not in languages:
            languages[tconst] = lang

    for tconst, country in original_countries.items():
        if tconst not in countries:
            countries[tconst] = country

    print(f"✓ Total titles with language: {len(languages):,}")
    print(f"✓ Total titles with country: {len(countries):,}")
    return languages, countries


def process_basics(basics_file: str, ratings: Dict[str, tuple], crew: Dict[str, tuple],
                   principals: Dict[str, str], names: Dict[str, str], languages: Dict[str, str],
                   countries: Dict[str, str], output_file: str):
    """Process basics file and merge with all data"""
    print(f"\n[7/8] Processing movies from {basics_file}...")

    movies_written = 0
    line_count = 0

    with gzip.open(basics_file, 'rt', encoding='utf-8') as fin:
        fin.readline()  # Skip header

        with open(output_file, 'w', encoding='utf-8') as fout:
            try:
                for line in fin:
                    line_count += 1
                    if line_count % 100000 == 0:
                        print(f"  Processed {line_count:,} lines, found {movies_written:,} movies...", flush=True)

                    parts = line.strip().split('\t')
                    if len(parts) < 9:
                        continue

                    tconst = parts[0]
                    title_type = parts[1]
                    primary_title = parts[2]
                    original_title = parts[3]
                    is_adult = parts[4]
                    start_year = parts[5]
                    runtime_minutes = parts[7]
                    genres = parts[8]

                    # Filter: only movies (all adult ratings kept), must have rating
                    if title_type != 'movie':
                        continue
                    if tconst not in ratings:
                        continue
                    if start_year == '\\N' or runtime_minutes == '\\N' or genres == '\\N':
                        continue

                    # Get rating and votes
                    avg_rating, num_votes = ratings[tconst]

                    # Get crew info
                    directors_ids, writers_ids = crew.get(tconst, ('', ''))

                    # Convert director/writer IDs to names
                    director_names = []
                    if directors_ids:
                        for nid in directors_ids.split(',')[:3]:  # Top 3 directors
                            if nid in names:
                                director_names.append(names[nid])
                    directors = ', '.join(director_names) if director_names else ''

                    writer_names = []
                    if writers_ids:
                        for nid in writers_ids.split(',')[:3]:  # Top 3 writers
                            if nid in names:
                                writer_names.append(names[nid])
                    writers = ', '.join(writer_names) if writer_names else ''

                    # Get cast
                    cast = principals.get(tconst, '')

                    # Get language and country
                    language = languages.get(tconst, '')
                    country = countries.get(tconst, '')

                    # Original title (show only if different from primary)
                    original = original_title if original_title != '\\N' and original_title != primary_title else ''

                    # Convert genres from comma-separated to pipe-separated
                    genres_formatted = genres.replace(',', '|')

                    # Format: imdb_id\ttitle\toriginal_title\tyear\trating\tvotes\tduration\tgenres\tdirectors\twriters\tcast\tlanguage\tcountry\tisAdult
                    fout.write(f"{tconst}\t{primary_title}\t{original}\t{start_year}\t{avg_rating:.1f}\t"
                              f"{num_votes}\t{runtime_minutes} mins.\t{genres_formatted}\t"
                              f"{directors}\t{writers}\t{cast}\t{language}\t{country}\t{is_adult}\n")
                    movies_written += 1

            except EOFError:
                print(f"  ⚠ Warning: basics file truncated after {line_count:,} lines. Using {movies_written:,} movies found so far.")

    print(f"✓ Total lines processed: {line_count:,}")
    print(f"✓ Total movies written: {movies_written:,}")


def main():
    print("=" * 70)
    print("IMDB Dataset Downloader and Processor (Automatic Mode)")
    print("=" * 70)
    print("\nDownloading and processing latest IMDB data...")
    print("This may take 5-10 minutes depending on your connection.\n")

    try:
        # Download files (ratings first, it's smallest)
        if not os.path.exists(RATINGS_GZ):
            download_file(RATINGS_URL, RATINGS_GZ)
        else:
            print(f"\n[1/8] ✓ {RATINGS_GZ} already exists, skipping download.")

        # Load ratings into memory
        ratings = load_ratings(RATINGS_GZ)

        # Download and load crew data
        if not os.path.exists(CREW_GZ):
            download_file(CREW_URL, CREW_GZ)
        else:
            print(f"\n✓ {CREW_GZ} already exists, skipping download.")
        crew = load_crew(CREW_GZ)

        # Download and load names
        if not os.path.exists(NAMES_GZ):
            download_file(NAMES_URL, NAMES_GZ)
        else:
            print(f"\n✓ {NAMES_GZ} already exists, skipping download.")
        names = load_names(NAMES_GZ)

        # Download and load principals
        if not os.path.exists(PRINCIPALS_GZ):
            download_file(PRINCIPALS_URL, PRINCIPALS_GZ)
        else:
            print(f"\n✓ {PRINCIPALS_GZ} already exists, skipping download.")
        principals = load_principals(PRINCIPALS_GZ, names)

        # Download and load languages and countries (akas)
        if not os.path.exists(AKAS_GZ):
            download_file(AKAS_URL, AKAS_GZ)
        else:
            print(f"\n✓ {AKAS_GZ} already exists, skipping download.")
        languages, countries = load_languages_and_countries(AKAS_GZ)

        # Download basics
        if not os.path.exists(BASICS_GZ):
            download_file(BASICS_URL, BASICS_GZ)
        else:
            print(f"\n✓ {BASICS_GZ} already exists, skipping download.")

        # Process and merge all data
        process_basics(BASICS_GZ, ratings, crew, principals, names, languages, countries, OUTPUT_FILE)

        # Cleanup
        print("\n[8/8] Cleaning up temporary files...")
        for gz_file in [BASICS_GZ, RATINGS_GZ, CREW_GZ, PRINCIPALS_GZ, NAMES_GZ, AKAS_GZ]:
            if os.path.exists(gz_file):
                os.remove(gz_file)
                print(f"✓ Deleted {gz_file}")

        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\n✓ Dataset created: {OUTPUT_FILE}")
        print(f"✓ File size: {os.path.getsize(OUTPUT_FILE) / (1024*1024):.1f} MB")
        print("\nYou can now run: python3 imdb_gui.py")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
