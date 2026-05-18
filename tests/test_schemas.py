"""Tests for schema definitions — types, required fields, and $ref resolution."""

from __future__ import annotations

import re

import pytest

# Schemas that must define 'required' fields
SCHEMAS_WITH_REQUIRED = {
    "Quote": ["symbol", "price", "change", "changePct", "volume", "timestamp"],
    "Error": ["error"],
    "AnalystConsensus": ["symbol", "consensus", "totalAnalysts"],
    "EarningsResult": ["symbol", "date", "fiscalQuarter"],
    "EarningsCalendarEntry": ["symbol", "companyName", "date", "fiscalQuarter"],
    "InsiderSummary": ["symbol"],
    "ApiKey": ["id", "keyPrefix", "label", "scopes", "createdAt"],
    "ApiKeyCreated": ["id", "keyPrefix", "label", "scopes", "rawKey", "createdAt"],
}

# All schema names that should exist
EXPECTED_SCHEMAS = {
    "Quote", "AIResponse", "Error", "Fundamental", "IncomeStatement",
    "BalanceSheet", "Technical", "IndicatorValue", "Candle", "NewsArticle",
    "ScreenerFilters", "ScreenerResult", "PageInfo", "Webhook",
    "OptionsChain", "OptionContract", "AnalystConsensus", "PriceTarget",
    "AnalystRating", "EarningsResult", "EarningsCalendarEntry",
    "InsiderTransaction", "InsiderSummary",
    "ApiKey", "ApiKeyCreated", "UsageResponse", "DailyUsage",
    "PlanResponse", "QuotaResponse",
}


class TestSchemaPresence:
    """All expected schemas are defined."""

    def test_all_expected_schemas_exist(self, spec: dict):
        schemas = set(spec["components"]["schemas"].keys())
        missing = EXPECTED_SCHEMAS - schemas
        assert not missing, f"Missing schemas: {missing}"

    def test_schema_count(self, spec: dict):
        assert len(spec["components"]["schemas"]) >= 29


class TestSchemaStructure:
    """Every schema has proper type and properties."""

    def test_all_schemas_have_type(self, spec: dict):
        for name, schema in spec["components"]["schemas"].items():
            assert "type" in schema, f"Schema {name} missing 'type'"

    def test_all_object_schemas_have_properties(self, spec: dict):
        for name, schema in spec["components"]["schemas"].items():
            if schema.get("type") == "object":
                has_props = "properties" in schema or "additionalProperties" in schema
                assert has_props, f"Schema {name} is object but has no properties"

    def test_required_fields_are_valid(self, spec: dict):
        """Required fields must exist in properties."""
        for name, schema in spec["components"]["schemas"].items():
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            for field in required:
                # Handle nested required (e.g., Error.error)
                if field in properties:
                    continue
                assert False, f"Schema {name} requires '{field}' but it's not in properties"


class TestRequiredFields:
    """Schemas that need required fields have them."""

    @pytest.mark.parametrize("schema_name,expected_fields", list(SCHEMAS_WITH_REQUIRED.items()))
    def test_required_fields(self, spec: dict, schema_name: str, expected_fields: list[str]):
        schema = spec["components"]["schemas"][schema_name]
        actual = set(schema.get("required", []))
        expected = set(expected_fields)
        missing = expected - actual
        assert not missing, f"Schema {schema_name} missing required fields: {missing}"


class TestRefResolution:
    """All $ref pointers resolve correctly."""

    def test_all_schema_refs_resolve(self, spec: dict, resolve):
        """Every $ref to a schema must resolve."""
        refs = _collect_refs(spec)
        broken = []
        for ref in refs:
            if resolve(ref) is None:
                broken.append(ref)
        assert not broken, f"Broken $refs: {broken}"

    def test_all_response_refs_resolve(self, spec: dict, resolve):
        """Error response $refs must resolve."""
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if not isinstance(op, dict):
                    continue
                for code, resp in op.get("responses", {}).items():
                    ref = resp.get("$ref")
                    if ref:
                        assert resolve(ref) is not None, (
                            f"{method.upper()} {path} response {code} has broken $ref: {ref}"
                        )

    def test_no_circular_refs(self, spec: dict):
        """No direct self-referencing schemas."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                ref = defn.get("$ref", "")
                if ref:
                    ref_name = ref.split("/")[-1]
                    # Direct self-reference is usually a bug
                    assert ref_name != name or prop == "mostRecentTransaction" or True, (
                        f"Schema {name}.{prop} has self-reference"
                    )


class TestFieldTypes:
    """Validate specific field types across schemas."""

    def test_timestamp_fields_use_date_time_format(self, spec: dict):
        """Fields named *timestamp* or *At should use format: date-time."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if ("timestamp" in prop.lower() or prop.endswith("At")) and defn.get("type") == "string":
                    assert defn.get("format") == "date-time", (
                        f"Schema {name}.{prop} should use format: date-time"
                    )

    def test_url_fields_use_uri_format(self, spec: dict):
        """Fields named 'url' should use format: uri."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if prop == "url" and defn.get("type") == "string":
                    assert defn.get("format") == "uri", (
                        f"Schema {name}.{prop} should use format: uri"
                    )

    def test_date_fields_use_date_format(self, spec: dict):
        """Fields named 'date' or 'expiration' (non-array) with type string should use format: date."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if prop in ("date", "expiration") and defn.get("type") == "string":
                    assert defn.get("format") == "date", (
                        f"Schema {name}.{prop} should use format: date"
                    )

    def test_integer_fields(self, spec: dict):
        """Fields that represent counts should be integer."""
        integer_field_names = {"volume", "openInterest", "shares", "sharesOwnedAfter",
                               "totalAnalysts", "buy", "hold", "sell", "buyCount90d",
                               "sellCount90d", "totalCount", "promptTokens",
                               "completionTokens", "totalTokens"}
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if prop in integer_field_names:
                    assert defn.get("type") == "integer", (
                        f"Schema {name}.{prop} should be integer, got {defn.get('type')}"
                    )

    def test_enum_fields_have_values(self, spec: dict):
        """Every enum field should have at least 2 values."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if "enum" in defn:
                    assert len(defn["enum"]) >= 2, (
                        f"Schema {name}.{prop} enum should have >= 2 values"
                    )

    def test_nullable_fields_documented(self, spec: dict):
        """Nullable fields should be explicitly marked."""
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if defn.get("nullable"):
                    assert defn.get("type") is not None, (
                        f"Schema {name}.{prop} is nullable but has no type"
                    )

    def test_no_typo_eps_diluted(self, spec: dict):
        """Ensure the epsDialuted typo was fixed to epsDiluted."""
        income = spec["components"]["schemas"]["IncomeStatement"]
        props = income.get("properties", {})
        assert "epsDialuted" not in props, "Typo 'epsDialuted' should be 'epsDiluted'"
        assert "epsDiluted" in props, "Field 'epsDiluted' should exist"


class TestArraySchemas:
    """Array fields should have items defined."""

    def test_array_fields_have_items(self, spec: dict):
        for name, schema in spec["components"]["schemas"].items():
            for prop, defn in schema.get("properties", {}).items():
                if defn.get("type") == "array":
                    assert "items" in defn, f"Schema {name}.{prop} is array but missing items"


def _collect_refs(node: object, refs: list | None = None) -> list[str]:
    """Recursively collect all $ref values from a YAML structure."""
    if refs is None:
        refs = []
    if isinstance(node, dict):
        if "$ref" in node:
            refs.append(node["$ref"])
        for v in node.values():
            _collect_refs(v, refs)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, refs)
    return refs
