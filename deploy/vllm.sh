#!/usr/bin/env bash
set -euo pipefail
: "${MODEL_NAME:=AEON-7/Qwen3.8-27B-AEON-ULTIMATE-UNCENSORED-BF16}"
: "${HF_TOKEN:=}"
command -v vllm >/dev/null || { echo 'Install vLLM on a CUDA host first: pip install vllm'; exit 1; }
exec vllm serve "$MODEL_NAME" \
  --dtype bfloat16 \
  --max-model-len "${MAX_MODEL_LEN:-16384}" \
  --max-num-seqs "${MAX_NUM_SEQS:-4}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.85}" \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --trust-remote-code \
  --host 127.0.0.1 --port 8000
