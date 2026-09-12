#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a
command -v tmux >/dev/null || { echo 'Install tmux: pkg install tmux'; exit 1; }
tmux new-session -d -s aeon-agent 'uvicorn aeon_agent.server:app --host 127.0.0.1 --port 8787'
echo 'Agent started in tmux session aeon-agent on http://127.0.0.1:8787'
echo 'Attach with: tmux attach -t aeon-agent'
