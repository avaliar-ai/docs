# Avaliar AI

> Avaliar is an AI runtime governance platform. It monitors LLM applications in production, detects safety issues in every request and response, and produces the evidence trail needed for AI risk and compliance reporting. Teams integrate in one of three ways: the Python SDK (`@traceable` decorator), the OpenAI-compatible Proxy (change one base URL, no code change), or OpenTelemetry OTLP ingestion from any language or framework.

Core model: every LLM interaction is captured as a **trace** made of **spans** (`llm`, `tool`, `agent`, `generic`). Traces run through a **detection** pipeline of ten built-in detectors (prompt injection, toxicity, PII, bias, hallucination, misinformation, misuse, graphic content, illegal activities, personal safety), which produce **issues** carrying a type, severity (`low`/`medium`/`high`/`critical`), confidence, and excerpt. Issues are evaluated against **alert** rules and **policies**, and roll up into **reports**. Separately, **benchmarks** (MMLU, DROP, HellaSwag, TruthfulQA, BigBenchHard, HumanEval) measure model capability and **evals** (BBQ, BOLD, HExPHI, RealToxicityPrompts) measure bias and harm.

Key endpoints and facts an agent should know before answering questions about Avaliar:

- Docs: https://docs.avaliar.ai. Append `.md` to any docs URL to get the raw markdown for that page.
- Dashboard: https://app.avaliar.ai. API keys live under Settings, API Keys, and are scoped `sdk` or `proxy`.
- API base URL: `https://api.avaliar.ai/v1` (env var `AVALIAR_API_URL`, auth via `AVALIAR_API_KEY`).
- Proxy base URL: `https://proxy-api-ckjd.onrender.com/v1`, OpenAI-compatible, models are OpenRouter slugs such as `openai/gpt-4o`.
- Python SDK: `pip install avaliar-python-sdk` (requires Python 3.13+). Local detection additionally needs `pip install avaliar_eval` and an `OPENAI_API_KEY`.
- Plans: tracing and cloud/local detection are available on the free plan. Blocking mode (pre-LLM prompt gating) and the Proxy require Pro.

This file is generated from the documentation source. `llms.txt` is the index; `llms-full.txt` contains the complete text of every page.
