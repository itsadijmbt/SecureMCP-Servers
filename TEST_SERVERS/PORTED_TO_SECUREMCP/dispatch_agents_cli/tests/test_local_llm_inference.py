"""Tests for local router LLM inference endpoint (/llm/inference).

Validates that the router's LLMInferenceRequest schema accepts all payloads
that the SDK sends, including optional fields like model/provider/agent_name.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create a test client for the router service."""
    from fastapi import FastAPI

    from dispatch_cli.router.service import api_router

    app = FastAPI()
    app.include_router(api_router)

    return TestClient(app)


@pytest.fixture
def mock_call_provider():
    """Mock the LLM provider call so we don't need real API keys."""
    mock_response = {
        "content": "Hello!",
        "tool_calls": None,
        "finish_reason": "stop",
        "input_tokens": 10,
        "output_tokens": 5,
    }
    with patch(
        "dispatch_cli.router.local_llm.call_provider",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock:
        yield mock


@pytest.fixture
def mock_get_api_key():
    """Mock API key retrieval."""
    with patch(
        "dispatch_cli.router.local_llm.get_api_key",
        return_value="sk-test-key",
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def set_openai_env():
    """Set a fake API key so provider auto-detection works."""
    old = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-test"
    yield
    if old is None:
        os.environ.pop("OPENAI_API_KEY", None)
    else:
        os.environ["OPENAI_API_KEY"] = old


class TestLLMInferenceRequestValidation:
    """Test that the inference endpoint accepts all payload shapes the SDK sends."""

    def test_full_request_with_all_fields(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test request with all fields explicitly set (like sdk llm.chat with overrides)."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4o",
                "provider": "openai",
                "temperature": 0.7,
                "max_tokens": 100,
                "trace_id": "trace-123",
                "invocation_id": "inv-456",
                "agent_name": "my-agent",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Hello!"
        assert data["model"] == "gpt-4o"
        assert data["provider"] == "openai"

    def test_minimal_request_no_model_no_provider(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test request without model/provider — should use defaults.

        This is the most common SDK usage: llm.chat("hello") sends no model or provider.
        """
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 1.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"  # auto-detected from OPENAI_API_KEY

    def test_request_with_agent_name(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test that agent_name field is accepted (SDK v0.6+ sends this)."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4o",
                "provider": "openai",
                "agent_name": "my-cool-agent",
            },
        )
        assert response.status_code == 200

    def test_request_with_extra_headers(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test that extra_headers field is accepted."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4o",
                "provider": "openai",
                "extra_headers": {"X-Custom": "value"},
            },
        )
        assert response.status_code == 200

    def test_request_with_system_message(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test multi-message request with system prompt (llm.chat with system=)."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello"},
                ],
                "model": "gpt-4o",
                "provider": "openai",
            },
        )
        assert response.status_code == 200

    def test_request_with_tools(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test request with tool definitions for function calling."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "What's the weather?"}],
                "model": "gpt-4o",
                "provider": "openai",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
            },
        )
        assert response.status_code == 200

    def test_request_with_response_format(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Test request with JSON mode response format."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Return JSON"}],
                "model": "gpt-4o",
                "provider": "openai",
                "response_format": {"type": "json_object"},
            },
        )
        assert response.status_code == 200

    def test_unknown_extra_field_rejected(self, test_client):
        """Test that truly unknown fields are still rejected (StrictBaseModel)."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4o",
                "provider": "openai",
                "totally_fake_field": "should fail",
            },
        )
        assert response.status_code == 422


class TestLLMInferenceDefaultResolution:
    """Test that model/provider defaults are resolved correctly."""

    def test_no_provider_uses_env_key(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """When no provider specified, should detect from environment API keys."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should pick openai since OPENAI_API_KEY is set
        assert data["provider"] == "openai"

    def test_no_model_gets_default_for_provider(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """When model not specified, should use default model for the provider."""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "provider": "openai",
            },
        )
        assert response.status_code == 200

    def test_no_provider_no_env_keys_returns_400(self, test_client):
        """When no provider and no API keys in env, should return 400."""
        # Clear all provider env vars
        env_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "AZURE_OPENAI_API_KEY",
            "MISTRAL_API_KEY",
            "COHERE_API_KEY",
            "DEEPSEEK_API_KEY",
        ]
        saved = {}
        for var in env_vars:
            saved[var] = os.environ.pop(var, None)

        try:
            response = test_client.post(
                "/llm/inference",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                },
            )
            assert response.status_code == 400
            assert "No LLM provider" in response.json()["detail"]
        finally:
            for var, val in saved.items():
                if val is not None:
                    os.environ[var] = val


class TestSDKCompatibility:
    """Test that exact payloads from the SDK are accepted.

    These payloads are captured from SDK v0.6.6 llm.chat() and llm.inference() calls
    to ensure the router schema stays in sync.
    """

    def test_sdk_chat_minimal_payload(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Exact payload from: llm.chat("Say hello")"""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Say hello"}],
                "temperature": 1.0,
                "trace_id": "6e9e04df-52a1-41e2-9c06-1de487559d27",
                "invocation_id": "44df8bbf-4a09-4264-a45a-f289a1e9e690",
                "agent_name": "test-agent",
            },
        )
        assert response.status_code == 200

    def test_sdk_chat_with_model_override_payload(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Exact payload from: llm.chat("Say hello", model="gpt-4o-mini", provider="openai")"""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Say hello"}],
                "model": "gpt-4o-mini",
                "provider": "openai",
                "temperature": 1.0,
                "trace_id": "6e9e04df-52a1-41e2-9c06-1de487559d27",
                "invocation_id": "44df8bbf-4a09-4264-a45a-f289a1e9e690",
                "agent_name": "test-agent",
            },
        )
        assert response.status_code == 200

    def test_sdk_inference_explicit_messages_payload(
        self, test_client, mock_call_provider, mock_get_api_key
    ):
        """Exact payload from: llm.inference(messages=[...])"""
        response = test_client.post(
            "/llm/inference",
            json={
                "messages": [{"role": "user", "content": "Say hello."}],
                "temperature": 1.0,
                "trace_id": "6e9e04df-52a1-41e2-9c06-1de487559d27",
                "invocation_id": "44df8bbf-4a09-4264-a45a-f289a1e9e690",
                "agent_name": "test-agent",
            },
        )
        assert response.status_code == 200
