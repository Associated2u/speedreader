#!/usr/bin/env bash
# readalong installer. No root. Installs into ~/.local only.
#
#   bash install.sh          install (or update)
#   bash uninstall.sh        remove
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo "do not run as root - this installs into your own home"; exit 1; }
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE="$HOME/.local/share/readalong"
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
install -m 0755 "$SRC"/readalong/*.py "$SHARE/"
for pair in "readalong:reader.py" "readalong-settings:settings.py" "readalong-voices:voice-lab.py"; do
  name="${pair%%:*}"; target="${pair##*:}"
  printf '#!/usr/bin/env bash\nexec "%s/%s" "$@"\n' "$SHARE" "$target" > "$BIN/$name"
  chmod 0755 "$BIN/$name"
done

case ":$PATH:" in *":$BIN:"*) ;; *) echo "note: $BIN is not on your PATH";; esac

cat <<EOF

installed:
  readalong            read what is highlighted; else the newest Claude reply; else a window
  readalong --toggle   start picking (highlight text, or click a window) / stop if reading
  readalong --settings voice, speed, what left-click does
  readalong-voices     audition voices, sweep speeds

bind --toggle to a button or key and --settings to a right-click. See integrations/.
EOF
