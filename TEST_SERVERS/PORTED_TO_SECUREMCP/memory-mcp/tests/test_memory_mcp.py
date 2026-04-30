import pytest
import asyncio
from fastmcp import Client
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import atexit


# Global variable to store test results
test_results = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
}


def log_test_result(test_name: str, status: str, details: dict = None, error: str = None):
    """Log test result to global results dictionary."""
    result = {
        "test_name": test_name,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
        "error": error
    }
    test_results["tests"].append(result)
    test_results["summary"]["total"] += 1
    
    if status == "PASSED":
        test_results["summary"]["passed"] += 1
    elif status == "FAILED":
        test_results["summary"]["failed"] += 1
        if error:
            test_results["summary"]["errors"].append(f"{test_name}: {error}")


def write_results_to_file():
    """Write test results to file."""
    try:
        # Create results directory if it doesn't exist
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"mcp_test_results_{timestamp}.json"
        
        # Write detailed results
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        # Write summary report
        summary_filename = results_dir / f"mcp_test_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("MCP SERVER TEST RESULTS SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test Run Time: {test_results['timestamp']}\n")
            f.write(f"Total Tests: {test_results['summary']['total']}\n")
            f.write(f"Passed: {test_results['summary']['passed']}\n")
            f.write(f"Failed: {test_results['summary']['failed']}\n")
            f.write(f"Success Rate: {(test_results['summary']['passed'] / max(test_results['summary']['total'], 1)) * 100:.1f}%\n")
            f.write("\n")
            
            if test_results['summary']['errors']:
                f.write("ERRORS:\n")
                f.write("-" * 20 + "\n")
                for error in test_results['summary']['errors']:
                    f.write(f"• {error}\n")
                f.write("\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for test in test_results['tests']:
                status_icon = "✅" if test['status'] == "PASSED" else "❌"
                f.write(f"{status_icon} {test['test_name']} - {test['status']}\n")
                if test['details']:
                    for key, value in test['details'].items():
                        f.write(f"   {key}: {value}\n")
                if test['error']:
                    f.write(f"   Error: {test['error']}\n")
                f.write("\n")
        
        print(f"\n📊 Test results written to:")
        print(f"   Detailed: {filename}")
        print(f"   Summary: {summary_filename}")
        return filename, summary_filename
        
    except Exception as e:
        print(f"❌ Failed to write test results: {e}")
        return None, None


# Register the function to run at exit
atexit.register(write_results_to_file)


@pytest.fixture
def test_config():
    """Test configuration data."""
    return {
        "user_id": "test.user@example.com",
        "conversation_id": "test_conversation_001",
        "query": "F1 Street Circuit Driving Experience at Marina Bay Sands",
        "mongodb_config": {
            "connection_string": os.getenv("MONGODB_URI"),
            "database_name": "maap_data_loader", 
            "collection_name": "documents",
            "fulltext_search_field": "text",
            "vector_search_index_name": "documents_vector_search_index",
            "vector_search_field": "embedding",
            "weight": 0.5,
            "limit": 5
        }
    }


@pytest.fixture
async def mcp_client():
    """Create MCP client for testing."""
    async with Client("http://localhost:8080/mcp") as client:
        yield client


async def extract_tool_response(result):
    """Extract text content from tool response and parse as JSON if possible."""
    response_data = {}
    for content in result.content:
        if hasattr(content, "text"):
            response_data = content.text
            break
    
    if isinstance(response_data, str):
        try:
            response_data = json.loads(response_data)
        except json.JSONDecodeError:
            pass
    
    return response_data


@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """Test listing available tools."""
    try:
        tools = await mcp_client.list_tools()
        assert len(tools) > 0
        tool_names = [tool.name for tool in tools]
        assert "store_memory" in tool_names
        assert "retrieve_memory" in tool_names
        assert "hybrid_search" in tool_names
        
        log_test_result(
            "test_list_tools", 
            "PASSED", 
            {"tools_count": len(tools), "tool_names": tool_names}
        )
    except Exception as e:
        log_test_result("test_list_tools", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_store_memory(mcp_client, test_config):
    """Test storing memory."""
    try:
        result = await mcp_client.call_tool("store_memory", {
            "conversation_id": test_config["conversation_id"],
            "text": "I'm interested in F1 racing at Marina Bay Sands.",
            "message_type": "human",
            "user_id": test_config["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        response = await extract_tool_response(result)
        assert response is not None
        
        log_test_result(
            "test_store_memory", 
            "PASSED", 
            {"response_type": type(response).__name__}
        )
    except Exception as e:
        log_test_result("test_store_memory", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_retrieve_memory(mcp_client, test_config):
    """Test retrieving memory."""
    try:
        # First store a memory
        await mcp_client.call_tool("store_memory", {
            "conversation_id": test_config["conversation_id"],
            "text": "I love F1 racing experiences",
            "message_type": "human",
            "user_id": test_config["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Then retrieve it
        result = await mcp_client.call_tool("retrieve_memory", {
            "user_id": test_config["user_id"],
            "text": "Tell me about F1 racing"
        })
        
        response = await extract_tool_response(result)
        assert response is not None
        assert isinstance(response, dict)
        
        log_test_result(
            "test_retrieve_memory", 
            "PASSED", 
            {
                "has_related_conversation": "related_conversation" in response,
                "has_conversation_summary": "conversation_summary" in response,
                "has_similar_memories": "similar_memories" in response
            }
        )
    except Exception as e:
        log_test_result("test_retrieve_memory", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_semantic_cache_store_and_check(mcp_client, test_config):
    """Test storing and checking semantic cache."""
    try:
        ai_response = "Marina Bay F1 circuit is amazing with night racing and city views."
        
        # Store cache
        store_result = await mcp_client.call_tool("semantic_cache_response", {
            "user_id": test_config["user_id"],
            "query": test_config["query"],
            "response": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        store_response = await extract_tool_response(store_result)
        assert store_response is not None
        
        # Check cache
        check_result = await mcp_client.call_tool("check_semantic_cache", {
            "user_id": test_config["user_id"],
            "query": "F1 Street Driving Experience at Marina Bay"
        })
        
        check_response = await extract_tool_response(check_result)
        assert check_response is not None
        
        log_test_result(
            "test_semantic_cache_store_and_check", 
            "PASSED", 
            {
                "store_success": store_response is not None,
                "check_success": check_response is not None
            }
        )
    except Exception as e:
        log_test_result("test_semantic_cache_store_and_check", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_hybrid_search(mcp_client, test_config):
    """Test hybrid search functionality."""
    try:
        result = await mcp_client.call_tool("hybrid_search", {
            **test_config["mongodb_config"],
            "query": test_config["query"],
            "user_id": test_config["user_id"]
        })
        
        response = await extract_tool_response(result)
        assert response is not None
        assert isinstance(response, dict)
        
        results_count = 0
        if "results" in response:
            assert isinstance(response["results"], list)
            results_count = len(response["results"])
        
        log_test_result(
            "test_hybrid_search", 
            "PASSED", 
            {
                "results_count": results_count,
                "has_results_key": "results" in response
            }
        )
    except Exception as e:
        log_test_result("test_hybrid_search", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_web_search(mcp_client, test_config):
    """Test web search functionality."""
    try:
        result = await mcp_client.call_tool("search_web", {
            "query": test_config["query"]
        })
        
        response = await extract_tool_response(result)
        assert response is not None
        
        response_type = type(response).__name__
        results_count = 0
        if isinstance(response, list):
            results_count = len(response)
        elif isinstance(response, dict) and "results" in response:
            results_count = len(response["results"])
        
        log_test_result(
            "test_web_search", 
            "PASSED", 
            {
                "response_type": response_type,
                "results_count": results_count
            }
        )
    except Exception as e:
        log_test_result("test_web_search", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_hybrid_search_with_different_weights(mcp_client, test_config):
    """Test hybrid search with different weight settings."""
    try:
        # Test keyword-focused search
        keyword_result = await mcp_client.call_tool("hybrid_search", {
            **test_config["mongodb_config"],
            "query": test_config["query"],
            "user_id": test_config["user_id"],
            "weight": 0.2
        })
        
        keyword_response = await extract_tool_response(keyword_result)
        assert keyword_response is not None
        
        # Test semantic-focused search
        semantic_result = await mcp_client.call_tool("hybrid_search", {
            **test_config["mongodb_config"],
            "query": test_config["query"],
            "user_id": test_config["user_id"],
            "weight": 0.8
        })
        
        semantic_response = await extract_tool_response(semantic_result)
        assert semantic_response is not None
        
        keyword_count = len(keyword_response.get("results", []))
        semantic_count = len(semantic_response.get("results", []))
        
        log_test_result(
            "test_hybrid_search_with_different_weights", 
            "PASSED", 
            {
                "keyword_results_count": keyword_count,
                "semantic_results_count": semantic_count,
                "weight_difference_test": True
            }
        )
    except Exception as e:
        log_test_result("test_hybrid_search_with_different_weights", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_error_handling_invalid_user_id(mcp_client, test_config):
    """Test error handling with invalid user_id."""
    try:
        with pytest.raises(Exception) as exc_info:
            await mcp_client.call_tool("store_memory", {
                "conversation_id": test_config["conversation_id"],
                "text": "This should fail",
                "message_type": "human",
                "user_id": None
            })
        
        log_test_result(
            "test_error_handling_invalid_user_id", 
            "PASSED", 
            {
                "expected_error": True,
                "error_type": type(exc_info.value).__name__
            }
        )
    except AssertionError as e:
        log_test_result("test_error_handling_invalid_user_id", "FAILED", error=str(e))
        raise
    except Exception as e:
        log_test_result("test_error_handling_invalid_user_id", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_error_handling_invalid_message_type(mcp_client, test_config):
    """Test error handling with invalid message type."""
    try:
        with pytest.raises(Exception) as exc_info:
            await mcp_client.call_tool("store_memory", {
                "conversation_id": test_config["conversation_id"],
                "text": "This should fail",
                "message_type": "invalid_type",  # Invalid message type
                "user_id": test_config["user_id"]
            })
        
        log_test_result(
            "test_error_handling_invalid_message_type", 
            "PASSED", 
            {
                "expected_error": True,
                "error_type": type(exc_info.value).__name__,
                "invalid_message_type": "invalid_type"
            }
        )
    except AssertionError as e:
        log_test_result("test_error_handling_invalid_message_type", "FAILED", error=str(e))
        raise
    except Exception as e:
        log_test_result("test_error_handling_invalid_message_type", "FAILED", error=str(e))
        raise


@pytest.mark.asyncio
async def test_concurrent_operations(mcp_client, test_config):
    """Test concurrent tool operations."""
    try:
        import time
        start_time = time.time()
        
        tasks = [
            mcp_client.call_tool("retrieve_memory", {
                "user_id": test_config["user_id"],
                "text": "F1 racing"
            }),
            mcp_client.call_tool("check_semantic_cache", {
                "user_id": test_config["user_id"],
                "query": "Racing experience"
            }),
            mcp_client.call_tool("hybrid_search", {
                **test_config["mongodb_config"],
                "query": "Marina Bay",
                "user_id": test_config["user_id"],
                "limit": 3
            })
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful > 0
        
        # Check that results are properly formatted
        for result in results:
            if not isinstance(result, Exception):
                response = await extract_tool_response(result)
                assert response is not None
        
        log_test_result(
            "test_concurrent_operations", 
            "PASSED", 
            {
                "successful_calls": successful,
                "total_calls": len(tasks),
                "elapsed_time": f"{elapsed_time:.2f}s",
                "concurrent_success": True
            }
        )
    except Exception as e:
        log_test_result("test_concurrent_operations", "FAILED", error=str(e))
        raise


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished, right before returning the exit status to the system."""
    write_results_to_file()


def pytest_configure(config):
    """Called after command line options have been parsed."""
    print("🚀 Starting MCP Server Test Suite with File Logging")


def pytest_unconfigure(config):
    """Called before test process is exited."""
    write_results_to_file()


if __name__ == "__main__":
    # Ensure results are written even if run directly
    try:
        exit_code = pytest.main([__file__, "-v", "-s"])
        write_results_to_file()  # Explicit call
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        write_results_to_file()
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        write_results_to_file()
    finally:
        # Force write results
        if test_results["tests"]:
            write_results_to_file()