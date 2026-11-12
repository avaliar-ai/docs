# Avaliar AI

> Avaliar is an AI runtime governance platform. It monitors LLM applications in production, detects safety issues in every request and response, and produces the evidence trail needed for AI risk and compliance reporting. Teams integrate in one of three ways: the open-source Python SDK (a runtime guard inside the app: `Guard` checks at five checkpoints, decided by a policy file `avaliar.yaml`, recorded in a hash-chained local evidence log), the OpenAI-compatible Proxy (change one base URL, no code change), or OpenTelemetry OTLP ingestion from any language or framework.

Core model: every LLM interaction is captured as a **trace** made of **spans** (`llm`, `tool`, `agent`, `generic`). Traces run through a **detection** pipeline of ten built-in detectors (prompt injection, toxicity, PII, bias, hallucination, misinformation, misuse, graphic content, illegal activities, personal safety), which produce **issues** carrying a type, severity (`low`/`medium`/`high`/`critical`), confidence, and excerpt. Issues are evaluated against **alert** rules and **policies**, and roll up into **reports**. The Python SDK checks in the app's own process instead: rules (tier 0), local ONNX models (tier 1, `[local]` extra) and an optional deep check (tier 2: local Clef-Flash, Jev, LLM APIs, or Avaliar Cloud) score sixteen categories, and each decision is `allow`, `warn`, `redact`, `block` or `approve`.

Key endpoints and facts an agent should know before answering questions about Avaliar:

- Docs: https://docs.avaliar.ai. Append `.md` to any docs URL to get the raw markdown for that page.
- Dashboard: https://app.avaliar.ai. API keys live under Settings, API Keys, and are scoped `sdk` or `proxy`.
- API: the SDK has the API URL built in; `AVALIAR_API_URL` overrides it. Auth via `AVALIAR_API_KEY` (header `X-API-KEY`).
- Proxy base URL: `https://proxy-api-ckjd.onrender.com/v1`, OpenAI-compatible, models are OpenRouter slugs such as `openai/gpt-4o`.
- Python SDK: `pip install avaliar-python-sdk`, import `avaliar`, Python 3.11+. Extras: `local`, `otel`, `openai-agents`, `langchain`, `mcp`. `from avaliar import Guard; guard = Guard()` reads `./avaliar.yaml`; checks are `check_input`, `check_output`, `check_tool_call`, `check_tool_result`, `check_action` (async twins `acheck_*`), `check_tool_definitions` and `@guard.tool`. Checks return a `Decision` and never raise, except `AvaliarPolicyError` at construction and the opt-in `GuardBlocked` / `GuardUnavailable`. CLI: `avaliar setup`, `init`, `doctor`, `scan`, `logs`, `stats`, `verify`, `redteam`, `models`, `judge`, `sync`, `detectors`, `policy`. It makes no network calls to Avaliar without `AVALIAR_API_KEY`; with it, evidence records upload and guard traces appear on the dashboard. `@traceable` is now only an optional OpenTelemetry span helper.
- Plans: the Python SDK needs no account. Linking it to the dashboard uses an `sdk`-scoped key; the Avaliar Cloud deep check (`judge.provider: avaliar`) and the Proxy require Pro.

This file is generated from the documentation source. `llms.txt` is the index; `llms-full.txt` contains the complete text of every page.
