#!/bin/bash
# Install the Deskmate stats helper on macOS so it starts by itself when you log in.
# Usage (in Terminal, from this folder):   bash install-mac.sh
set -e
NAME="com.deskmate.stats"
DIR="$HOME/Library/Application Support/Deskmate"
PLIST="$HOME/Library/LaunchAgents/$NAME.plist"
HERE="$(cd "$(dirname "$0")" && pwd)"

PY="$(command -v python3 || true)"
if [ -z "$PY" ] || ! "$PY" --version >/dev/null 2>&1; then
  echo "Python 3 isn't ready yet. macOS should now offer to install the Command Line Tools — click Install,"
  echo "wait for it to finish, then run this script again.  (Or run:  xcode-select --install)"
  exit 1
fi

mkdir -p "$DIR" "$HOME/Library/LaunchAgents"
cp "$HERE/deskmate_stats.py" "$DIR/deskmate_stats.py"

cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$NAME</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$DIR/deskmate_stats.py</string></array>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>$DIR/stats.log</string>
  <key>StandardErrorPath</key><string>$DIR/stats.log</string>
</dict>
</plist>
PLISTEOF

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true   # restart cleanly if it was installed before
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed. Checking it's running…"
sleep 3
if curl -s -H "Origin: null" http://127.0.0.1:47800/stats | grep -q CurrentCpu; then
  echo "✓ The stats helper is running. Reload the wallpaper (Plash → Reload): the SYSTEM panel will appear."
else
  echo "It didn't answer yet. Wait a few seconds and reload the wallpaper. Log: $DIR/stats.log"
fi
