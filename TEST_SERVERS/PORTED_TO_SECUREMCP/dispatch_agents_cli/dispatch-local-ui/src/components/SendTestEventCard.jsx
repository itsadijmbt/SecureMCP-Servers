import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { Send, Sparkles, Zap, Radio, Loader2, CheckCircle2, XCircle, Copy, Clock } from 'lucide-react';

const SendTestEventCard = ({ appState }) => {
  const { topics, selectedAgent, isTopicDetailsPage, isAgentDetailsPage } = appState;

  // Invocation type: 'function' or 'topic'
  const [invocationType, setInvocationType] = useState('function');

  const [eventForm, setEventForm] = useState({
    topic: '',
    functionName: '',
    payload: '{\n  "message": "Hello from UI!"\n}',
    sender_id: 'ui-test',
    timeout_seconds: 3600, // Default 1 hour (matches backend default)
  });
  const [jsonError, setJsonError] = useState(null);
  const [sendingEvent, setSendingEvent] = useState(false);
  const [eventResponse, setEventResponse] = useState(null);
  const [currentTraceId, setCurrentTraceId] = useState(null);
  const [isLoadingSchema, setIsLoadingSchema] = useState(false);
  const [schemaError, setSchemaError] = useState(null);
  const [isAgentReady, setIsAgentReady] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Track which topic we've already loaded schema for to prevent redundant fetches
  const lastLoadedSchemaTopicRef = useRef(null);

  // Function invocation state (similar to FunctionsCard modal)
  const [invocationState, setInvocationState] = useState({
    status: 'idle', // idle | pending | running | completed | error
    invocationId: null,
    traceId: null,
    result: null,
    error: null,
  });

  // Filter topics based on selected agent's capabilities
  const getAgentTopics = () => {
    if (!selectedAgent) {
      return [];
    }

    // Use agent.topics array directly (simpler and more reliable)
    if (selectedAgent.topics && Array.isArray(selectedAgent.topics)) {
      console.log(`Agent ${selectedAgent.name} subscribes to topics:`, selectedAgent.topics);
      const filteredTopics = topics.filter(topic => {
        const topicName = typeof topic === 'string' ? topic : (topic?.topic || topic?.name || topic);
        return selectedAgent.topics.includes(topicName);
      });
      console.log(`Filtered topics for agent:`, filteredTopics);
      return filteredTopics;
    }

    // Fallback: try to extract from functions (legacy support)
    if (selectedAgent.functions && Array.isArray(selectedAgent.functions)) {
      const agentTopics = selectedAgent.functions
        .flatMap(func => func.triggers || [])
        .filter(trigger => trigger.type === 'topic' && trigger.topic)
        .map(trigger => trigger.topic);

      return topics.filter(topic => {
        const topicName = typeof topic === 'string' ? topic : (topic?.topic || topic?.name || topic);
        return agentTopics.includes(topicName);
      });
    }

    // If no topic information available, return empty array instead of all topics
    return [];
  };

  // Get callable @fn functions from agent
  const getAgentFunctions = () => {
    if (!selectedAgent || !selectedAgent.functions) {
      return [];
    }

    const callableFunctions = [];
    for (const func of selectedAgent.functions) {
      const callableTriggers = (func.triggers || []).filter(t => t.type === 'callable');
      for (const trigger of callableTriggers) {
        callableFunctions.push({
          functionName: trigger.function_name || func.name,
          name: func.name,
          description: func.description,
          inputSchema: func.input_schema,
          outputSchema: func.output_schema,
        });
      }
    }
    return callableFunctions;
  };

  // Check if agent has topics
  const hasTopics = () => {
    return getAgentTopics().length > 0;
  };

  // Check if agent has callable functions
  const hasFunctions = () => {
    return getAgentFunctions().length > 0;
  };

  // Auto-select first function or topic when agent is selected
  useEffect(() => {
    // On Topic Details page, everything is immediately ready
    if (isTopicDetailsPage) {
      setIsAgentReady(true);
      setInvocationType('topic'); // Force topic mode on topic details page
      return;
    }

    // On Agent Details page, force function mode only
    if (isAgentDetailsPage && selectedAgent) {
      setIsAgentReady(true);
      setInvocationType('function'); // Force function mode on agent details page

      const functions = getAgentFunctions();
      if (functions.length > 0 && !eventForm.functionName) {
        handleFunctionChange(functions[0].functionName);
      }
      return;
    }

    // Regular logic for other pages
    if (selectedAgent) {
      // Agent data is already available from subscription - no delay needed
      setIsAgentReady(true);

      // Auto-select based on what's available
      const functions = getAgentFunctions();
      const agentTopics = getAgentTopics();

      if (functions.length > 0) {
        // Default to function mode and select first function
        setInvocationType('function');
        if (!eventForm.functionName) {
          handleFunctionChange(functions[0].functionName);
        }
      } else if (agentTopics.length > 0) {
        // Fall back to topic mode
        setInvocationType('topic');
        const firstTopic = typeof agentTopics[0] === 'string' ? agentTopics[0] : agentTopics[0].topic;
        if (firstTopic !== eventForm.topic) {
          handleTopicChange(firstTopic);
        }
      }
    } else {
      setIsAgentReady(false);
    }
  }, [selectedAgent, isTopicDetailsPage, isAgentDetailsPage]);

  // Listen for invokeFunction events from FunctionsCard
  useEffect(() => {
    const handleInvokeFunction = (event) => {
      const { functionName, inputSchema } = event.detail;
      setInvocationType('function');
      handleFunctionChange(functionName, inputSchema);
      // Reset invocation state when switching functions
      setInvocationState({
        status: 'idle',
        invocationId: null,
        traceId: null,
        result: null,
        error: null,
      });
    };

    window.addEventListener('invokeFunction', handleInvokeFunction);
    return () => window.removeEventListener('invokeFunction', handleInvokeFunction);
  }, [selectedAgent]);

  // Auto-populate schema when selectedAgent or topic changes (only when agent is ready)
  useEffect(() => {
    if (eventForm.topic && ((selectedAgent && isAgentReady) || isTopicDetailsPage)) {
      populateWithSchemaExample(eventForm.topic);
    }
  }, [selectedAgent, eventForm.topic, isAgentReady, isTopicDetailsPage]);

  // Initialize form - different behavior for Topic Details vs Agent Details pages
  // This effect only runs once when the page loads, not on every topics array update
  useEffect(() => {
    // On Topic Details page, immediately set the topic from the topics array
    if (isTopicDetailsPage && topics.length > 0 && topics[0]) {
      const topicName = typeof topics[0] === 'string' ? topics[0] : (topics[0].topic || topics[0].name || topics[0]);
      if (topicName && topicName !== eventForm.topic) {
        setEventForm(prev => ({
          ...prev,
          topic: topicName
        }));
        // Also immediately load schema since we know the topic
        populateWithSchemaExample(topicName);
      }
    }
    // Regular agent details page behavior
    else if (!isTopicDetailsPage && topics.length > 0 && topics[0] && !eventForm.topic && !selectedAgent) {
      const topicName = typeof topics[0] === 'string' ? topics[0] : (topics[0].topic || topics[0].name || 'test');
      setEventForm(prev => ({
        ...prev,
        topic: topicName
      }));
    }
  }, [topics, isTopicDetailsPage]);

  // Initialize icons when component updates

  // Validate JSON payload
  const validateJson = (jsonString) => {
    try {
      JSON.parse(jsonString);
      setJsonError(null);
      return true;
    } catch (error) {
      setJsonError('Invalid JSON: ' + error.message);
      return false;
    }
  };

  // Handle form input changes
  const handleFormChange = (field, value) => {
    setEventForm(prev => ({
      ...prev,
      [field]: value
    }));

    if (field === 'payload') {
      validateJson(value);
    }
  };

  // Auto-populate form with schema example
  const populateWithSchemaExample = async (topicName, forceRefresh = false) => {
    if (!topicName) {
      return;
    }

    // Skip if we've already loaded schema for this topic (unless forced)
    if (!forceRefresh && lastLoadedSchemaTopicRef.current === topicName) {
      return;
    }

    setIsLoadingSchema(true);
    setSchemaError(null);
    lastLoadedSchemaTopicRef.current = topicName;

    try {
      // First try the topics endpoint that works with the local router
      const topicSchemasResponse = await fetch('/api/unstable/schemas/topics');
      if (topicSchemasResponse.ok) {
        const topicSchemasData = await topicSchemasResponse.json();
        const topicSchemas = topicSchemasData.topics || {};

        // Find schemas for this topic
        const schemas = topicSchemas[topicName] || [];

        if (schemas.length > 0) {
          // Try to generate example from first schema
          const schema = schemas[0];
          if (schema.schema && schema.schema.input_schema) {
            try {
              const examplePayload = generateExampleFromSchema(schema.schema.input_schema);
              handleFormChange('payload', JSON.stringify(examplePayload, null, 2));
              setSchemaError(null);
              return;
            } catch (error) {
              setSchemaError('Could not generate example from schema');
            }
          }
        }
      }

      // Fallback: try the individual schema endpoint
      const response = await fetch(`/api/unstable/schemas/${encodeURIComponent(topicName)}`);
      if (response.ok) {
        const schemaInfo = await response.json();

        if (schemaInfo.canonical_schema) {
          const schema = schemaInfo.canonical_schema.input_schema;
          const examplePayload = generateExampleFromSchema(schema);
          handleFormChange('payload', JSON.stringify(examplePayload, null, 2));
          setSchemaError(null);
        } else {
          setSchemaError('No schema available for this topic');
        }
      } else {
        // Schema not available yet - show helpful message
        setSchemaError('Schema not yet available. Agent may still be registering.');
      }
    } catch (error) {
      setSchemaError('Could not load schema. Please try again in a moment.');
    } finally {
      setIsLoadingSchema(false);
    }
  };

  // Simple schema example generator
  const generateExampleFromSchema = (schema) => {
    if (!schema || typeof schema !== 'object') {
      return { message: 'Hello from UI!' };
    }

    const generateFromProperties = (properties) => {
      const result = {};
      for (const [key, prop] of Object.entries(properties)) {
        if (prop.type === 'string') {
          result[key] = prop.example || `example_${key}`;
        } else if (prop.type === 'number' || prop.type === 'integer') {
          result[key] = prop.example || 42;
        } else if (prop.type === 'boolean') {
          result[key] = prop.example !== undefined ? prop.example : true;
        } else if (prop.type === 'array') {
          result[key] = [prop.items ? generateFromProperties({ item: prop.items }).item : 'item'];
        } else if (prop.type === 'object' && prop.properties) {
          result[key] = generateFromProperties(prop.properties);
        } else {
          result[key] = prop.example || `example_${key}`;
        }
      }
      return result;
    };

    if (schema.properties) {
      return generateFromProperties(schema.properties);
    } else if (schema.example) {
      return schema.example;
    }

    return { message: 'Hello from UI!' };
  };

  // Handle topic change
  const handleTopicChange = (newTopic) => {
    handleFormChange('topic', newTopic);
    // Auto-populate with schema example when topic changes
    if (newTopic && selectedAgent) {
      populateWithSchemaExample(newTopic);
    }
  };

  // Handle function change
  const handleFunctionChange = (newFunctionName, inputSchema = null) => {
    handleFormChange('functionName', newFunctionName);

    // Find function schema if not provided
    if (!inputSchema) {
      const functions = getAgentFunctions();
      const func = functions.find(f => f.functionName === newFunctionName);
      inputSchema = func?.inputSchema;
    }

    // Auto-populate payload from function schema
    if (inputSchema) {
      try {
        const example = generateExampleFromSchema(inputSchema);
        handleFormChange('payload', JSON.stringify(example, null, 2));
        setSchemaError(null);
      } catch (e) {
        // Fall back to default payload
        handleFormChange('payload', '{}');
      }
    } else {
      handleFormChange('payload', '{}');
    }
  };

  // Poll for function invocation result
  const pollForResult = useCallback(async (invocationId, timeoutSeconds) => {
    // Use 2x the timeout to avoid race conditions with backend timeout
    const maxAttempts = (timeoutSeconds || 3600) * 2;
    let attempts = 0;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setInvocationState(prev => ({
          ...prev,
          status: 'error',
          error: `Invocation timed out after ${Math.round(maxAttempts / 60)} minutes`,
        }));
        setSendingEvent(false);
        return;
      }

      try {
        const response = await fetch(`/api/unstable/invoke/${invocationId}`);
        if (!response.ok) {
          throw new Error('Failed to get invocation status');
        }

        const data = await response.json();

        if (data.status === 'completed') {
          setInvocationState(prev => ({
            ...prev,
            status: 'completed',
            result: data.result,
            traceId: data.trace_id,
          }));
          setSendingEvent(false);

          // Dispatch trace event for MessageFeed to poll for enriched events
          if (data.trace_id) {
            window.dispatchEvent(new CustomEvent('traceStarted', {
              detail: {
                traceId: data.trace_id,
                startPolling: true,
                timeoutSeconds: eventForm.timeout_seconds,
              },
            }));
          }
          return;
        }

        if (data.status === 'error') {
          setInvocationState(prev => ({
            ...prev,
            status: 'error',
            error: data.error || 'Unknown error',
            traceId: data.trace_id,
          }));
          setSendingEvent(false);
          return;
        }

        // Still pending or running
        setInvocationState(prev => ({
          ...prev,
          status: data.status,
          traceId: data.trace_id,
        }));

        attempts++;
        setTimeout(poll, 1000);
      } catch (err) {
        setInvocationState(prev => ({
          ...prev,
          status: 'error',
          error: err.message || 'Failed to get invocation status',
        }));
        setSendingEvent(false);
      }
    };

    poll();
  }, []);

  // Invoke function
  const invokeFunction = async () => {
    if (!validateJson(eventForm.payload) || !selectedAgent || !eventForm.functionName) {
      return;
    }

    setSendingEvent(true);
    setEventResponse(null);
    setInvocationState({
      status: 'pending',
      invocationId: null,
      traceId: null,
      result: null,
      error: null,
    });

    try {
      const response = await fetch('/api/unstable/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: selectedAgent.name,
          function_name: eventForm.functionName,
          payload: JSON.parse(eventForm.payload),
          timeout_seconds: eventForm.timeout_seconds,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to invoke function');
      }

      const data = await response.json();
      setInvocationState(prev => ({
        ...prev,
        invocationId: data.invocation_id,
        traceId: data.trace_id,
        status: 'running',
      }));

      // Start MessageFeed polling immediately so LLM calls appear in real-time
      if (data.trace_id) {
        window.dispatchEvent(new CustomEvent('traceStarted', {
          detail: {
            traceId: data.trace_id,
            startPolling: true,
            timeoutSeconds: eventForm.timeout_seconds,
          },
        }));
      }

      // Start polling for result
      pollForResult(data.invocation_id, eventForm.timeout_seconds);
    } catch (err) {
      setInvocationState({
        status: 'error',
        invocationId: null,
        traceId: null,
        result: null,
        error: err.message,
      });
      setSendingEvent(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Poll for topic publish invocation results (same pattern as function invoke)
  const pollForTopicResults = useCallback(async (invocationIds, traceId, timeoutSeconds) => {
    // Use 2x the timeout to avoid race conditions with backend timeout
    const maxAttempts = (timeoutSeconds || 3600) * 2;
    let attempts = 0;
    const pendingInvocations = new Set(invocationIds);

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setInvocationState(prev => ({
          ...prev,
          status: 'error',
          error: `Invocation timed out after ${Math.round(maxAttempts / 60)} minutes`,
        }));
        setSendingEvent(false);
        return;
      }

      try {
        // Poll each pending invocation
        const results = await Promise.all(
          [...pendingInvocations].map(async (invId) => {
            const response = await fetch(`/api/unstable/invoke/${invId}`);
            if (!response.ok) {
              throw new Error('Failed to get invocation status');
            }
            return response.json();
          })
        );

        // Check which invocations are done
        let allCompleted = true;
        let anyError = false;
        let lastError = null;
        const completedResults = [];

        for (const data of results) {
          if (data.status === 'completed') {
            pendingInvocations.delete(data.invocation_id);
            completedResults.push(data);
          } else if (data.status === 'error') {
            pendingInvocations.delete(data.invocation_id);
            anyError = true;
            lastError = data.error;
          } else {
            allCompleted = false;
          }
        }

        // All done or all have resolved
        if (pendingInvocations.size === 0) {
          if (anyError) {
            setInvocationState(prev => ({
              ...prev,
              status: 'error',
              error: lastError || 'One or more handlers failed',
              traceId: traceId,
            }));
          } else {
            // Combine all results
            const combinedResult = completedResults.length === 1
              ? completedResults[0].result
              : completedResults.map(r => ({ agent: r.agent_name, result: r.result }));

            setInvocationState(prev => ({
              ...prev,
              status: 'completed',
              result: combinedResult,
              traceId: traceId,
            }));
          }
          setSendingEvent(false);

          // Dispatch trace event for MessageFeed to poll for enriched events
          window.dispatchEvent(new CustomEvent('traceStarted', {
            detail: {
              traceId: traceId,
              startPolling: true,
              timeoutSeconds: eventForm.timeout_seconds,
            },
          }));
          return;
        }

        // Still pending - update state and continue polling
        setInvocationState(prev => ({
          ...prev,
          status: 'running',
          traceId: traceId,
        }));

        attempts++;
        setTimeout(poll, 1000);
      } catch (err) {
        setInvocationState(prev => ({
          ...prev,
          status: 'error',
          error: err.message || 'Failed to get invocation status',
        }));
        setSendingEvent(false);
      }
    };

    poll();
  }, []);

  // Send event function (for topics) - now uses invocation-based pattern
  const sendEvent = async () => {
    if (!validateJson(eventForm.payload)) {
      return;
    }

    setSendingEvent(true);
    setEventResponse(null);
    setCurrentTraceId(null);
    setInvocationState({
      status: 'pending',
      invocationId: null,
      traceId: null,
      result: null,
      error: null,
    });

    try {
      // Use /events/publish which returns invocation_ids (like /invoke)
      const response = await fetch('/api/unstable/events/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: eventForm.topic,
          payload: JSON.parse(eventForm.payload),
          sender_id: eventForm.sender_id
        })
      });

      const result = await response.json();

      if (response.ok) {
        // Store trace info for display
        setCurrentTraceId(result.event_uid);

        // If no handlers, show message
        if (result.handler_count === 0) {
          setInvocationState({
            status: 'completed',
            invocationId: null,
            traceId: null,
            result: { message: 'No handlers subscribed to this topic' },
            error: null,
          });
          setSendingEvent(false);
          return;
        }

        // Update state with invocation IDs
        setInvocationState(prev => ({
          ...prev,
          status: 'running',
          invocationId: result.invocation_ids.join(', '),
        }));

        // Poll for results (like function invocation)
        // First, we need to extract trace_id - fetch it from first invocation
        const firstInvocationResponse = await fetch(`/api/unstable/invoke/${result.invocation_ids[0]}`);
        if (firstInvocationResponse.ok) {
          const firstInvData = await firstInvocationResponse.json();
          pollForTopicResults(result.invocation_ids, firstInvData.trace_id, eventForm.timeout_seconds);
        } else {
          // Fallback: poll without trace_id
          pollForTopicResults(result.invocation_ids, result.event_uid, eventForm.timeout_seconds);
        }
      } else {
        setInvocationState({
          status: 'error',
          invocationId: null,
          traceId: null,
          result: null,
          error: result.detail || 'Failed to publish event',
        });
        setSendingEvent(false);
      }
    } catch (error) {
      console.error('Error sending event:', error);
      setInvocationState({
        status: 'error',
        invocationId: null,
        traceId: null,
        result: null,
        error: 'Network error: ' + error.message,
      });
      setSendingEvent(false);
    }
  };

  const isInvoking = invocationState.status === 'pending' || invocationState.status === 'running';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Send className="w-4 h-4 mr-2" />
          Test Agent
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-6">

      <div className="space-y-4">
        {/* Invocation Type Toggle - Hidden on Topic Details page and Agent Details page (agent details is function-only) */}
        {!isTopicDetailsPage && !isAgentDetailsPage && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Invocation Type
            </label>
            <div className="flex rounded-lg border border-gray-300 overflow-hidden">
              <button
                type="button"
                onClick={() => {
                  setInvocationType('function');
                  setInvocationState({ status: 'idle', invocationId: null, traceId: null, result: null, error: null });
                  // Auto-select first function
                  const functions = getAgentFunctions();
                  if (functions.length > 0 && !eventForm.functionName) {
                    handleFunctionChange(functions[0].functionName);
                  }
                }}
                disabled={!hasFunctions() || !isAgentReady}
                className={`flex-1 px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                  invocationType === 'function'
                    ? 'bg-blue-50 text-blue-700 border-r border-blue-200'
                    : 'bg-white text-gray-600 hover:bg-gray-50 border-r border-gray-300'
                } ${(!hasFunctions() || !isAgentReady) ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Zap className="w-4 h-4" />
                Function Call
              </button>
              <button
                type="button"
                onClick={() => {
                  setInvocationType('topic');
                  setInvocationState({ status: 'idle', invocationId: null, traceId: null, result: null, error: null });
                  // Auto-select first topic
                  const agentTopics = getAgentTopics();
                  if (agentTopics.length > 0 && !eventForm.topic) {
                    const firstTopic = typeof agentTopics[0] === 'string' ? agentTopics[0] : agentTopics[0].topic;
                    handleTopicChange(firstTopic);
                  }
                }}
                disabled={!hasTopics() || !isAgentReady}
                className={`flex-1 px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                  invocationType === 'topic'
                    ? 'bg-purple-50 text-purple-700'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                } ${(!hasTopics() || !isAgentReady) ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Radio className="w-4 h-4" />
                Topic Event
              </button>
            </div>
            {selectedAgent && !isAgentReady && (
              <div className="flex items-center text-xs text-amber-600 mt-2">
                <div className="animate-spin rounded-full h-3 w-3 border-b border-amber-600 mr-1"></div>
                Loading agent capabilities...
              </div>
            )}
            {isAgentReady && !hasFunctions() && !hasTopics() && (
              <p className="text-xs text-amber-600 mt-2">
                No handlers registered. Wait for agent to subscribe.
              </p>
            )}
          </div>
        )}

        {/* Function Selection - Only shown for function invocation type */}
        {!isTopicDetailsPage && invocationType === 'function' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Function
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              value={eventForm.functionName}
              onChange={(e) => handleFunctionChange(e.target.value)}
              disabled={!isAgentReady || isInvoking}
            >
              <option value="">Select a function</option>
              {getAgentFunctions().map((func, index) => (
                <option key={func.functionName || index} value={func.functionName}>
                  {func.functionName}()
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Topic Selection - Only shown for topic invocation type (not on Topic Details page) */}
        {!isTopicDetailsPage && invocationType === 'topic' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              value={eventForm.topic}
              onChange={(e) => handleTopicChange(e.target.value)}
              disabled={!isAgentReady || sendingEvent}
            >
              <option value="">Select a topic</option>
              {getAgentTopics().map((topicData, index) => {
                const topicName = typeof topicData === 'string' ? topicData : topicData?.topic || 'unknown';
                return (
                  <option key={topicName || index} value={topicName}>
                    {topicName}
                  </option>
                );
              })}
            </select>
          </div>
        )}

        {/* Topic Display for Topic Details page */}
        {isTopicDetailsPage && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic
            </label>
            <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
              {eventForm.topic || 'No topic selected'}
            </div>
          </div>
        )}

        {/* JSON Payload */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">
              JSON Payload
            </label>
            {(eventForm.topic || eventForm.functionName) && (
              <button
                type="button"
                onClick={() => {
                  if (invocationType === 'function' && eventForm.functionName) {
                    handleFunctionChange(eventForm.functionName);
                  } else if (eventForm.topic) {
                    populateWithSchemaExample(eventForm.topic, true); // Force refresh on manual click
                  }
                }}
                disabled={isLoadingSchema || isInvoking}
                className="text-xs text-indigo-600 hover:text-indigo-500 disabled:text-gray-400 flex items-center"
              >
                {isLoadingSchema ? (
                  <>
                    <div className="animate-spin rounded-full h-3 w-3 border-b border-indigo-600 mr-1"></div>
                    Loading...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3 h-3 inline mr-1" />
                    Auto-populate
                  </>
                )}
              </button>
            )}
          </div>
          <textarea
            className={`w-full px-3 py-2 border rounded-md shadow-sm font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
              jsonError ? 'border-red-500' : 'border-gray-300'
            } ${isInvoking ? 'bg-gray-100' : ''}`}
            rows="6"
            value={eventForm.payload}
            onChange={(e) => handleFormChange('payload', e.target.value)}
            placeholder='{\n  "message": "Hello from UI!"\n}'
            disabled={isInvoking}
          />
          {jsonError && (
            <p className="text-red-500 text-sm mt-1">{jsonError}</p>
          )}
          {schemaError && (
            <p className="text-amber-600 text-sm mt-1">{schemaError}</p>
          )}
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <span>Advanced Options</span>
            <svg
              className={`ml-1 h-4 w-4 transform transition-transform ${
                showAdvanced ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="mt-3 pt-3 border-t border-gray-200 space-y-4">
              {/* Timeout (only for function invocations) */}
              {invocationType === 'function' && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      Timeout
                    </label>
                    <span className="text-xs text-gray-500">
                      {eventForm.timeout_seconds >= 3600
                        ? `${(eventForm.timeout_seconds / 3600).toFixed(1)} hour(s)`
                        : `${Math.round(eventForm.timeout_seconds / 60)} minute(s)`}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      className="w-28 px-3 py-2 border border-gray-300 rounded-md shadow-sm font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={eventForm.timeout_seconds}
                      onChange={(e) => {
                        const val = parseInt(e.target.value, 10);
                        if (!isNaN(val) && val >= 1 && val <= 86400) {
                          handleFormChange('timeout_seconds', val);
                        }
                      }}
                      min={1}
                      max={86400}
                      disabled={isInvoking}
                    />
                    <span className="text-sm text-gray-600">seconds</span>
                    <div className="flex gap-1 ml-auto">
                      <button
                        type="button"
                        onClick={() => handleFormChange('timeout_seconds', 60)}
                        disabled={isInvoking}
                        className={`px-2 py-1 text-xs border rounded transition-colors ${
                          eventForm.timeout_seconds === 60
                            ? 'bg-blue-50 border-blue-300 text-blue-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        } ${isInvoking ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        1m
                      </button>
                      <button
                        type="button"
                        onClick={() => handleFormChange('timeout_seconds', 300)}
                        disabled={isInvoking}
                        className={`px-2 py-1 text-xs border rounded transition-colors ${
                          eventForm.timeout_seconds === 300
                            ? 'bg-blue-50 border-blue-300 text-blue-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        } ${isInvoking ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        5m
                      </button>
                      <button
                        type="button"
                        onClick={() => handleFormChange('timeout_seconds', 3600)}
                        disabled={isInvoking}
                        className={`px-2 py-1 text-xs border rounded transition-colors ${
                          eventForm.timeout_seconds === 3600
                            ? 'bg-blue-50 border-blue-300 text-blue-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        } ${isInvoking ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        1h
                      </button>
                      <button
                        type="button"
                        onClick={() => handleFormChange('timeout_seconds', 86400)}
                        disabled={isInvoking}
                        className={`px-2 py-1 text-xs border rounded transition-colors ${
                          eventForm.timeout_seconds === 86400
                            ? 'bg-blue-50 border-blue-300 text-blue-700'
                            : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                        } ${isInvoking ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        24h
                      </button>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Maximum execution time for this invocation (1 second to 24 hours)
                  </p>
                </div>
              )}

              {/* Sender ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sender ID
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  value={eventForm.sender_id}
                  onChange={(e) => handleFormChange('sender_id', e.target.value)}
                  placeholder="ui-test"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Identifier for the sender of this test event
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Send/Invoke Button */}
        <div>
          {invocationType === 'function' && !isTopicDetailsPage ? (
            <Button
              onClick={invokeFunction}
              disabled={sendingEvent || jsonError || !eventForm.functionName || !selectedAgent}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {sendingEvent ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Invoking...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Invoke Function
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={sendEvent}
              disabled={sendingEvent || jsonError || !eventForm.topic}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              {sendingEvent ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Radio className="w-4 h-4 mr-2" />
                  Send Topic Event
                </>
              )}
            </Button>
          )}
        </div>

        {/* Function Invocation Result */}
        {invocationType === 'function' && invocationState.status !== 'idle' && (
          <div className={`rounded-lg p-4 space-y-3 ${
            invocationState.status === 'completed' ? 'bg-green-50 border border-green-200' :
            invocationState.status === 'error' ? 'bg-red-50 border border-red-200' :
            'bg-gray-50 border border-gray-200'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Invocation Status</span>
              {invocationState.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  Completed
                </span>
              )}
              {invocationState.status === 'error' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  <XCircle className="w-3 h-3 mr-1" />
                  Error
                </span>
              )}
              {(invocationState.status === 'pending' || invocationState.status === 'running') && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                  {invocationState.status === 'pending' ? 'Starting...' : 'Running...'}
                </span>
              )}
            </div>

            {invocationState.invocationId && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">Invocation ID:</span>
                <code className="px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono">
                  {invocationState.invocationId}
                </code>
                <button
                  onClick={() => copyToClipboard(invocationState.invocationId)}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Copy to clipboard"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
            )}

            {invocationState.traceId && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">Trace ID:</span>
                <code className="px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono">
                  {invocationState.traceId}
                </code>
                <button
                  onClick={() => copyToClipboard(invocationState.traceId)}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Copy to clipboard"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
            )}

            {/* Result display */}
            {invocationState.status === 'completed' && invocationState.result && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-green-800">Result</span>
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(invocationState.result, null, 2))}
                    className="text-xs text-gray-600 hover:text-gray-800 flex items-center"
                  >
                    <Copy className="w-3 h-3 mr-1" />
                    Copy
                  </button>
                </div>
                <pre className="text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-gray-800">
                  {JSON.stringify(invocationState.result, null, 2)}
                </pre>
              </div>
            )}

            {/* Error display */}
            {invocationState.status === 'error' && invocationState.error && (
              <div className="mt-3">
                <span className="text-sm font-medium text-red-800">Error</span>
                <pre className="text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-red-700 mt-1">
                  {invocationState.error}
                </pre>
              </div>
            )}

            {/* Running indicator */}
            {isInvoking && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Waiting for function to complete...</span>
              </div>
            )}
          </div>
        )}

        {/* Topic Event Invocation Result (same UI as function invocations) */}
        {invocationType === 'topic' && invocationState.status !== 'idle' && (
          <div className={`rounded-lg p-4 space-y-3 ${
            invocationState.status === 'completed' ? 'bg-green-50 border border-green-200' :
            invocationState.status === 'error' ? 'bg-red-50 border border-red-200' :
            'bg-gray-50 border border-gray-200'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Publish Status</span>
              {invocationState.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  Completed
                </span>
              )}
              {invocationState.status === 'error' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  <XCircle className="w-3 h-3 mr-1" />
                  Error
                </span>
              )}
              {(invocationState.status === 'pending' || invocationState.status === 'running') && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                  {invocationState.status === 'pending' ? 'Publishing...' : 'Running handlers...'}
                </span>
              )}
            </div>

            {invocationState.invocationId && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">Invocation ID(s):</span>
                <code className="px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono text-xs">
                  {invocationState.invocationId.length > 40
                    ? invocationState.invocationId.substring(0, 40) + '...'
                    : invocationState.invocationId}
                </code>
              </div>
            )}

            {invocationState.traceId && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">Trace ID:</span>
                <code className="px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono">
                  {invocationState.traceId}
                </code>
                <button
                  onClick={() => copyToClipboard(invocationState.traceId)}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Copy to clipboard"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
            )}

            {/* Result display */}
            {invocationState.status === 'completed' && invocationState.result && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-green-800">Result</span>
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(invocationState.result, null, 2))}
                    className="text-xs text-gray-600 hover:text-gray-800 flex items-center"
                  >
                    <Copy className="w-3 h-3 mr-1" />
                    Copy
                  </button>
                </div>
                <pre className="text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-gray-800">
                  {JSON.stringify(invocationState.result, null, 2)}
                </pre>
              </div>
            )}

            {/* Error display */}
            {invocationState.status === 'error' && invocationState.error && (
              <div className="mt-3">
                <span className="text-sm font-medium text-red-800">Error</span>
                <pre className="text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-red-700 mt-1">
                  {invocationState.error}
                </pre>
              </div>
            )}

            {/* Running indicator */}
            {(invocationState.status === 'pending' || invocationState.status === 'running') && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Waiting for handlers to complete...</span>
              </div>
            )}
          </div>
        )}
      </div>
      </CardContent>
    </Card>
  );
};

export default SendTestEventCard;