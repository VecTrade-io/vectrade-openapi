# VecTrade OpenAPI — Copilot Instructions

## Workflow

All agents follow the standard workflow defined in `instructions/agent-workflow.instructions.md`:
**Implement → Verify → Changelog → Commit**

## Agents

| Agent | When to Use |
|-------|------------|
| `@vt-api-designer` | Designing/modifying API spec |
| `@vt-spec-reviewer` | Reviewing spec changes, backward compatibility |

## Conventions

- OpenAPI 3.1 specification in `spec.yaml`
- All fields use `snake_case`
- Every endpoint needs: `operationId`, `summary`, `description`, `tags`, `security`
- Errors follow RFC 7807 Problem Details
- Pagination is cursor-based (`cursor` + `limit`)
- No breaking changes without version bump

## Downstream Consumers

Changes to this spec affect:
- `vectrade-python` (Python SDK)
- `vectrade-node` (TypeScript SDK)
- `vectrade-docs` (API reference pages)
- `vectrade-sdk-generator` (code generation)
- `vectrade-mcp` (MCP tool schemas)

## Validation

```bash
npx @redocly/cli lint spec.yaml
npx @stoplight/spectral-cli lint spec.yaml
```
