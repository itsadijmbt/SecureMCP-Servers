# Manual End-to-End Test Plan for Operator MCP Server

## Objective
Test the complete operator MCP workflow by manually executing each tool in sequence to validate the entire agent lifecycle.

## Prerequisites
- Backend running at http://localhost:8000
- MCP operator server configured in .mcp.json as dispatch-operator-localhost

## Test Workflow Commands

### 1. Create Agent
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name create_agent \
  --tool-arg 'request={"parent_directory": "examples", "agent_name": "test-workflow-agent", "description": "End-to-end test agent", "namespace": "examples"}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "success": true,
    "agent_directory": "examples/test-workflow-agent",
    "message": "Successfully created agent 'test-workflow-agent'"
  }
}
```

**Verification:**
```bash
ls -la examples/test-workflow-agent/
cat examples/test-workflow-agent/.dispatch.yaml
```

### 2. Deploy Agent
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name deploy_agent \
  --tool-arg 'request={"agent_directory": "examples/test-workflow-agent"}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "agent_name": "test-workflow-agent",
    "status": "deployed",
    "message": "...deployment output..."
  }
}
```

### 3. Get Topic Schema
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name get_topic_schema \
  --tool-arg 'request={"topic": "test-workflow-agent.hello_world", "namespace": "examples"}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "topic": "test-workflow-agent.hello_world",
    "canonical_schema": {...},
    "handlers": [...]
  }
}
```

### 4. Publish Event
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name publish_event \
  --tool-arg 'request={"topic": "test-workflow-agent.hello_world", "payload": {"text": "test-workflow"}, "namespace": "examples"}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "message": "Event published successfully",
    "event_uid": "..."
  }
}
```

### 5. Get Agent Logs
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name get_agent_logs \
  --tool-arg 'request={"agent_name": "test-workflow-agent", "namespace": "examples", "limit": 20}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "events": [
      {
        "timestamp": ...,
        "message": "...",
        "ingestion_time": null
      }
    ]
  }
}
```

**Look for:** Evidence that the event with subject "test-workflow" was processed by the agent.

### 6. Uninstall Agent
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli \
  --method tools/call \
  --tool-name uninstall_agent \
  --tool-arg 'request={"agent_name": "test-workflow-agent", "namespace": "examples"}'
```

**Expected Output:**
```json
{
  "structuredContent": {
    "success": true,
    "message": "..."
  }
}
```

**Verification:**
```bash
# Verify agent is gone from backend
curl -H "Authorization: Bearer test-token" \
  http://localhost:8000/api/unstable/namespace/examples/agents/test-workflow-agent
# Should return 404
```

### 7. Cleanup
```bash
rm -rf examples/test-workflow-agent
```
