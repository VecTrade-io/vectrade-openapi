# VecTrade OpenAPI Specification

[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-openapi)](LICENSE)
[![CI](https://github.com/VecTrade-io/vectrade-openapi/actions/workflows/ci.yml/badge.svg)](https://github.com/VecTrade-io/vectrade-openapi/actions/workflows/ci.yml)

The single source of truth for the VecTrade public API surface.

## Files

| File | Format | Description |
|------|--------|-------------|
| `spec.yaml` | OpenAPI 3.1 | REST API specification (22 operations, 23 schemas) |
| `asyncapi.yaml` | AsyncAPI 3.0 | WebSocket/SSE real-time event specification |
| `.spectral.yaml` | Spectral | OpenAPI lint rules |

## Quick Start

```bash
# Run spec validation tests (Python)
pip install pyyaml pytest
python -m pytest tests/ -v

# Lint with Spectral (Node.js)
npx @stoplight/spectral-cli lint spec.yaml --ruleset .spectral.yaml

# Generate docs
npx @redocly/cli build-docs spec.yaml -o docs/index.html

# Check for breaking changes
npx oasdiff breaking spec.yaml <previous-spec>
```

## API Coverage

- **Quotes** — Real-time and batch quotes
- **Fundamentals** — Company data, income statements, balance sheets
- **Technicals** — Indicators (SMA, EMA, RSI, MACD, Bollinger) and candles
- **News** — Financial news with sentiment
- **Screener** — Custom stock screening
- **AI** — AI-powered analysis with streaming support
- **Webhooks** — Event subscriptions
- **Options** — Options chains and expirations
- **Analyst** — Consensus, price targets, rating changes
- **Earnings** — Historical results and calendar
- **Insider** — Transactions and trading summaries

## SDK Generation

SDKs are generated from this spec. Do not edit SDK code directly — update this spec and regenerate.

## Documentation

Rendered API docs: [docs.vectrade.io/api-reference](https://docs.vectrade.io/api-reference).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

Apache-2.0
