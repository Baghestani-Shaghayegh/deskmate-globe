#!/bin/bash
# Remove the Deskmate stats helper from macOS.   Usage:  bash uninstall-mac.sh
NAME="com.deskmate.stats"
PLIST="$HOME/Library/LaunchAgents/$NAME.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
rm -f "$HOME/Library/Application Support/Deskmate/deskmate_stats.py" "$HOME/Library/Application Support/Deskmate/stats.log"
rmdir "$HOME/Library/Application Support/Deskmate" 2>/dev/null || true
echo "✓ Removed. The wallpaper's SYSTEM panel will hide itself again."
