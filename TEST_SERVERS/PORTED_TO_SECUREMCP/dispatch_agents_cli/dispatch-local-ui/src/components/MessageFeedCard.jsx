import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { Badge } from '@ui/badge';
import { MessageCircle, RefreshCw, Trash2, ChevronDown, ChevronUp, Bot } from 'lucide-react';
import LLMCallCard, { LLMMessageCard } from './LLMCallCard';

const MessageFeedCard = ({ appState }) => {
  const { selectedAgent } = appState;

  const [messages, setMessages] = useState([]);
  const [llmCalls, setLlmCalls] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTraceId, setActiveTraceId] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const [expandedMessages, setExpandedMessages] = useState(new Set());
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages or LLM calls arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, llmCalls]);

  // Load recent messages for the selected agent (disabled in new architecture)
  const loadRecentMessages = async () => {
    // In the new architecture with synthetic messages,
    // we don't want to load/replace messages from API
    // Messages are created immediately when events are sent
    return;
  };

  // Flatten tree structure into a sorted list for display
  const flattenEventTree = (events, result = []) => {
    for (const event of events) {
      // Add event to flat list (without children array to avoid circular refs)
      const { children, ...eventWithoutChildren } = event;
      result.push(eventWithoutChildren);

      // Recursively add children
      if (children && children.length > 0) {
        flattenEventTree(children, result);
      }
    }
    return result;
  };

  // Poll for messages in a specific trace
  const pollTraceMessages = async (traceId) => {
    if (!traceId) return;

    try {
      // Use trace endpoint which returns production-compatible format
      // Events are in a tree structure with LLM calls merged in
      const response = await fetch(`/api/unstable/events/trace/${traceId}`);
      if (response.ok) {
        const data = await response.json();
        // New format: events is a tree, LLM calls are merged in with message_type: "llm_call"
        // Old format fallback: events array + separate llm_calls array
        let traceEvents = data.events || data.messages || [];

        // Flatten tree structure if events have children
        if (traceEvents.some(e => e.children && e.children.length > 0)) {
          traceEvents = flattenEventTree(traceEvents);
        }

        // Sort by effective_timestamp or timestamp
        traceEvents.sort((a, b) => {
          const timeA = a.effective_timestamp || a.timestamp || a.ts || '';
          const timeB = b.effective_timestamp || b.timestamp || b.ts || '';
          return timeA.localeCompare(timeB);
        });

        // Separate LLM calls from other events
        const llmCallEvents = traceEvents.filter(e => e.message_type === 'llm_call');
        const nonLlmEvents = traceEvents.filter(e => e.message_type !== 'llm_call');

        // Also handle legacy format with separate llm_calls array
        const legacyLlmCalls = data.llm_calls || [];

        if (nonLlmEvents.length > 0) {
          setMessages(prevMessages => {
            const existingByUid = new Map(prevMessages.map(m => [m.uid, m]));
            const existingMessageKeys = new Set(prevMessages.map(m =>
              `${m.trace_id || ''}-${m.topic || m.function_name}-${m.sender_id}-${JSON.stringify(m.payload)}`
            ));

            // Separate into updates (existing UID with changed status) and truly new messages
            const updatedUids = new Set();
            const newMessages = [];

            for (const m of nonLlmEvents) {
              const existing = existingByUid.get(m.uid);
              if (existing) {
                // Check if invocation status changed (e.g. running → completed)
                if (existing.invocation_status !== m.invocation_status) {
                  updatedUids.add(m.uid);
                  existingByUid.set(m.uid, m); // Replace with updated version
                }
              } else {
                const messageKey = `${m.trace_id || ''}-${m.topic || m.function_name}-${m.sender_id}-${JSON.stringify(m.payload)}`;
                if (!existingMessageKeys.has(messageKey)) {
                  newMessages.push(m);
                }
              }
            }

            // Check for completion across both new and updated messages
            const allChangedMessages = [
              ...newMessages,
              ...[...updatedUids].map(uid => existingByUid.get(uid)),
            ];
            const hasCompletedInvocations = allChangedMessages.some(msg =>
              msg && (
                (msg.topic && msg.topic.includes('.response')) ||
                msg.invocation_status === 'completed' ||
                msg.invocation_status === 'error'
              )
            );

            if (hasCompletedInvocations) {
              stopPolling();
            }

            if (updatedUids.size > 0 || newMessages.length > 0) {
              // Rebuild: replace updated messages in-place, append new ones
              const rebuilt = prevMessages.map(m =>
                updatedUids.has(m.uid) ? existingByUid.get(m.uid) : m
              );
              return [...rebuilt, ...newMessages];
            }
            return prevMessages;
          });
        }

        // Update LLM calls (from both new merged format and legacy format)
        const allLlmCalls = [
          ...llmCallEvents.map(e => ({
            ...e,
            llm_call_id: e.uid,
            messages: e.request_messages,
            tool_calls: e.response_tool_calls,
          })),
          ...legacyLlmCalls
        ];

        if (allLlmCalls.length > 0) {
          setLlmCalls(prevLlmCalls => {
            const existingIds = new Set(prevLlmCalls.map(c => c.llm_call_id || c.uid));
            const newCalls = allLlmCalls.filter(c => !existingIds.has(c.llm_call_id || c.uid));
            if (newCalls.length > 0) {
              return [...prevLlmCalls, ...newCalls];
            }
            return prevLlmCalls;
          });
        }
      }
    } catch (error) {
      console.error('Error polling trace messages:', error);
    }
  };

  // Start polling for a trace
  const startTracePolling = (traceId, timeoutSeconds = 3600) => {
    // Clear existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    setActiveTraceId(traceId);

    // Poll immediately first
    pollTraceMessages(traceId);

    // Then poll every 2 seconds
    const interval = setInterval(() => {
      pollTraceMessages(traceId);
    }, 2000);

    setPollingInterval(interval);

    // Stop polling after 2x the timeout to avoid race conditions with backend
    const pollingTimeoutMs = timeoutSeconds * 2 * 1000;
    setTimeout(() => {
      if (interval) {
        clearInterval(interval);
        setPollingInterval(null);
        setActiveTraceId(null);
      }
    }, pollingTimeoutMs);
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
      setActiveTraceId(null);
    }
  };

  // Clear messages and LLM calls
  const clearMessages = () => {
    setMessages([]);
    setLlmCalls([]);
    stopPolling();
  };

  // Clean up polling when agent changes
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [selectedAgent]);

  // Listen for trace events from SendTestEventCard
  useEffect(() => {
    const handleTraceEvent = (event) => {
      // Handle immediate messages if provided
      if (event.detail.immediateMessages && event.detail.immediateMessages.length > 0) {
        const immediateMessages = event.detail.immediateMessages;

        setMessages(prevMessages => {
          const existingUids = new Set(prevMessages.map(m => m.uid));
          const newMessages = immediateMessages.filter(m => !existingUids.has(m.uid));

          if (newMessages.length > 0) {
            return [...prevMessages, ...newMessages];
          }
          return prevMessages;
        });

        // Check if we have agent responses in immediate messages
        const hasAgentResponses = immediateMessages.some(msg =>
          msg.topic && msg.topic.includes('.response')
        );

        // If we have immediate agent responses, no need to poll
        if (hasAgentResponses) {
          return; // Don't start polling
        }
      }

      // Start polling for any additional messages if requested (only if no immediate agent responses)
      if (event.detail.startPolling && event.detail.traceId) {
        startTracePolling(event.detail.traceId, event.detail.timeoutSeconds);
      }
    };

    window.addEventListener('traceStarted', handleTraceEvent);
    return () => {
      window.removeEventListener('traceStarted', handleTraceEvent);
    };
  }, []);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Toggle message expansion
  const toggleMessageExpansion = (messageUid) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageUid)) {
        newSet.delete(messageUid);
      } else {
        newSet.add(messageUid);
      }
      return newSet;
    });
  };

  const formatMessageContent = (message, isExpanded = false) => {
    let content;
    if (typeof message.payload === 'string') {
      content = message.payload;
    } else {
      content = JSON.stringify(message.payload, null, 2);
    }

    // Define length threshold for truncation
    const maxLength = 300;
    const needsTruncation = content.length > maxLength;

    if (isExpanded || !needsTruncation) {
      return { content, needsTruncation };
    }

    return {
      content: content.slice(0, maxLength) + '...',
      needsTruncation
    };
  };

  // Group messages and LLM calls by trace_id into unified traces
  const traceGroups = React.useMemo(() => {
    const groups = new Map();

    // Add messages grouped by trace_id
    messages.forEach(msg => {
      const traceId = msg.trace_id || 'no-trace';
      if (!groups.has(traceId)) {
        groups.set(traceId, {
          traceId,
          invocation: null,
          llmCalls: [],
          timestamp: msg.ts || msg.stored_at || '',
        });
      }
      const group = groups.get(traceId);
      // The first function message is usually the invocation
      if (!group.invocation && (msg.message_type === 'function' || msg.function_name)) {
        group.invocation = msg;
      }
      // Update timestamp if earlier
      const msgTime = msg.ts || msg.stored_at || '';
      if (msgTime && (!group.timestamp || msgTime < group.timestamp)) {
        group.timestamp = msgTime;
      }
    });

    // Add LLM calls to their trace groups
    llmCalls.forEach(call => {
      const traceId = call.trace_id || 'no-trace';
      if (!groups.has(traceId)) {
        groups.set(traceId, {
          traceId,
          invocation: null,
          llmCalls: [],
          timestamp: call.ts || '',
        });
      }
      groups.get(traceId).llmCalls.push(call);
    });

    // Sort LLM calls within each group by timestamp
    groups.forEach(group => {
      group.llmCalls.sort((a, b) => {
        const timeA = a.ts || '';
        const timeB = b.ts || '';
        return timeA.localeCompare(timeB);
      });
    });

    // Convert to array and sort by timestamp (newest first for display)
    const sortedGroups = Array.from(groups.values());
    sortedGroups.sort((a, b) => {
      const timeA = a.timestamp || '';
      const timeB = b.timestamp || '';
      return timeA.localeCompare(timeB);
    });

    return sortedGroups;
  }, [messages, llmCalls]);

  const hasContent = messages.length > 0 || llmCalls.length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            Message Feed
            {activeTraceId && (
              <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-800">
                Live
              </Badge>
            )}
            {llmCalls.length > 0 && (
              <Badge variant="secondary" className="ml-2 bg-indigo-100 text-indigo-800">
                <Bot className="w-3 h-3 mr-1" />
                {llmCalls.length} LLM call{llmCalls.length !== 1 ? 's' : ''}
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearMessages}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-6">

      <div className="bg-white rounded-md border h-[600px] overflow-y-auto">
        {isLoading && !hasContent ? (
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500 mx-auto mb-2"></div>
            Loading messages...
          </div>
        ) : !hasContent ? (
          <div className="p-4 text-center text-gray-500">
            <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No messages yet</p>
            <p className="text-xs mt-1">Send a test event to see messages appear here</p>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {traceGroups.map((group, groupIndex) => {
              const invocation = group.invocation;
              const llmCallsList = group.llmCalls;

              // Calculate total stats across all LLM calls in this trace
              const totalCost = llmCallsList.reduce((sum, c) => sum + (c.cost_usd || 0), 0);
              const totalInputTokens = llmCallsList.reduce((sum, c) => sum + (c.input_tokens || 0), 0);
              const totalOutputTokens = llmCallsList.reduce((sum, c) => sum + (c.output_tokens || 0), 0);
              const totalLatency = llmCallsList.reduce((sum, c) => sum + (c.latency_ms || 0), 0);

              // Build unified conversation from LLM calls, grouped by subprocess_id.
              // Calls from different subprocesses (orchestrator vs subagent) get separate
              // conversation threads to avoid flickering between different message contexts.
              const conversationMessages = [];

              if (llmCallsList.length > 0) {
                // Group LLM calls by subprocess_id
                const subprocessGroups = new Map();
                llmCallsList.forEach(call => {
                  const spId = call.subprocess_id || '_default';
                  if (!subprocessGroups.has(spId)) {
                    subprocessGroups.set(spId, []);
                  }
                  subprocessGroups.get(spId).push(call);
                });

                // Use the largest subprocess group as the primary conversation
                // (usually the orchestrator has the most calls)
                let primaryCalls = llmCallsList;
                if (subprocessGroups.size > 1) {
                  let maxSize = 0;
                  subprocessGroups.forEach((calls) => {
                    if (calls.length > maxSize) {
                      maxSize = calls.length;
                      primaryCalls = calls;
                    }
                  });
                }

                const lastCall = primaryCalls[primaryCalls.length - 1];
                const lastCallMessages = lastCall.messages || [];

                // Add all messages, annotating assistant messages with the model
                lastCallMessages.forEach(msg => {
                  if (msg.role === 'assistant') {
                    // Find which call produced this response by matching content
                    const matchingCall = primaryCalls.find(c =>
                      c.response_content && msg.content &&
                      typeof msg.content === 'string' &&
                      c.response_content === msg.content
                    );
                    conversationMessages.push({
                      ...msg,
                      _model: matchingCall?.model || primaryCalls[0]?.model,
                    });
                  } else {
                    conversationMessages.push({ ...msg });
                  }
                });

                // Add the final response from the last LLM call
                if (lastCall.response_content && lastCall.response_content !== '[streamed]') {
                  conversationMessages.push({
                    role: 'assistant',
                    content: lastCall.response_content,
                    _model: lastCall.model,
                  });
                } else if (lastCall.tool_calls && lastCall.tool_calls.length > 0) {
                  conversationMessages.push({
                    role: 'assistant',
                    content: null,
                    tool_calls: lastCall.tool_calls,
                    _model: lastCall.model,
                  });
                }
              }

              return (
                <div key={`trace-${group.traceId}-${groupIndex}`} className="rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm">
                  {/* Trace Header */}
                  <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {invocation && (
                          <>
                            <span className="text-sm text-gray-600">
                              {invocation.sender_id || 'unknown'}
                            </span>
                            <span className="text-gray-400">→</span>
                            <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                              {invocation.function_name || invocation.target_agent || 'unknown'}
                            </Badge>
                          </>
                        )}
                        {invocation?.invocation_status === 'completed' && (
                          <Badge className="bg-green-100 text-green-800 text-xs">Completed</Badge>
                        )}
                        {invocation?.invocation_status === 'error' && (
                          <Badge className="bg-red-100 text-red-800 text-xs">Error</Badge>
                        )}
                        {invocation?.invocation_status === 'running' && (
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">Running</Badge>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(group.timestamp)}
                      </span>
                    </div>

                    {/* Stats row */}
                    {llmCallsList.length > 0 && (
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-600">
                        <span className="flex items-center gap-1">
                          <Bot className="w-3.5 h-3.5" />
                          {llmCallsList.length} LLM call{llmCallsList.length !== 1 ? 's' : ''}
                        </span>
                        {(() => {
                          const models = [...new Set(llmCallsList.map(c => c.model).filter(Boolean))];
                          return models.length > 0 ? (
                            <span className="font-medium text-gray-700">{models.join(', ')}</span>
                          ) : null;
                        })()}
                        <span>{(totalInputTokens + totalOutputTokens).toLocaleString()} tokens</span>
                        <span>{totalCost < 0.0001 ? '<$0.0001' : `$${totalCost.toFixed(4)}`}</span>
                        <span>{totalLatency}ms</span>
                      </div>
                    )}
                  </div>

                  {/* Trace Content */}
                  <div className="p-4 space-y-3">
                    {/* Input Payload */}
                    {invocation && invocation.payload && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="text-xs font-semibold text-blue-800 mb-1">Input</div>
                        <pre className="text-xs font-mono text-blue-900 whitespace-pre-wrap break-words">
                          {JSON.stringify(invocation.payload, null, 2)}
                        </pre>
                      </div>
                    )}

                    {/* LLM Conversation Timeline */}
                    {conversationMessages.length > 0 && (
                      <div className="space-y-2">
                        {conversationMessages.map((msg, idx) => (
                          <LLMMessageCard key={`msg-${idx}`} message={msg} index={idx} />
                        ))}
                      </div>
                    )}

                    {/* Invocation Result */}
                    {invocation?.invocation_status === 'completed' && invocation?.invocation_result && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="text-xs font-semibold text-green-800 mb-1">
                          Response from {invocation.target_agent || 'agent'}
                        </div>
                        <pre className="text-xs font-mono text-green-900 whitespace-pre-wrap break-words">
                          {JSON.stringify(invocation.invocation_result, null, 2)}
                        </pre>
                      </div>
                    )}

                    {/* Invocation Error */}
                    {invocation?.invocation_status === 'error' && invocation?.invocation_error && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div className="text-xs font-semibold text-red-800 mb-1">
                          Error from {invocation.target_agent || 'agent'}
                        </div>
                        <pre className="text-xs font-mono text-red-900 whitespace-pre-wrap break-words">
                          {invocation.invocation_error}
                        </pre>
                      </div>
                    )}

                    {/* Trace ID */}
                    {group.traceId && group.traceId !== 'no-trace' && (
                      <div className="text-xs text-gray-400">
                        Trace: {group.traceId.substring(0, 8)}...
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
        {activeTraceId && (
          <div className="mt-2 text-center">
            <div className="flex items-center justify-center text-xs text-gray-500">
              <div className="animate-pulse w-1.5 h-1.5 bg-blue-400 rounded-full mr-1.5"></div>
              Listening for messages...
            </div>
          </div>
        )}
      </div>
      </CardContent>
    </Card>
  );
};

export default MessageFeedCard;
