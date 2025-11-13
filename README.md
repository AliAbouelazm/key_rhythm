# Typing Rhythm Tracker

A lightweight, privacy-safe macOS background app that tracks typing rhythm metadata (keystroke timing) without logging actual text content.

## Features

- **Privacy-First**: Logs only keystroke timing metadata, never actual text
- **Lightweight**: Event-driven listening with minimal CPU usage
- **Background Operation**: Runs continuously without slowing down your Mac
- **Automatic Logging**: Flushes data to CSV files periodically

## Setup

### 1. Create Virtual Environment

```bash
cd ~/Desktop/projects/typing-rhythm-tracker
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Grant Accessibility Permissions

On macOS, you'll need to grant accessibility permissions for the app to monitor keystrokes:

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon and enter your password
3. Check the box next to Terminal (or your Python interpreter)
4. If running from a script, you may need to add the Python executable

### 4. Run the Listener

```bash
python -m src.listener
```

Or use the convenience script:

```bash
./scripts/run_listener.sh
```

## Data Format

The app logs keystroke events to CSV files in `data/raw/` with the following columns:

- `timestamp`: ISO format timestamp
- `key`: Single key pressed (e.g., "a", "b", "space", "enter")
- `time_since_previous_ms`: Milliseconds since the previous keystroke
- `is_backspace`: Boolean flag (1 if backspace, 0 otherwise)

Files are named: `keystrokes_YYYY-MM-DD.csv`

## Project Structure

```
typing-rhythm-tracker/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── listener.py      # Keystroke listener
│   ├── config.py        # Settings
│   └── processor.py     # Future feature engineering
├── data/
│   ├── raw/             # Raw keystroke logs
│   └── processed/       # Processed data (future)
└── scripts/
    └── run_listener.sh  # Startup script
```

## Privacy

This app is designed with privacy in mind:
- **No text logging**: Only individual key names and timing are recorded
- **No sequence reconstruction**: Individual keystrokes cannot be used to reconstruct what you typed
- **Local storage only**: All data stays on your machine
- **Open source**: You can review all code

## Generating Statistics for Website

### Manual Method

To generate a JSON file with typing statistics:

```bash
python -m src.generate_stats
```

This creates `typing_stats.json` in the project root with:
- WPM over time
- Keystroke timing distribution
- Burst patterns
- Summary statistics

### Automated Method

**Option 1: Copy only (you commit manually)**
```bash
./scripts/update_website.sh
```
This generates stats and copies to your website repo, but you commit/push manually.

**Option 2: Fully automated (auto-commit & push)**
```bash
./scripts/update_website_auto.sh
```
This generates stats, copies to website repo, commits, and pushes automatically.

The scripts assume your website repo is at `~/Desktop/website`. You can edit the scripts to change this path.

## Future Enhancements

- Feature engineering for typing patterns
- Visualization tools
- Automated data sync with website

