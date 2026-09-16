#!/usr/bin/env bash
# speedreader installer. No root. Installs into ~/.local only.
#
#   bash install.sh          install (or update)
#   bash uninstall.sh        remove
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo "do not run as root - this installs into your own home"; exit 1; }
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE="$HOME/.local/share/speedreader"
BIN="$HOME/.local/bin"

missing=()
for b in spd-say xclip xdotool xprop xwininfo paplay python3; do
  command -v "$b" >/dev/null || missing+=("$b")
done
python3 -c 'import speechd' 2>/dev/null || missing+=("python3-speechd")
python3 -c 'import gi; gi.require_version("Gtk","3.0")' 2>/dev/null || missing+=("python3-gi + gir1.2-gtk-3.0")
python3 -c 'import Xlib' 2>/dev/null || missing+=("python3-xlib")
if ((${#missing[@]})); then
  echo "missing: ${missing[*]}"
  echo
  echo "Debian / Ubuntu / Mint:"
  echo "  sudo apt install speech-dispatcher speech-dispatcher-espeak-ng python3-speechd \\"
  echo "       xclip xdotool x11-utils pulseaudio-utils python3-gi gir1.2-gtk-3.0 python3-xlib"
  echo "optional, for reading windows that expose no accessibility tree:"
  echo "  sudo apt install tesseract-ocr ffmpeg"
  exit 1
fi

install -d "$SHARE" "$BIN"
install -m 0755 "$SRC"/speedreader/*.py "$SHARE/"
for pair in "speedreader:reader.py" "speedreader-settings:settings.py" \
            "speedreader-voices:voice-lab.py" "speedreader-tray:tray.py"; do
  name="${pair%%:*}"; target="${pair##*:}"
  printf '#!/usr/bin/env bash\nexec "%s/%s" "$@"\n' "$SHARE" "$target" > "$BIN/$name"
  chmod 0755 "$BIN/$name"
done

# A desktop entry so the tray shows up in the app menu (and can be added to
# autostart or a panel). Written to the user's data dir - no root.
APPS="$HOME/.local/share/applications"
install -d "$APPS"
cat > "$APPS/speedreader-tray.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=SpeedReader (tray)
Comment=Read text aloud with a follow-along window
Exec=$BIN/speedreader-tray
Icon=media-playback-start
Terminal=false
Categories=Utility;Accessibility;
DESK
update-desktop-database "$APPS" >/dev/null 2>&1 || true

case ":$PATH:" in *":$BIN:"*) ;; *) echo "note: $BIN is not on your PATH";; esac

cat <<EOF

installed:
  speedreader            read what is highlighted; else the newest Claude reply; else a window
  speedreader --toggle   start picking (highlight text, or click a window) / stop if reading
  speedreader --settings voice, speed, level, redaction
  speedreader-voices     audition voices, sweep speeds

Try the tray icon:
  speedreader-tray                start it (left=read, right=read-along, middle=settings)

Start it automatically at login:
  ln -s "$APPS/speedreader-tray.desktop" ~/.config/autostart/ 2>/dev/null || \
    cp "$APPS/speedreader-tray.desktop" ~/.config/autostart/

Or bind the CLI to your own bar / hotkeys - see integrations/.
EOF
