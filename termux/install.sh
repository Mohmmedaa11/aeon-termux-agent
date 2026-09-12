#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ "$(uname -o 2>/dev/null || true)" != "Android" ] && [ -z "${TERMUX_VERSION:-}" ] && [ ! -d /data/data/com.termux ]; then
  echo "هذا السكربت مخصص لتطبيق Termux على Android."
  exit 1
fi

PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

printf '\n[1/5] تحديث مستودعات Termux...\n'
pkg update -y
printf '\n[2/5] تثبيت المتطلبات...\n'
pkg install -y python git openssh tmux

printf '\n[3/5] تحديث pip وتثبيت مكتبات الوكيل...\n'
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -e "$PROJECT_DIR"

printf '\n[4/5] إنشاء ملف الإعداد...\n'
cd "$PROJECT_DIR"
if [ ! -f .env ]; then cp .env.example .env; fi
mkdir -p "$HOME/.local/bin"

printf '\n[5/5] إنشاء أوامر مختصرة...\n'
cat > "$HOME/.local/bin/aeon-start" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
cd "$PROJECT_DIR"
exec bash termux/start.sh
EOF
cat > "$HOME/.local/bin/aeon-stop" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
tmux kill-session -t aeon-agent 2>/dev/null || true
echo "AEON agent stopped."
EOF
cat > "$HOME/.local/bin/aeon-status" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
tmux has-session -t aeon-agent 2>/dev/null && echo "AEON agent is running" || echo "AEON agent is stopped"
EOF
chmod +x "$HOME/.local/bin/aeon-start" "$HOME/.local/bin/aeon-stop" "$HOME/.local/bin/aeon-status"

if ! echo ":$PATH:" | grep -q ":$HOME/.local/bin:"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  export PATH="$HOME/.local/bin:$PATH"
fi

echo
printf '%s\n' 'تم التثبيت بنجاح.' '1) عدّل الإعدادات: nano .env' '2) أنشئ نفق النموذج: ssh -N -L 8000:127.0.0.1:8000 user@SERVER' '3) في جلسة أخرى شغّل: aeon-start' '4) افحص الحالة: aeon-status'
