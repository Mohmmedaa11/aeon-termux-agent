#!/data/data/com.termux/files/usr/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -f .env ]; then cp .env.example .env; fi
set -a
. ./.env
set +a

command -v tmux >/dev/null 2>&1 || { echo 'tmux غير مثبت. شغّل: pkg install tmux'; exit 1; }

tmux kill-session -t aeon-agent 2>/dev/null || true
LOG_FILE="$PROJECT_DIR/.aeon-agent.log"
tmux new-session -d -s aeon-agent "cd '$PROJECT_DIR' && exec python -m aeon_agent.server >> '$LOG_FILE' 2>&1"

sleep 1
if ! tmux has-session -t aeon-agent 2>/dev/null; then
  echo 'فشل تشغيل الوكيل. آخر سجل للخطأ:'
  tail -n 30 "$LOG_FILE" 2>/dev/null || true
  exit 1
fi

echo 'تم تشغيل الوكيل على http://127.0.0.1:8787'
echo 'عرض السجل: tmux attach -t aeon-agent'
echo 'إيقافه: tmux kill-session -t aeon-agent'
