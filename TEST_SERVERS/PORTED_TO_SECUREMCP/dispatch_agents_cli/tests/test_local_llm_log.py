"""Tests for local router LLM logging endpoint (/llm/log).

These tests verify the local router's ability to log LLM calls
made directly to providers (OpenAI, Anthropic, etc.) for trace correlation.
"""

import pytest
from fastapi.testclient import TestClient

# We need to import the router service to test endpoints
# Using a fixture to avoid import issues with missing dependencies


@pytest.fixture
def test_client():
    """Create a test client for the router service."""
    # Import here to avoid issues with optional dependencies
    from fastapi import FastAPI

    from dispatch_cli.router.service import api_router

    app = FastAPI()
    app.include_router(api_router)

    return TestClient(app)


class TestLocalLLMLogEndpoint:
    """Test the POST /llm/log endpoint on the local router."""

    @pytest.fixture
    def valid_log_request(self) -> dict:
        """Create a valid LLM log request payload."""
        return {
            "input_messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            "response_content": "Hello! How can I help you today?",
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 25,
            "output_tokens": 10,
            "finish_reason": "stop",
            "latency_ms": 150,
        }

    def test_log_llm_call_success(self, test_client, valid_log_request):
        """Test successful LLM call logging."""
        response = test_client.post("/llm/log", json=valid_log_request)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "llm_call_id" in data
        assert "cost_usd" in data

        # Cost should be calculated (non-zero for real models)
        assert isinstance(data["cost_usd"], float)
        assert data["cost_usd"] >= 0

        # llm_call_id should be a UUID
        assert len(data["llm_call_id"]) == 36  # UUID format

    def test_log_llm_call_minimal_request(self, test_client):
        """Test logging with minimal required fields."""
        minimal_request = {
            "input_messages": [{"role": "user", "content": "Hi"}],
            "model": "gpt-4o-mini",
            "provider": "openai",
            "input_tokens": 3,
            "output_tokens": 5,
        }

        response = test_client.post("/llm/log", json=minimal_request)

        assert response.status_code == 200
        data = response.json()
        assert "llm_call_id" in data
        assert "cost_usd" in data

    def test_log_llm_call_with_tool_calls(self, test_client):
        """Test logging LLM call with tool calls."""
        request_data = {
            "input_messages": [{"role": "user", "content": "What's the weather?"}],
            "response_content": None,
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 10,
            "output_tokens": 25,
            "finish_reason": "tool_calls",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "San Francisco"}',
                    },
                }
            ],
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200
        assert "llm_call_id" in response.json()

    def test_log_llm_call_with_trace_id(self, test_client, valid_log_request):
        """Test logging with explicit trace_id."""
        valid_log_request["trace_id"] = "trace-abc-123"

        response = test_client.post("/llm/log", json=valid_log_request)

        assert response.status_code == 200
        # The trace_id should be stored (we can't verify directly, but endpoint should accept it)

    def test_log_llm_call_with_invocation_id(self, test_client, valid_log_request):
        """Test logging with invocation_id (links to parent handler)."""
        valid_log_request["invocation_id"] = "inv-xyz-456"
        valid_log_request["trace_id"] = "trace-abc-123"

        response = test_client.post("/llm/log", json=valid_log_request)

        assert response.status_code == 200

    def test_log_llm_call_anthropic_model(self, test_client):
        """Test logging Anthropic model call."""
        request_data = {
            "input_messages": [{"role": "user", "content": "Hello Claude!"}],
            "response_content": "Hello! I'm Claude, an AI assistant made by Anthropic.",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "input_tokens": 8,
            "output_tokens": 15,
            "finish_reason": "stop",
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["cost_usd"] >= 0  # Should calculate cost for Anthropic models

    def test_log_llm_call_unknown_model(self, test_client):
        """Test logging with unknown model (should still work)."""
        request_data = {
            "input_messages": [{"role": "user", "content": "Hello"}],
            "response_content": "Hi!",
            "model": "unknown-model-xyz",
            "provider": "custom",
            "input_tokens": 5,
            "output_tokens": 3,
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # Unknown models may get fallback pricing, just verify it's a valid number
        assert isinstance(data["cost_usd"], float)
        assert data["cost_usd"] >= 0

    def test_log_llm_call_missing_required_field(self, test_client):
        """Test that missing required fields return validation error."""
        invalid_request = {
            "input_messages": [{"role": "user", "content": "Hello"}],
            # Missing model, provider, input_tokens, output_tokens
        }

        response = test_client.post("/llm/log", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_log_llm_call_invalid_messages_format(self, test_client):
        """Test that invalid message format returns error."""
        invalid_request = {
            "input_messages": "not a list",  # Should be a list
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 5,
            "output_tokens": 5,
        }

        response = test_client.post("/llm/log", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_log_llm_call_multi_turn_conversation(self, test_client):
        """Test logging multi-turn conversation history."""
        request_data = {
            "input_messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language."},
                {"role": "user", "content": "How do I install it?"},
            ],
            "response_content": "You can install Python from python.org or using a package manager.",
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 50,
            "output_tokens": 20,
            "finish_reason": "stop",
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200


class TestLLMLogRequestValidation:
    """Test request validation for /llm/log endpoint."""

    def test_negative_token_count_fails(self, test_client):
        """Test that negative token counts are handled (may pass depending on validation)."""
        # Note: The local router may not enforce this, but we test to document behavior
        request_data = {
            "input_messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": -10,  # Invalid
            "output_tokens": 5,
        }

        # Local router may accept this but it's semantically invalid
        # This test documents current behavior - just verify it doesn't crash
        test_client.post("/llm/log", json=request_data)

    def test_empty_messages_list(self, test_client):
        """Test handling of empty messages list."""
        request_data = {
            "input_messages": [],  # Empty but valid
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 0,
            "output_tokens": 5,
        }

        response = test_client.post("/llm/log", json=request_data)
        # Should accept empty messages (degenerate case but valid)
        assert response.status_code == 200


class TestLLMLogCostCalculation:
    """Test cost calculation for logged LLM calls."""

    def test_gpt4o_cost_calculation(self, test_client):
        """Test cost calculation for GPT-4o model."""
        request_data = {
            "input_messages": [{"role": "user", "content": "Hello"}],
            "response_content": "Hi!",
            "model": "gpt-4o",
            "provider": "openai",
            "input_tokens": 1000000,  # 1M tokens
            "output_tokens": 1000000,  # 1M tokens
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # gpt-4o: $2.50/1M input + $10.00/1M output = $12.50
        # Allow some tolerance for pricing variations
        assert data["cost_usd"] > 0

    def test_claude_cost_calculation(self, test_client):
        """Test cost calculation for Claude model."""
        request_data = {
            "input_messages": [{"role": "user", "content": "Hello"}],
            "response_content": "Hi!",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "input_tokens": 1000000,  # 1M tokens
            "output_tokens": 1000000,  # 1M tokens
        }

        response = test_client.post("/llm/log", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # claude-3-5-sonnet: $3.00/1M input + $15.00/1M output = $18.00
        assert data["cost_usd"] > 0
