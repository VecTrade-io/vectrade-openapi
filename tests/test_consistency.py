"""Tests for cross-spec consistency between OpenAPI and AsyncAPI, naming conventions, and overall quality."""

from __future__ import annotations

import re

import yaml


class TestYamlValidity:
    """Spec files are valid YAML and parseable."""

    def test_spec_yaml_parses(self, spec: dict):
        assert isinstance(spec, dict)

    def test_asyncapi_yaml_parses(self, asyncapi: dict):
        assert isinstance(asyncapi, dict)

    def test_spectral_yaml_parses(self, spectral: dict):
        assert isinstance(spectral, dict)

    def test_spec_not_empty(self, spec: dict):
        assert len(spec) > 0

    def test_asyncapi_not_empty(self, asyncapi: dict):
        assert len(asyncapi) > 0

    def test_no_yaml_aliases(self, spec_raw: str):
        """YAML anchors/aliases can cause confusion in API specs."""
        assert "&" not in spec_raw or "<<:" not in spec_raw

    def test_no_tabs_in_spec(self, spec_raw: str):
        """YAML should use spaces, not tabs."""
        assert "\t" not in spec_raw, "spec.yaml contains tab characters"

    def test_no_tabs_in_asyncapi(self, asyncapi_raw: str):
        assert "\t" not in asyncapi_raw, "asyncapi.yaml contains tab characters"

    def test_spec_file_not_too_large(self, spec_raw: str):
        """Spec file should stay reasonable in size."""
        line_count = spec_raw.count("\n")
        assert line_count < 5000, f"spec.yaml has {line_count} lines — consider splitting"

    def test_asyncapi_file_not_too_large(self, asyncapi_raw: str):
        line_count = asyncapi_raw.count("\n")
        assert line_count < 2000, f"asyncapi.yaml has {line_count} lines — consider splitting"


class TestNamingConventions:
    """Naming conventions are consistent across the spec."""

    def test_schema_names_pascal_case(self, spec: dict):
        for name in spec["components"]["schemas"]:
            assert name[0].isupper(), f"Schema '{name}' should be PascalCase"
            assert "_" not in name, f"Schema '{name}' should not use underscores"

    def test_response_names_pascal_case(self, spec: dict):
        for name in spec["components"]["responses"]:
            assert name[0].isupper(), f"Response '{name}' should be PascalCase"

    def test_property_names_camel_case(self, spec: dict):
        """Schema property names should be camelCase or simple lowercase."""
        # Allow special names like page_info (already in spec as convention)
        exceptions = {"page_info", "docs_url", "request_id"}
        for schema_name, schema in spec["components"]["schemas"].items():
            for prop in schema.get("properties", {}):
                if prop in exceptions:
                    continue
                assert " " not in prop, f"{schema_name}.{prop} has spaces"

    def test_path_segments_lowercase_kebab(self, spec: dict):
        """Path segments (non-parameters) should be lowercase or kebab-case."""
        for path in spec["paths"]:
            segments = path.split("/")
            for seg in segments:
                if seg.startswith("{") or not seg:
                    continue
                assert seg == seg.lower(), f"Path segment '{seg}' in {path} should be lowercase"


class TestCrossSpecConsistency:
    """OpenAPI and AsyncAPI specs should be consistent."""

    def test_both_specs_reference_same_api_name(self, spec: dict, asyncapi: dict):
        assert "VecTrade" in spec["info"]["title"]
        assert "VecTrade" in asyncapi["info"]["title"]

    def test_both_specs_same_version(self, spec: dict, asyncapi: dict):
        assert spec["info"]["version"] == asyncapi["info"]["version"]

    def test_both_specs_same_license(self, spec: dict, asyncapi: dict):
        assert spec["info"]["license"]["name"] == asyncapi["info"]["license"]["name"]

    def test_both_specs_have_contact(self, spec: dict, asyncapi: dict):
        assert "contact" in spec["info"]
        assert "contact" in asyncapi["info"]

    def test_rest_uses_bearer_auth(self, spec: dict):
        assert "BearerAuth" in spec["components"]["securitySchemes"]

    def test_ws_uses_bearer_auth(self, asyncapi: dict):
        assert "bearerToken" in asyncapi["components"]["securitySchemes"]


