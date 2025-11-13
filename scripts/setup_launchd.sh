#!/bin/bash

# Script to set up auto-start on Mac login

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_FILE="$PROJECT_DIR/com.aliabouelazm.typing-rhythm.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
DEST_PLIST="$LAUNCH_AGENTS_DIR/com.aliabouelazm.typing-rhythm.plist"

echo "Setting up auto-start for typing rhythm tracker..."
echo ""

# Check if venv exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: cd $PROJECT_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist file
cp "$PLIST_FILE" "$DEST_PLIST"

# Update paths in plist (in case username is different)
sed -i '' "s|/Users/aliabouelazm|$HOME|g" "$DEST_PLIST"

# Load the launch agent
launchctl unload "$DEST_PLIST" 2>/dev/null  # Unload if already loaded
launchctl load "$DEST_PLIST"

echo "✓ Auto-start configured!"
echo ""
echo "IMPORTANT: You need to grant accessibility permissions!"
echo ""
echo "1. Open System Preferences → Security & Privacy → Privacy → Accessibility"
echo "2. Click the lock and enter your password"
echo "3. Add /bin/bash to the list (click + and navigate to /bin/bash)"
echo "   OR add Terminal (Applications → Utilities → Terminal)"
echo "4. Check the box next to it"
echo ""
echo "After granting permissions, restart the service:"
echo "  launchctl stop com.aliabouelazm.typing-rhythm"
echo "  launchctl start com.aliabouelazm.typing-rhythm"
echo ""
echo "The listener will now start automatically when you log in."
echo ""
echo "To stop auto-start, run:"
echo "  launchctl unload $DEST_PLIST"
echo ""
echo "To check status, run:"
echo "  launchctl list | grep typing-rhythm"

