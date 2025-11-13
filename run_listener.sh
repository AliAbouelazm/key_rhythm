#!/bin/bash

# Wrapper script for typing rhythm listener
# This makes it easier to add to macOS Accessibility

cd "$(dirname "$0")"
source venv/bin/activate
exec python3 -m src.listener

