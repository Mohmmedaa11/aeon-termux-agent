#!/data/data/com.termux/files/usr/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -f .env ]; then cp .env.example .env; fi
set -a
. ./.env
set +a

command -v uvicorn >/dev/null 2>&1 || { echo 'uvicorn غير مثبت. شغّل: bash termux/install.sh'; exit 1; }
command -v tmux >/dev/null 2>&1 || { echo 'tmux غير مثبت. شغّل: pkg install tmux'; exit 1; }

tmux kill-session -t aeon-agent 2>/dev/null || true
tmux new-session -d -s aeon-agent "cd '$PROJECT_DIR' && set -a && . ./.env && set +a && exec uvicorn aeon_agent.server:app --host 127.0.0.1 --port 8787"

echo 'تم تشغيل الوكيل على http://127.0.0.1:8787'
echo 'عرض السجل: tmux attach -t aeon-agent'
echo 'إيقافه: tmux kill-session -t aeon-agent'
