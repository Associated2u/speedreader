#!/usr/bin/env bash
set -euo pipefail
# stop a running tray first
"$HOME/.local/bin/speedreader-tray" --quit 2>/dev/null || true
rm -rf "$HOME/.local/share/speedreader"
rm -f "$HOME/.local/bin"/{speedreader,speedreader-settings,speedreader-voices,speedreader-tray}
rm -f "$HOME/.local/share/applications/speedreader-tray.desktop"
rm -f "$HOME/.config/autostart/speedreader-tray.desktop"
echo "removed. config kept at ~/.config/speedreader/ - delete it yourself if you want it gone."
