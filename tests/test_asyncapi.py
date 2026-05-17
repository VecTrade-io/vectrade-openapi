"""Tests for AsyncAPI specification structure and completeness."""

from __future__ import annotations


EXPECTED_CHANNELS = {"quotes", "priceAlerts", "aiStream", "news"}

EXPECTED_OPERATIONS = {
    "subscribeQuotes",
    "receiveQuoteUpdates",
    "receiveAlerts",
    "receiveAIStream",
    "receiveNews",
}

EXPECTED_MESSAGES = {
    "SubscribeRequest",
    "UnsubscribeRequest",
    "QuoteUpdate",
    "AlertTriggered",
    "AIChunk",
    "AIDone",
    "NewsPublished",
}


class TestAsyncApiVersion:
    """Validate AsyncAPI version and top-level structure."""

    def test_asyncapi_version(self, asyncapi: dict):
        assert asyncapi["asyncapi"] == "3.0.0"

    def test_info_present(self, asyncapi: dict):
        info = asyncapi["info"]
        assert "title" in info
        assert "version" in info
        assert "description" in info

    def test_info_title(self, asyncapi: dict):
        assert asyncapi["info"]["title"] == "VecTrade Event API"

    def test_info_contact(self, asyncapi: dict):
        contact = asyncapi["info"]["contact"]
        assert "name" in contact
        assert "email" in contact

    def test_info_license(self, asyncapi: dict):
        lic = asyncapi["info"]["license"]
        assert lic["name"] == "Apache 2.0"

    def test_default_content_type(self, asyncapi: dict):
        assert asyncapi["defaultContentType"] == "application/json"


class TestAsyncApiServers:
    """Validate WebSocket server definitions."""

    def test_server_defined(self, asyncapi: dict):
        assert "production" in asyncapi["servers"]

    def test_server_protocol_wss(self, asyncapi: dict):
        server = asyncapi["servers"]["production"]
        assert server["protocol"] == "wss"

    def test_server_host(self, asyncapi: dict):
        server = asyncapi["servers"]["production"]
        assert "ws.vectrade.io" in server["host"]

    def test_server_has_security(self, asyncapi: dict):
        server = asyncapi["servers"]["production"]
        assert "security" in server

    def test_server_has_description(self, asyncapi: dict):
        server = asyncapi["servers"]["production"]
        assert "description" in server


class TestAsyncApiChannels:
    """Validate channel definitions."""

    def test_all_expected_channels_present(self, asyncapi: dict):
        channels = set(asyncapi.get("channels", {}).keys())
        missing = EXPECTED_CHANNELS - channels
        assert not missing, f"Missing channels: {missing}"

    def test_channels_have_address(self, asyncapi: dict):
        for name, channel in asyncapi["channels"].items():
            assert "address" in channel, f"Channel {name} missing address"

    def test_channels_have_description(self, asyncapi: dict):
        for name, channel in asyncapi["channels"].items():
            assert "description" in channel, f"Channel {name} missing description"

    def test_channels_have_messages(self, asyncapi: dict):
        for name, channel in asyncapi["channels"].items():
            assert "messages" in channel, f"Channel {name} missing messages"
            assert len(channel["messages"]) >= 1

    def test_channel_addresses_start_with_ws(self, asyncapi: dict):
        for name, channel in asyncapi["channels"].items():
            assert channel["address"].startswith("/ws/"), (
                f"Channel {name} address should start with /ws/"
            )

    def test_channel_address_versioned(self, asyncapi: dict):
        for name, channel in asyncapi["channels"].items():
            assert "/v1/" in channel["address"], (
                f"Channel {name} address should include /v1/"
            )


