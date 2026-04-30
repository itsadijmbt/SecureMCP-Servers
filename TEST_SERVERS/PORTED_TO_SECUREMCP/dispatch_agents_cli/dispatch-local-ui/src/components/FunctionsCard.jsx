import React, { useState, useEffect } from 'react';
import { Button } from '@ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { Badge } from '@ui/badge';
import { Code, Zap, Radio, Play, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';

/**
 * FunctionsCard - Displays agent functions and allows invoking @fn handlers
 *
 * Supports both:
 * - @on handlers (topic-triggered) - shown with Radio icon
 * - @fn handlers (callable) - shown with Zap icon and Invoke button
 *
 * The Invoke button dispatches a custom event to populate the SendTestEventCard
 * instead of opening its own modal.
 */
const FunctionsCard = ({ appState }) => {
  const { selectedAgent } = appState;

  const [functions, setFunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedFunction, setExpandedFunction] = useState(null);

  // Load functions from agent data
  useEffect(() => {
    if (!selectedAgent) {
      setFunctions([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    const agentFunctions = selectedAgent.functions || [];

    // Process functions into display format
    const processedFunctions = [];

    for (const func of agentFunctions) {
      // Get topic triggers (@on handlers)
      const topicTriggers = (func.triggers || []).filter(t => t.type === 'topic');
      for (const trigger of topicTriggers) {
        if (trigger.topic) {
          processedFunctions.push({
            id: `topic-${trigger.topic}-${func.name}`,
            triggerType: 'topic',
            topic: trigger.topic,
            functionName: func.name,
            name: func.name,
            description: func.description,
            inputSchema: func.input_schema,
            outputSchema: func.output_schema,
          });
        }
      }

      // Get callable triggers (@fn handlers)
      const callableTriggers = (func.triggers || []).filter(t => t.type === 'callable');
      for (const trigger of callableTriggers) {
        const fnName = trigger.function_name || func.name;
        processedFunctions.push({
          id: `callable-${fnName}`,
          triggerType: 'callable',
          topic: null,
          functionName: fnName,
          name: func.name,
          description: func.description,
          inputSchema: func.input_schema,
          outputSchema: func.output_schema,
        });
      }
    }

    setFunctions(processedFunctions);
    setLoading(false);
  }, [selectedAgent]);

  // Dispatch event to populate SendTestEventCard with this function
  const handleInvokeClick = (func) => {
    window.dispatchEvent(new CustomEvent('invokeFunction', {
      detail: {
        functionName: func.functionName,
        inputSchema: func.inputSchema,
      },
    }));
  };

  // Trigger type badge
  const getTriggerTypeBadge = (func) => {
    if (func.triggerType === 'topic') {
      return (
        <Badge className="bg-purple-50 text-purple-700 border-purple-200 flex items-center gap-1 text-xs">
          <Radio className="w-3 h-3" />
          @on
        </Badge>
      );
    } else {
      return (
        <Badge className="bg-blue-50 text-blue-700 border-blue-200 flex items-center gap-1 text-xs">
          <Zap className="w-3 h-3" />
          @fn
        </Badge>
      );
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Code className="w-4 h-4 mr-2" />
            Functions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-500">Loading functions...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (functions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Code className="w-4 h-4 mr-2" />
            Functions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <Code className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No functions registered</p>
            <p className="text-sm mt-1">This agent hasn't registered any handler functions yet.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Code className="w-4 h-4 mr-2" />
              Functions
            </div>
            <span className="text-sm font-normal text-gray-500">
              {functions.length} registered
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="pb-6">
          <div className="space-y-3">
            {functions.map((func) => (
              <div
                key={func.id}
                className="border border-gray-200 rounded-lg overflow-hidden"
              >
                {/* Function header */}
                <div
                  className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => setExpandedFunction(expandedFunction === func.id ? null : func.id)}
                >
                  <div className="flex items-center gap-2">
                    {expandedFunction === func.id ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                    <code className="text-sm font-medium text-gray-900">
                      {func.functionName || func.name}
                    </code>
                    {getTriggerTypeBadge(func)}
                  </div>

                  {/* Invoke button for callable functions - dispatches event to SendTestEventCard */}
                  {func.triggerType === 'callable' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleInvokeClick(func);
                      }}
                      className="text-xs flex items-center gap-1 text-blue-600 hover:text-blue-800 border-blue-200 hover:border-blue-400"
                    >
                      <Play className="w-3 h-3" />
                      Invoke
                    </Button>
                  )}
                </div>

                {/* Expanded content */}
                {expandedFunction === func.id && (
                  <div className="p-3 border-t border-gray-200 bg-white">
                    {/* Description */}
                    {func.description && (
                      <p className="text-sm text-gray-600 mb-3">{func.description}</p>
                    )}

                    {/* Trigger info */}
                    <div className="mb-3">
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        {func.triggerType === 'topic' ? 'Topic Trigger' : 'Function Name'}
                      </span>
                      <div className="mt-1">
                        {func.triggerType === 'topic' ? (
                          <code className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-sm">
                            {func.topic}
                          </code>
                        ) : (
                          <code className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm">
                            {func.functionName}()
                          </code>
                        )}
                      </div>
                    </div>

                    {/* Input schema */}
                    {func.inputSchema && (
                      <div>
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Input Schema
                        </span>
                        <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-auto max-h-32">
                          {JSON.stringify(func.inputSchema, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
  );
};

export default FunctionsCard;
