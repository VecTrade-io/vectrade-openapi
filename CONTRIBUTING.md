# Contributing to VecTrade OpenAPI

Thank you for your interest in contributing to the VecTrade API specification.

## Getting Started

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run validation: `pip install pyyaml pytest && python -m pytest tests/ -v`
5. Submit a pull request

## Spec Guidelines

- **OpenAPI 3.1** for REST endpoints (`spec.yaml`)
- **AsyncAPI 3.0** for WebSocket/SSE channels (`asyncapi.yaml`)
- Every operation must have: `operationId`, `summary`, `description`, `tags`
- Every operation must include `401` and `429` error responses
- Resource endpoints with `{symbol}` or `{id}` must include `404`
- Schema names use **PascalCase**, properties use **camelCase**
- `operationId` values use **camelCase**
- Timestamp fields use `format: date-time`, URL fields use `format: uri`

## Validation

```bash
# Run spec validation tests
pip install pyyaml pytest
python -m pytest tests/ -v

# Run Spectral lint (requires Node.js)
npx @stoplight/spectral-cli lint spec.yaml --ruleset .spectral.yaml
```

## Pull Request Checklist

- [ ] All validation tests pass
- [ ] Spectral lint passes with no errors
- [ ] New endpoints include all required fields (operationId, description, error responses)
- [ ] New schemas have appropriate `required` fields and types
- [ ] Breaking changes are documented

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.
