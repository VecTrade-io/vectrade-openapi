"""Tests for OpenAPI spec top-level structure and metadata."""

from __future__ import annotations


class TestSpecVersion:
    """Validate OpenAPI version and format."""

    def test_openapi_version(self, spec: dict):
        assert spec["openapi"] == "3.1.0"

    def test_info_present(self, spec: dict):
        info = spec["info"]
        assert "title" in info
        assert "version" in info
        assert "description" in info

    def test_info_title(self, spec: dict):
        assert spec["info"]["title"] == "VecTrade API"

    def test_info_version_semver(self, spec: dict):
        version = spec["info"]["version"]
        parts = str(version).split(".")
        assert len(parts) == 3, f"Version {version} is not semver"
        assert all(p.isdigit() for p in parts)

    def test_info_contact(self, spec: dict):
        contact = spec["info"]["contact"]
        assert "name" in contact
        assert "email" in contact
        assert "url" in contact

    def test_info_license(self, spec: dict):
        lic = spec["info"]["license"]
        assert lic["name"] == "Apache 2.0"
        assert "url" in lic

    def test_info_description_has_auth(self, spec: dict):
        desc = spec["info"]["description"]
        assert "Authentication" in desc or "Bearer" in desc


class TestServers:
    """Validate server definitions."""

    def test_servers_present(self, spec: dict):
        assert "servers" in spec
        assert len(spec["servers"]) >= 1

    def test_server_url_is_https(self, spec: dict):
        for server in spec["servers"]:
            assert server["url"].startswith("https://")

    def test_server_has_description(self, spec: dict):
        for server in spec["servers"]:
            assert "description" in server


class TestSecurity:
    """Validate global security definitions."""

    def test_global_security_defined(self, spec: dict):
        assert "security" in spec
        assert len(spec["security"]) >= 1

    def test_bearer_auth_scheme(self, spec: dict):
        schemes = spec["components"]["securitySchemes"]
        assert "BearerAuth" in schemes
        bearer = schemes["BearerAuth"]
        assert bearer["type"] == "http"
        assert bearer["scheme"] == "bearer"

    def test_bearer_format_documented(self, spec: dict):
        bearer = spec["components"]["securitySchemes"]["BearerAuth"]
        assert "bearerFormat" in bearer


class TestPaths:
    """Validate path structure."""

    def test_paths_present(self, spec: dict):
        assert "paths" in spec
        assert len(spec["paths"]) > 0

    def test_all_paths_start_with_prefix(self, spec: dict):
        for path in spec["paths"]:
            assert path.startswith("/vq/"), f"Path {path} missing /vq/ prefix"

    def test_path_count(self, spec: dict):
        assert len(spec["paths"]) >= 21

    def test_no_trailing_slashes(self, spec: dict):
        for path in spec["paths"]:
            assert not path.endswith("/"), f"Path {path} has trailing slash"


class TestComponents:
    """Validate components section structure."""

    def test_schemas_present(self, spec: dict):
        assert "schemas" in spec["components"]
        assert len(spec["components"]["schemas"]) > 0

    def test_responses_present(self, spec: dict):
        assert "responses" in spec["components"]
        assert len(spec["components"]["responses"]) > 0

    def test_standard_error_responses_defined(self, spec: dict):
        responses = spec["components"]["responses"]
        for name in ("Unauthorized", "NotFound", "RateLimited", "ValidationError"):
            assert name in responses, f"Missing standard response: {name}"

    def test_error_responses_reference_error_schema(self, spec: dict):
        responses = spec["components"]["responses"]
        for name in ("Unauthorized", "NotFound", "RateLimited", "ValidationError"):
            resp = responses[name]
            content = resp.get("content", {})
            if content:
                json_content = content.get("application/json", {})
                ref = json_content.get("schema", {}).get("$ref", "")
                assert "Error" in ref, f"Response {name} should reference Error schema"

    def test_rate_limited_has_retry_after_header(self, spec: dict):
        rate_limited = spec["components"]["responses"]["RateLimited"]
        assert "headers" in rate_limited
        assert "Retry-After" in rate_limited["headers"]

    def test_rate_limited_has_rate_limit_headers(self, spec: dict):
        rate_limited = spec["components"]["responses"]["RateLimited"]
        headers = rate_limited["headers"]
        for h in ("X-VQ-RateLimit-Limit", "X-VQ-RateLimit-Remaining", "X-VQ-RateLimit-Reset"):
            assert h in headers, f"RateLimited missing header: {h}"