class TestAsyncApiOperations:
    """Validate operation definitions."""

    def test_all_expected_operations_present(self, asyncapi: dict):
        ops = set(asyncapi.get("operations", {}).keys())
        missing = EXPECTED_OPERATIONS - ops
        assert not missing, f"Missing operations: {missing}"

    def test_operations_have_action(self, asyncapi: dict):
        for name, op in asyncapi["operations"].items():
            assert "action" in op, f"Operation {name} missing action"
            assert op["action"] in ("send", "receive")

    def test_operations_have_channel_ref(self, asyncapi: dict):
        for name, op in asyncapi["operations"].items():
            assert "channel" in op, f"Operation {name} missing channel"
            assert "$ref" in op["channel"]

    def test_operations_have_summary(self, asyncapi: dict):
        for name, op in asyncapi["operations"].items():
            assert "summary" in op, f"Operation {name} missing summary"

    def test_operations_have_messages(self, asyncapi: dict):
        for name, op in asyncapi["operations"].items():
            assert "messages" in op, f"Operation {name} missing messages"
            assert len(op["messages"]) >= 1

    def test_subscribe_is_send_action(self, asyncapi: dict):
        sub = asyncapi["operations"]["subscribeQuotes"]
        assert sub["action"] == "send"

    def test_receive_operations_are_receive_action(self, asyncapi: dict):
        for name, op in asyncapi["operations"].items():
            if name.startswith("receive"):
                assert op["action"] == "receive", f"Operation {name} should be receive"


class TestAsyncApiMessages:
    """Validate message definitions."""

    def test_all_expected_messages_present(self, asyncapi: dict):
        messages = set(asyncapi["components"]["messages"].keys())
        missing = EXPECTED_MESSAGES - messages
        assert not missing, f"Missing messages: {missing}"

    def test_messages_have_payload(self, asyncapi: dict):
        for name, msg in asyncapi["components"]["messages"].items():
            assert "payload" in msg, f"Message {name} missing payload"

    def test_messages_have_name(self, asyncapi: dict):
        for name, msg in asyncapi["components"]["messages"].items():
            assert "name" in msg, f"Message {name} missing name field"

    def test_message_payloads_are_objects(self, asyncapi: dict):
        for name, msg in asyncapi["components"]["messages"].items():
            payload = msg["payload"]
            assert payload.get("type") == "object", (
                f"Message {name} payload should be object"
            )

    def test_message_payloads_have_required_fields(self, asyncapi: dict):
        for name, msg in asyncapi["components"]["messages"].items():
            payload = msg["payload"]
            assert "properties" in payload, f"Message {name} payload missing properties"

    def test_event_messages_have_type_const(self, asyncapi: dict):
        """Event messages (not requests) should have a 'type' const field."""
        event_messages = ["QuoteUpdate", "AlertTriggered", "AIChunk", "AIDone", "NewsPublished"]
        for name in event_messages:
            msg = asyncapi["components"]["messages"][name]
            props = msg["payload"]["properties"]
            assert "type" in props, f"Message {name} missing 'type' property"
            assert "const" in props["type"], f"Message {name} 'type' should use const"


class TestAsyncApiSecurity:
    """Validate security scheme."""

    def test_security_scheme_defined(self, asyncapi: dict):
        schemes = asyncapi["components"]["securitySchemes"]
        assert "bearerToken" in schemes

    def test_bearer_scheme_type(self, asyncapi: dict):
        bearer = asyncapi["components"]["securitySchemes"]["bearerToken"]
        assert bearer["type"] == "http"
        assert bearer["scheme"] == "bearer"


class TestAsyncApiMessageRefs:
    """Validate that channel message $refs resolve."""

    def test_channel_message_refs_resolve(self, asyncapi: dict):
        messages = asyncapi["components"]["messages"]
        for ch_name, channel in asyncapi["channels"].items():
            for msg_key, msg_ref in channel.get("messages", {}).items():
                ref = msg_ref.get("$ref", "")
                # Refs like #/components/messages/QuoteUpdate
                if ref.startswith("#/components/messages/"):
                    msg_name = ref.split("/")[-1]
                    assert msg_name in messages, (
                        f"Channel {ch_name} references unknown message: {msg_name}"
                    )

    def test_operation_channel_refs_resolve(self, asyncapi: dict):
        channels = asyncapi["channels"]
        for op_name, op in asyncapi["operations"].items():
            ch_ref = op["channel"]["$ref"]
            if ch_ref.startswith("#/channels/"):
                ch_name = ch_ref.split("/")[-1]
                assert ch_name in channels, (
                    f"Operation {op_name} references unknown channel: {ch_name}"
                )
