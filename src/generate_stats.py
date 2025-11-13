"""Generate statistics JSON file for website integration.

This script processes raw keystroke CSV files and generates a JSON file
with typing rhythm statistics that can be used by the portfolio website.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

from .config import DATA_RAW_DIR


def load_all_keystrokes() -> List[Dict]:
    """Load all keystroke data from CSV files."""
    keystrokes = []
    
    # Get all CSV files
    csv_files = sorted(DATA_RAW_DIR.glob("keystrokes_*.csv"))
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    keystrokes.append({
                        'timestamp': row['timestamp'],
                        'key': row['key'],
                        'time_since_previous_ms': float(row['time_since_previous_ms']),
                        'is_backspace': int(row['is_backspace']),
                    })
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    return keystrokes


def calculate_wpm(keystrokes: List[Dict], window_minutes: int = 1) -> List[Dict]:
    """Calculate WPM over time with rolling windows."""
    if not keystrokes:
        return []
    
    wpm_data = []
    window_seconds = window_minutes * 60
    
    # Group keystrokes by time windows
    current_window_start = None
    window_keystrokes = []
    
    for ks in keystrokes:
        timestamp = datetime.fromisoformat(ks['timestamp'])
        
        if current_window_start is None:
            current_window_start = timestamp
        
        # If we've moved to a new window, calculate WPM for previous window
        if (timestamp - current_window_start).total_seconds() >= window_seconds:
            if window_keystrokes:
                # Calculate WPM (assuming 5 characters per word)
                total_chars = len([k for k in window_keystrokes if not k['is_backspace']])
                words = total_chars / 5.0
                minutes = window_seconds / 60.0
                wpm = words / minutes if minutes > 0 else 0
                
                wpm_data.append({
                    'timestamp': current_window_start.isoformat(),
                    'wpm': round(wpm, 1)
                })
            
            # Start new window
            current_window_start = timestamp
            window_keystrokes = [ks]
        else:
            window_keystrokes.append(ks)
    
    # Calculate WPM for last window
    if window_keystrokes:
        total_chars = len([k for k in window_keystrokes if not k['is_backspace']])
        words = total_chars / 5.0
        minutes = window_seconds / 60.0
        wpm = words / minutes if minutes > 0 else 0
        
        wpm_data.append({
            'timestamp': current_window_start.isoformat(),
            'wpm': round(wpm, 1)
        })
    
    return wpm_data


def calculate_keystroke_timing_distribution(keystrokes: List[Dict]) -> Dict:
    """Calculate distribution of time between keystrokes."""
    if not keystrokes:
        return {
            'mean': 0,
            'median': 0,
            'std': 0,
            'percentiles': {
                '25': 0,
                '50': 0,
                '75': 0,
                '95': 0
            }
        }
    
    # Get all inter-keystroke times (exclude first keystroke)
    times = [ks['time_since_previous_ms'] for ks in keystrokes[1:]]
    times = [t for t in times if t > 0]  # Filter out zeros
    
    if not times:
        return {
            'mean': 0,
            'median': 0,
            'std': 0,
            'percentiles': {
                '25': 0,
                '50': 0,
                '75': 0,
                '95': 0
            }
        }
    
    times_sorted = sorted(times)
    n = len(times_sorted)
    
    mean = sum(times) / n
    median = times_sorted[n // 2] if n > 0 else 0
    
    # Calculate standard deviation
    variance = sum((t - mean) ** 2 for t in times) / n
    std = variance ** 0.5
    
    # Percentiles
    def percentile(data, p):
        if not data:
            return 0
        k = (len(data) - 1) * p
        f = int(k)
        c = k - f
        if f + 1 < len(data):
            return data[f] + c * (data[f + 1] - data[f])
        return data[f]
    
    return {
        'mean': round(mean, 2),
        'median': round(median, 2),
        'std': round(std, 2),
        'percentiles': {
            '25': round(percentile(times_sorted, 0.25), 2),
            '50': round(median, 2),
            '75': round(percentile(times_sorted, 0.75), 2),
            '95': round(percentile(times_sorted, 0.95), 2)
        }
    }


def detect_burst_patterns(keystrokes: List[Dict], burst_threshold_ms: float = 500) -> List[Dict]:
    """Detect typing bursts (rapid sequences of keystrokes)."""
    if not keystrokes:
        return []
    
    bursts = []
    current_burst = []
    
    for ks in keystrokes:
        if ks['time_since_previous_ms'] < burst_threshold_ms:
            # Continue current burst
            if not current_burst:
                # Start new burst with previous keystroke
                current_burst = [keystrokes[keystrokes.index(ks) - 1]] if keystrokes.index(ks) > 0 else []
            current_burst.append(ks)
        else:
            # End of burst
            if len(current_burst) >= 3:  # Minimum burst length
                bursts.append({
                    'start': current_burst[0]['timestamp'],
                    'end': current_burst[-1]['timestamp'],
                    'duration_ms': sum(k['time_since_previous_ms'] for k in current_burst[1:]),
                    'keystrokes': len(current_burst)
                })
            current_burst = []
    
    # Handle last burst
    if len(current_burst) >= 3:
        bursts.append({
            'start': current_burst[0]['timestamp'],
            'end': current_burst[-1]['timestamp'],
            'duration_ms': sum(k['time_since_previous_ms'] for k in current_burst[1:]),
            'keystrokes': len(current_burst)
        })
    
    return bursts


def generate_stats_json(output_path: Path = None):
    """Generate statistics JSON file from raw keystroke data."""
    if output_path is None:
        output_path = Path(__file__).parent.parent / "typing_stats.json"
    
    print("Loading keystroke data...")
    keystrokes = load_all_keystrokes()
    
    if not keystrokes:
        print("No keystroke data found. Generating empty stats file.")
        stats = {
            'last_updated': datetime.now().isoformat(),
            'total_keystrokes': 0,
            'wpm_over_time': [],
            'keystroke_timing': {},
            'burst_patterns': [],
            'summary': {
                'avg_wpm': 0,
                'total_bursts': 0,
                'avg_burst_length': 0
            }
        }
    else:
        print(f"Processing {len(keystrokes)} keystrokes...")
        
        # Calculate statistics
        wpm_over_time = calculate_wpm(keystrokes, window_minutes=5)  # 5-minute windows
        timing_dist = calculate_keystroke_timing_distribution(keystrokes)
        bursts = detect_burst_patterns(keystrokes)
        
        # Calculate summary stats
        avg_wpm = sum(w['wpm'] for w in wpm_over_time) / len(wpm_over_time) if wpm_over_time else 0
        avg_burst_length = sum(b['keystrokes'] for b in bursts) / len(bursts) if bursts else 0
        
        stats = {
            'last_updated': datetime.now().isoformat(),
            'total_keystrokes': len(keystrokes),
            'wpm_over_time': wpm_over_time[-100:],  # Last 100 data points
            'keystroke_timing': timing_dist,
            'burst_patterns': bursts[-50:],  # Last 50 bursts
            'summary': {
                'avg_wpm': round(avg_wpm, 1),
                'total_bursts': len(bursts),
                'avg_burst_length': round(avg_burst_length, 1)
            }
        }
    
    # Write JSON file
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Statistics saved to {output_path}")
    return stats


def main():
    """Main entry point."""
    generate_stats_json()


if __name__ == "__main__":
    main()

