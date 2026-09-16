#!/usr/bin/env bash
set -euo pipefail
rm -rf "$HOME/.local/share/readalong"
rm -f "$HOME/.local/bin"/{readalong,readalong-settings,readalong-voices}
echo "removed. config kept at ~/.config/readalong/ - delete it yourself if you want it gone."
