"""Tests for individual endpoint behavior — verifying each path in the spec."""

from __future__ import annotations

import pytest


class TestQuotesEndpoints:
    """Tests for /vq/quotes/* endpoints."""

    def test_get_quote_has_symbol_param(self, spec: dict):
        op = spec["paths"]["/vq/quotes/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "symbol" in params
        assert params["symbol"]["in"] == "path"
        assert params["symbol"]["required"] is True

    def test_get_quote_has_fields_param(self, spec: dict):
        op = spec["paths"]["/vq/quotes/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "fields" in params
        assert params["fields"]["in"] == "query"

    def test_batch_quotes_has_symbols_param(self, spec: dict):
        op = spec["paths"]["/vq/quotes/batch"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "symbols" in params
        assert params["symbols"]["required"] is True

    def test_batch_quotes_returns_array(self, spec: dict):
        op = spec["paths"]["/vq/quotes/batch"]["get"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        assert "data" in schema["properties"]
        assert schema["properties"]["data"]["type"] == "array"


class TestFundamentalsEndpoints:
    """Tests for /vq/fundamentals/* endpoints."""

    def test_get_fundamentals_returns_fundamental_schema(self, spec: dict):
        op = spec["paths"]["/vq/fundamentals/{symbol}"]["get"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("/Fundamental")

    def test_income_statement_has_period_param(self, spec: dict):
        op = spec["paths"]["/vq/fundamentals/{symbol}/income-statement"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "period" in params
        assert set(params["period"]["schema"]["enum"]) == {"annual", "quarterly"}

    def test_income_statement_has_limit_param(self, spec: dict):
        op = spec["paths"]["/vq/fundamentals/{symbol}/income-statement"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "limit" in params
        assert params["limit"]["schema"]["default"] == 4

    def test_balance_sheet_has_period_param(self, spec: dict):
        op = spec["paths"]["/vq/fundamentals/{symbol}/balance-sheet"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "period" in params


class TestTechnicalsEndpoint:
    """Tests for /vq/technicals/{symbol}."""

    def test_technicals_has_indicators_param(self, spec: dict):
        op = spec["paths"]["/vq/technicals/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "indicators" in params

    def test_technicals_has_interval_enum(self, spec: dict):
        op = spec["paths"]["/vq/technicals/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        interval = params["interval"]
        assert "enum" in interval["schema"]
        assert "1d" in interval["schema"]["enum"]


class TestNewsEndpoints:
    """Tests for /vq/news/* endpoints."""

    def test_list_news_pagination(self, spec: dict):
        op = spec["paths"]["/vq/news"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "cursor" in params
        assert "limit" in params
        assert params["limit"]["schema"]["maximum"] == 100

    def test_list_news_symbol_filter(self, spec: dict):
        op = spec["paths"]["/vq/news"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "symbols" in params

    def test_get_news_article_by_id(self, spec: dict):
        op = spec["paths"]["/vq/news/{id}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "id" in params


class TestScreenerEndpoint:
    """Tests for /vq/screener."""

    def test_screener_is_post(self, spec: dict):
        assert "post" in spec["paths"]["/vq/screener"]

    def test_screener_uses_screener_filters_schema(self, spec: dict):
        op = spec["paths"]["/vq/screener"]["post"]
        rb_ref = op["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        assert rb_ref.endswith("/ScreenerFilters")

    def test_screener_has_pagination(self, spec: dict):
        op = spec["paths"]["/vq/screener"]["post"]
        params = {p["name"]: p for p in op.get("parameters", [])}
        assert "cursor" in params
        assert "limit" in params

    def test_screener_limit_max(self, spec: dict):
        op = spec["paths"]["/vq/screener"]["post"]
        params = {p["name"]: p for p in op.get("parameters", [])}
        assert params["limit"]["schema"]["maximum"] == 200

    def test_screener_has_422(self, spec: dict):
        op = spec["paths"]["/vq/screener"]["post"]
        assert "422" in op["responses"]


class TestAIEndpoint:
    """Tests for /vq/ai/analyze."""

    def test_ai_is_post(self, spec: dict):
        assert "post" in spec["paths"]["/vq/ai/analyze"]

    def test_ai_request_requires_prompt(self, spec: dict):
        op = spec["paths"]["/vq/ai/analyze"]["post"]
        rb = op["requestBody"]["content"]["application/json"]["schema"]
        assert "prompt" in rb["required"]

    def test_ai_supports_streaming(self, spec: dict):
        op = spec["paths"]["/vq/ai/analyze"]["post"]
        content = op["responses"]["200"]["content"]
        assert "text/event-stream" in content

    def test_ai_has_422(self, spec: dict):
        op = spec["paths"]["/vq/ai/analyze"]["post"]
        assert "422" in op["responses"]


class TestWebhooksEndpoints:
    """Tests for /vq/webhooks/* endpoints."""

    def test_list_webhooks_is_get(self, spec: dict):
        assert "get" in spec["paths"]["/vq/webhooks"]

    def test_create_webhook_is_post(self, spec: dict):
        assert "post" in spec["paths"]["/vq/webhooks"]

    def test_create_webhook_requires_url_and_events(self, spec: dict):
        op = spec["paths"]["/vq/webhooks"]["post"]
        rb = op["requestBody"]["content"]["application/json"]["schema"]
        assert set(rb["required"]) == {"url", "events"}

    def test_create_webhook_events_enum(self, spec: dict):
        op = spec["paths"]["/vq/webhooks"]["post"]
        rb = op["requestBody"]["content"]["application/json"]["schema"]
        events_enum = rb["properties"]["events"]["items"]["enum"]
        assert "quote.update" in events_enum
        assert "news.published" in events_enum

    def test_delete_webhook_returns_204(self, spec: dict):
        op = spec["paths"]["/vq/webhooks/{id}"]["delete"]
        assert "204" in op["responses"]

    def test_create_webhook_returns_201(self, spec: dict):
        op = spec["paths"]["/vq/webhooks"]["post"]
        assert "201" in op["responses"]


class TestOptionsEndpoints:
    """Tests for /vq/options/* endpoints."""

    def test_options_chain_has_expiration_filter(self, spec: dict):
        op = spec["paths"]["/vq/options/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "expiration" in params
        assert params["expiration"]["schema"]["format"] == "date"

    def test_options_chain_has_type_filter(self, spec: dict):
        op = spec["paths"]["/vq/options/{symbol}"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "type" in params
        assert set(params["type"]["schema"]["enum"]) == {"call", "put"}

    def test_expirations_returns_date_array(self, spec: dict):
        op = spec["paths"]["/vq/options/{symbol}/expirations"]["get"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        items = schema["properties"]["data"]["items"]
        assert items["type"] == "string"
        assert items["format"] == "date"


class TestAnalystEndpoints:
    """Tests for /vq/analyst/* endpoints."""

    def test_consensus_returns_consensus_schema(self, spec: dict):
        op = spec["paths"]["/vq/analyst/{symbol}/consensus"]["get"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("/AnalystConsensus")

    def test_price_targets_returns_array(self, spec: dict):
        op = spec["paths"]["/vq/analyst/{symbol}/price-targets"]["get"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["properties"]["data"]["type"] == "array"

    def test_ratings_has_limit(self, spec: dict):
        op = spec["paths"]["/vq/analyst/{symbol}/ratings"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "limit" in params


class TestEarningsEndpoints:
    """Tests for /vq/earnings/* endpoints."""

    def test_history_returns_array(self, spec: dict):
        op = spec["paths"]["/vq/earnings/{symbol}/history"]["get"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["properties"]["data"]["type"] == "array"

    def test_history_has_limit(self, spec: dict):
        op = spec["paths"]["/vq/earnings/{symbol}/history"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "limit" in params
        assert params["limit"]["schema"]["default"] == 8

    def test_calendar_has_date_range(self, spec: dict):
        op = spec["paths"]["/vq/earnings/calendar"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "from" in params
        assert "to" in params
        assert params["from"]["schema"]["format"] == "date"
        assert params["to"]["schema"]["format"] == "date"


class TestInsiderEndpoints:
    """Tests for /vq/insider/* endpoints."""

    def test_transactions_returns_array(self, spec: dict):
        op = spec["paths"]["/vq/insider/{symbol}/transactions"]["get"]
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["properties"]["data"]["type"] == "array"

    def test_transactions_has_limit(self, spec: dict):
        op = spec["paths"]["/vq/insider/{symbol}/transactions"]["get"]
        params = {p["name"]: p for p in op["parameters"]}
        assert "limit" in params

    def test_summary_returns_insider_summary_schema(self, spec: dict):
        op = spec["paths"]["/vq/insider/{symbol}/summary"]["get"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("/InsiderSummary")

    def test_insider_summary_references_transaction(self, spec: dict):
        schema = spec["components"]["schemas"]["InsiderSummary"]
        most_recent = schema["properties"]["mostRecentTransaction"]
        assert "$ref" in most_recent
        assert most_recent["$ref"].endswith("/InsiderTransaction")
