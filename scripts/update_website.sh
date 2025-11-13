#!/bin/bash

# Script to generate stats and copy to website repo

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WEBSITE_DIR="$HOME/Desktop/website"

# Activate virtual environment if it exists
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Generate stats JSON
echo "Generating typing statistics..."
cd "$PROJECT_DIR"
python -m src.generate_stats

# Check if stats file was created
STATS_FILE="$PROJECT_DIR/typing_stats.json"
if [ ! -f "$STATS_FILE" ]; then
    echo "Error: Failed to generate stats file"
    exit 1
fi

# Copy to website repo
echo "Copying stats to website repo..."
cp "$STATS_FILE" "$WEBSITE_DIR/typing_stats.json"

echo "Stats updated in website repo!"
echo "Don't forget to commit and push:"
echo "  cd $WEBSITE_DIR"
echo "  git add typing_stats.json"
echo "  git commit -m 'Update typing rhythm stats'"
echo "  git push"

