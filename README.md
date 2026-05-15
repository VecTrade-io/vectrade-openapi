# VecTrade OpenAPI Specification

[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-openapi)](LICENSE)

The single source of truth for the VecTrade public API surface.

## Files

- `spec.yaml` — OpenAPI 3.1 specification
- `.spectral.yaml` — Lint rules (Spectral)

## Usage

```bash
# Lint the spec
npx @stoplight/spectral-cli lint spec.yaml

# Generate docs
npx @redocly/cli build-docs spec.yaml -o docs/index.html

# Check for breaking changes (against main)
npx oasdiff breaking spec.yaml <previous-spec>
```

## SDK Generation

SDKs are generated from this spec using the `sdk-generator/` tooling. Do not edit SDK code directly — update this spec and regenerate.

## Documentation

Rendered API docs: [docs.vectrade.io/api-reference](https://docs.vectrade.io/api-reference).

## Contributing

1. Edit `spec.yaml`
2. Run `npx @stoplight/spectral-cli lint spec.yaml` to validate
3. Open a pull request

## License

Apache-2.0
