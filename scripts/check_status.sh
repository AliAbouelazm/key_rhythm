#!/bin/bash

# Quick script to check if listener is running and show recent data

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
DATA_DIR="$PROJECT_DIR/data/raw"

echo "Checking typing rhythm tracker status..."
echo ""

# Check if process is running
if pgrep -f "python.*src.listener" > /dev/null; then
    echo "✓ Listener is RUNNING"
else
    echo "✗ Listener is NOT running"
fi

echo ""

# Check for data files
if [ -d "$DATA_DIR" ]; then
    CSV_FILES=$(ls -t "$DATA_DIR"/*.csv 2>/dev/null | head -1)
    if [ -n "$CSV_FILES" ]; then
        LATEST_FILE=$(ls -t "$DATA_DIR"/*.csv | head -1)
        LINE_COUNT=$(wc -l < "$LATEST_FILE" 2>/dev/null || echo "0")
        FILE_SIZE=$(ls -lh "$LATEST_FILE" | awk '{print $5}' 2>/dev/null || echo "0")
        echo "Latest data file: $(basename "$LATEST_FILE")"
        echo "Events recorded: $((LINE_COUNT - 1))"  # Subtract header
        echo "File size: $FILE_SIZE"
        echo ""
        echo "Last 3 keystrokes:"
        tail -3 "$LATEST_FILE" | column -t -s,
    else
        echo "No data files found yet. Start typing to generate data!"
    fi
else
    echo "Data directory not found."
fi