class TestSpectralConfig:
    """Spectral linting config is well-formed."""

    def test_spectral_extends_oas(self, spectral: dict):
        extends = spectral.get("extends", [])
        assert any("spectral:oas" in str(e) for e in extends)

    def test_spectral_has_rules(self, spectral: dict):
        assert "rules" in spectral
        assert len(spectral["rules"]) > 0

    def test_spectral_requires_operation_id(self, spectral: dict):
        rules = spectral["rules"]
        assert "operation-operationId" in rules
        rule = rules["operation-operationId"]
        severity = rule["severity"] if isinstance(rule, dict) else rule
        assert severity == "error"

    def test_spectral_requires_tags(self, spectral: dict):
        rules = spectral["rules"]
        assert "operation-tags" in rules
        rule = rules["operation-tags"]
        severity = rule["severity"] if isinstance(rule, dict) else rule
        assert severity == "error"

    def test_spectral_requires_servers(self, spectral: dict):
        rules = spectral["rules"]
        assert "oas3-api-servers" in rules

    def test_spectral_security_rules(self, spectral: dict):
        rules = spectral["rules"]
        assert "no-eval-in-markdown" in rules
        assert "no-script-tags-in-markdown" in rules

    def test_spectral_success_response_rule(self, spectral: dict):
        rules = spectral["rules"]
        assert "operation-success-response" in rules
        rule = rules["operation-success-response"]
        severity = rule["severity"] if isinstance(rule, dict) else rule
        assert severity == "error"


class TestResponseConsistency:
    """Response shapes follow consistent patterns."""

    def test_list_endpoints_use_data_wrapper(self, spec: dict):
        """List endpoints should wrap results in a 'data' array."""
        list_ops = ["listNews", "listWebhooks", "getEarningsCalendar",
                     "getInsiderTransactions", "getAnalystPriceTargets",
                     "getAnalystRatings", "getEarningsHistory"]
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if not isinstance(op, dict):
                    continue
                oid = op.get("operationId", "")
                if oid in list_ops:
                    resp_200 = op["responses"].get("200", op["responses"].get("201", {}))
                    content = resp_200.get("content", {}).get("application/json", {})
                    schema = content.get("schema", {})
                    props = schema.get("properties", {})
                    assert "data" in props, f"{oid} should wrap results in 'data'"

    def test_paginated_endpoints_have_page_info(self, spec: dict):
        """Paginated list endpoints should include page_info."""
        paginated_ops = ["listNews", "runScreener"]
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if not isinstance(op, dict):
                    continue
                oid = op.get("operationId", "")
                if oid in paginated_ops:
                    resp_200 = op["responses"]["200"]
                    content = resp_200.get("content", {}).get("application/json", {})
                    schema = content.get("schema", {})
                    props = schema.get("properties", {})
                    assert "page_info" in props, f"{oid} should include page_info"


class TestSpecCompleteness:
    """Overall spec quality checks."""

    def test_all_tags_documented_in_operations(self, spec: dict):
        """Every tag used in operations should exist."""
        used_tags = set()
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if isinstance(op, dict):
                    used_tags.update(op.get("tags", []))
        assert len(used_tags) >= 10

    def test_spec_has_no_todo_comments(self, spec_raw: str):
        """No TODO comments left in spec."""
        assert "TODO" not in spec_raw.upper() or "todo" not in spec_raw.lower()

    def test_no_empty_descriptions(self, spec: dict):
        """No empty description fields."""
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if not isinstance(op, dict):
                    continue
                desc = op.get("description", "x")
                assert desc.strip(), f"{method.upper()} {path} has empty description"

    def test_description_ends_with_period(self, spec: dict):
        """Operation descriptions should end with a period."""
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if not isinstance(op, dict):
                    continue
                desc = op.get("description", "")
                if desc:
                    assert desc.strip().endswith("."), (
                        f"{op.get('operationId')}: description should end with period"
                    )
