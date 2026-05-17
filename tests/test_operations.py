"""Tests for all OpenAPI operations — completeness, consistency, and quality."""

from __future__ import annotations

import pytest

# Expected operationIds for regression checking
EXPECTED_OPERATION_IDS = {
    "getQuote",
    "getBatchQuotes",
    "getFundamentals",
    "getIncomeStatement",
    "getBalanceSheet",
    "getTechnicals",
    "listNews",
    "getNewsArticle",
    "runScreener",
    "analyzeAI",
    "listWebhooks",
    "createWebhook",
    "deleteWebhook",
    "getOptionsChain",
    "getOptionsExpirations",
    "getAnalystConsensus",
    "getAnalystPriceTargets",
    "getAnalystRatings",
    "getEarningsHistory",
    "getEarningsCalendar",
    "getInsiderTransactions",
    "getInsiderSummary",
}

# Tags that must exist
EXPECTED_TAGS = {"Quotes", "Fundamentals", "Technicals", "News", "Screener", "AI", "Webhooks",
                 "Options", "Analyst", "Earnings", "Insider"}


class TestOperationCompleteness:
    """Every operation must have required fields."""

    def test_all_operations_have_operation_id(self, operations):
        for method, path, op in operations:
            assert "operationId" in op, f"{method.upper()} {path} missing operationId"

    def test_all_operations_have_summary(self, operations):
        for method, path, op in operations:
            assert "summary" in op, f"{method.upper()} {path} missing summary"

    def test_all_operations_have_description(self, operations):
        for method, path, op in operations:
            assert "description" in op, f"{method.upper()} {path} missing description"

    def test_all_operations_have_tags(self, operations):
        for method, path, op in operations:
            assert op.get("tags"), f"{method.upper()} {path} missing tags"

    def test_all_operations_have_responses(self, operations):
        for method, path, op in operations:
            assert "responses" in op, f"{method.upper()} {path} missing responses"
            assert len(op["responses"]) >= 1


class TestOperationIds:
    """Operation ID uniqueness and naming conventions."""

    def test_operation_ids_unique(self, operations):
        ids = [op["operationId"] for _, _, op in operations]
        assert len(ids) == len(set(ids)), f"Duplicate operationIds: {[x for x in ids if ids.count(x) > 1]}"

    def test_expected_operations_present(self, operations):
        ids = {op["operationId"] for _, _, op in operations}
        missing = EXPECTED_OPERATION_IDS - ids
        assert not missing, f"Missing expected operations: {missing}"

    def test_operation_id_naming_convention(self, operations):
        """operationIds should be camelCase."""
        for _, path, op in operations:
            oid = op["operationId"]
            assert oid[0].islower(), f"{oid} should start lowercase"
            assert " " not in oid, f"{oid} should not contain spaces"
            assert "-" not in oid, f"{oid} should not contain hyphens"

    def test_operation_count(self, operations):
        assert len(operations) == 22


class TestErrorResponses:
    """Every operation must include standard error responses."""

    def test_all_operations_have_401(self, operations):
        for method, path, op in operations:
            assert "401" in op["responses"], f"{method.upper()} {path} missing 401"

    def test_all_operations_have_429(self, operations):
        for method, path, op in operations:
            assert "429" in op["responses"], f"{method.upper()} {path} missing 429"

    def test_symbol_paths_have_404(self, operations):
        for method, path, op in operations:
            if "{symbol}" in path or "{id}" in path:
                assert "404" in op["responses"], f"{method.upper()} {path} missing 404"

    def test_post_operations_have_success_response(self, operations):
        for method, path, op in operations:
            if method == "post":
                has_success = any(str(c).startswith("2") for c in op["responses"])
                assert has_success, f"POST {path} missing 2xx response"

    def test_delete_has_204(self, operations):
        for method, path, op in operations:
            if method == "delete":
                assert "204" in op["responses"], f"DELETE {path} should return 204"

    def test_error_responses_use_refs(self, operations):
        """Error responses should use $ref to standard components."""
        for method, path, op in operations:
            for code in ("401", "429"):
                if code in op["responses"]:
                    resp = op["responses"][code]
                    assert "$ref" in resp, f"{method.upper()} {path} {code} should use $ref"


class TestTags:
    """Tag organization and coverage."""

    def test_expected_tags_used(self, operations):
        used_tags = set()
        for _, _, op in operations:
            used_tags.update(op.get("tags", []))
        missing = EXPECTED_TAGS - used_tags
        assert not missing, f"Expected tags not used: {missing}"

    def test_each_operation_has_exactly_one_tag(self, operations):
        for _, path, op in operations:
            tags = op.get("tags", [])
            assert len(tags) == 1, f"{path} should have exactly one tag, got {tags}"


class TestParameters:
    """Parameter definitions are well-formed."""

    def test_path_params_required(self, operations):
        for method, path, op in operations:
            for param in op.get("parameters", []):
                if param.get("in") == "path":
                    assert param.get("required") is True, (
                        f"{method.upper()} {path} path param '{param.get('name')}' must be required"
                    )

    def test_parameters_have_schema(self, operations):
        for method, path, op in operations:
            for param in op.get("parameters", []):
                assert "schema" in param, (
                    f"{method.upper()} {path} param '{param.get('name')}' missing schema"
                )

    def test_path_params_defined_in_operation(self, operations):
        """Every {param} in path should have a matching parameter definition."""
        import re
        for method, path, op in operations:
            path_params = set(re.findall(r"\{(\w+)\}", path))
            defined_params = {
                p["name"] for p in op.get("parameters", []) if p.get("in") == "path"
            }
            missing = path_params - defined_params
            assert not missing, f"{method.upper()} {path} missing path param definitions: {missing}"

    def test_query_params_have_type(self, operations):
        for method, path, op in operations:
            for param in op.get("parameters", []):
                if param.get("in") == "query":
                    schema = param.get("schema", {})
                    assert "type" in schema or "$ref" in schema, (
                        f"{method.upper()} {path} query param '{param.get('name')}' missing type"
                    )


class TestRequestBodies:
    """POST/PUT operations should have request bodies."""

    def test_post_operations_have_request_body(self, operations):
        for method, path, op in operations:
            if method == "post":
                assert "requestBody" in op, f"POST {path} missing requestBody"

    def test_request_bodies_are_json(self, operations):
        for method, path, op in operations:
            rb = op.get("requestBody")
            if rb:
                content = rb.get("content", {})
                assert "application/json" in content, (
                    f"{method.upper()} {path} requestBody should accept application/json"
                )

    def test_request_bodies_marked_required(self, operations):
        for method, path, op in operations:
            rb = op.get("requestBody")
            if rb:
                assert rb.get("required") is True, (
                    f"{method.upper()} {path} requestBody should be required"
                )
