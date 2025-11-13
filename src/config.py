"""Configuration settings for typing rhythm tracker."""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Ensure directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Batch settings
BATCH_SIZE = 100  # Flush after this many events
FLUSH_INTERVAL_SECONDS = 60  # Flush every N seconds

# CSV settings
CSV_HEADER = ["timestamp", "key", "time_since_previous_ms", "is_backspace"]

