# Avaliar AI Documentation

Developer documentation for the [Avaliar AI](https://avaliar.ai) observability platform. Built with [Mintlify](https://mintlify.com).

## Overview

Avaliar is an AI observability platform that monitors, detects, and fixes safety issues in LLM applications. This repository contains the source for our developer documentation at [docs.avaliar.ai](https://docs.avaliar.ai).

### Documentation Structure

- **Getting Started** — Platform overview, quickstart guide, core concepts
- **Python SDK** — Installation, `@traceable` decorator, detection, benchmarks
- **Proxy Integration** — Proxy gateway setup and architecture
- **Detection** — 6 detector types, local vs cloud modes
- **Benchmarks & Evals** — MMLU, DROP, HellaSwag, TruthfulQA, BigBenchHard, HumanEval, BBQ, HEx-PHI
- **Platform** — Traces, analytics, alerts, reports, team management, API keys
- **Architecture** — Event-sourced trace system, data flow
- **API Reference** — Complete REST API documentation with OpenAPI spec

## Development

Install the [Mintlify CLI](https://www.npmjs.com/package/mint) to preview documentation changes locally:

```bash
npm i -g mint
```

Run the development server:

```bash
mint dev
```

View your local preview at `http://localhost:3000`.

## Publishing

Changes pushed to the `main` branch are automatically deployed via the Mintlify GitHub integration.

## Resources

- [Avaliar Dashboard](https://app.avaliar.ai)
- [Python SDK](https://pypi.org/project/avaliar-python-sdk/)
- [GitHub Organization](https://github.com/avaliar-ai)
