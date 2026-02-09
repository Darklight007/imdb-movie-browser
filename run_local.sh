#!/bin/bash
#
# Quick start script for local testing
# Run this to test the web app before deploying
#

echo "======================================================================"
echo "IMDB Movie Browser - Local Test Server"
echo "======================================================================"
echo ""

# Check if database exists
if [ ! -f "imdb_dataset.db" ]; then
    echo "❌ ERROR: imdb_dataset.db not found!"
    echo ""
    echo "Please copy the database file:"
    echo "  cp ../imdb_dataset.db ./"
    echo ""
    echo "Or create it:"
    echo "  cd .."
    echo "  python3 fix_country_data.py"
    echo "  python3 convert_to_sqlite.py"
    echo "  cp imdb_dataset.db imdb_web_app/"
    echo ""
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo ""
    echo "❌ Flask not installed!"
    echo ""
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "✓ Dependencies installed"
echo ""
echo "Starting development server..."
echo ""
echo "URL: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""
echo "======================================================================"
echo ""

# Run the app
python3 app.py
