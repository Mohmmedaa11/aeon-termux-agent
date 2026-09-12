# AEON Termux Agent

وكيل محلي/بعيد قابل للتشغيل من الهاتف عبر Termux، متوافق مع واجهة OpenAI ويستخدم نموذج `AEON-7/Qwen3.8-27B-AEON-ULTIMATE-UNCENSORED-BF16` عبر vLLM أو أي خادم متوافق.

## مهم قبل التشغيل

- حجم النموذج المنشور يقارب **54GB بصيغة BF16**؛ الهاتف العادي لا يستطيع تشغيله مباشرة. استخدم خادم GPU، أو استبدل `MODEL_NAME` بنسخة مكمّمة مناسبة.
- المشروع لا يضم أوزان النموذج ولا مفاتيح API.
- أدوات الأمن مقيّدة بالأهداف التي تضعها في `ALLOWED_TARGETS`، وتنفذ فحوصات دفاعية منخفضة التأثير فقط. لا تستخدمه ضد أنظمة لا تملك تصريحًا مكتوبًا لاختبارها.

## المكونات

1. `aeon_agent/server.py`: واجهة HTTP بسيطة للدردشة واستدعاء الأدوات.
2. `aeon_agent/llm.py`: عميل OpenAI-compatible لـ vLLM أو Hugging Face Inference Endpoint.
3. `tools/`: أدوات آمنة: DNS، فحص ترويسة HTTP، وملخص حالة خدمة محلية.
4. `deploy/vllm.sh`: تشغيل النموذج على خادم GPU.
5. `termux/`: تشغيل العميل من الهاتف داخل Termux.

## تشغيل خادم النموذج

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
export HF_TOKEN=your_token_if_required
bash deploy/vllm.sh
```

السكربت يفتح vLLM على `127.0.0.1:8000`. للإتاحة من الهاتف، شغّل الوكيل عبر شبكة خاصة مثل Tailscale أو SSH reverse tunnel؛ لا تفتح المنفذ مباشرة على الإنترنت.

## تشغيل الوكيل

```bash
export LLM_BASE_URL=http://127.0.0.1:8000/v1
export MODEL_NAME=AEON-7/Qwen3.8-27B-AEON-ULTIMATE-UNCENSORED-BF16
export ALLOWED_TARGETS=example.com,localhost,127.0.0.1
uvicorn aeon_agent.server:app --host 0.0.0.0 --port 8787
```

## تشغيل من Termux

```bash
pkg update && pkg install python openssh tmux
git clone https://github.com/Mohmmedaa11/aeon-termux-agent
cd aeon-termux-agent
pip install -e .
cp .env.example .env
bash termux/start.sh
```

للوصول الآمن إلى جهاز التشغيل:

```bash
ssh -N -L 8787:127.0.0.1:8787 user@your-server
```

ثم استخدم `http://127.0.0.1:8787` على الهاتف.

## مثال API

```bash
curl -X POST http://127.0.0.1:8787/chat \
  -H 'content-type: application/json' \
  -d '{"message":"افحص ترويسة https://example.com"}'
```

## حدود أمنية

لا يوجد exploit runner، ولا brute force، ولا port scan عام، ولا تنفيذ shell عن بُعد. إذا احتجت اختبارًا احترافيًا، استخدم بيئة مختبرية معزولة مثل OWASP Juice Shop أو Metasploitable وبموافقة واضحة، ثم أضف أدواتك محليًا بعد مراجعة الصلاحيات.

## الترخيص

كود هذا المستودع MIT. راجع شروط نموذج Qwen ونسخة AEON-7 قبل الاستخدام التجاري أو إعادة التوزيع.
