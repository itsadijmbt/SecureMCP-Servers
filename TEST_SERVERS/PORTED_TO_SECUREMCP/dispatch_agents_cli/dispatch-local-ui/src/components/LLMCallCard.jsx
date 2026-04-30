import React, { useState, useMemo } from 'react';
import { marked } from 'marked';
import { Badge } from '@ui/badge';
import { Bot, ChevronDown, ChevronUp, Clock, Hash, Zap, User, Wrench, Settings, MessageSquare, Code, FileText } from 'lucide-react';

// Configure marked for GFM support
marked.setOptions({
  gfm: true,
  breaks: false,
});

// Markdown content renderer with toggle
const MarkdownContent = ({ content, className = '' }) => {
  const html = useMemo(() => marked.parse(content || ''), [content]);
  return (
    <div
      className={`markdown-content max-w-none text-sm text-gray-700 ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};

// Provider color coding
function getProviderColor(provider) {
  switch (provider?.toLowerCase()) {
    case 'openai':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    case 'anthropic':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'google':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

// Finish reason badge
function getFinishReasonBadge(finishReason) {
  switch (finishReason) {
    case 'stop':
      return <Badge className="text-xs bg-green-100 text-green-800">Completed</Badge>;
    case 'tool_calls':
      return <Badge className="text-xs bg-amber-100 text-amber-800">Tool Calls</Badge>;
    case 'length':
      return <Badge className="text-xs bg-gray-100 text-gray-800">Max Length</Badge>;
    default:
      return <Badge variant="outline" className="text-xs">{finishReason || 'Unknown'}</Badge>;
  }
}

// Format cost
function formatCost(cost) {
  if (cost === undefined || cost === null) return '-';
  if (cost < 0.0001) return '<$0.0001';
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

// Format latency
function formatLatency(ms) {
  if (ms === undefined || ms === null) return '-';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

// Get role icon and styling
function getRoleConfig(role) {
  switch (role) {
    case 'system':
      return {
        icon: Settings,
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200',
        textColor: 'text-purple-800',
        iconColor: 'text-purple-600',
        label: 'System'
      };
    case 'user':
      return {
        icon: User,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        iconColor: 'text-blue-600',
        label: 'User'
      };
    case 'assistant':
      return {
        icon: Bot,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        iconColor: 'text-green-600',
        label: 'Assistant'
      };
    case 'tool':
      return {
        icon: Wrench,
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-200',
        textColor: 'text-amber-800',
        iconColor: 'text-amber-600',
        label: 'Tool Result'
      };
    default:
      return {
        icon: MessageSquare,
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        textColor: 'text-gray-800',
        iconColor: 'text-gray-600',
        label: role || 'Message'
      };
  }
}

// Individual message card component
const LLMMessageCard = ({ message, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showRaw, setShowRaw] = useState(false); // Default to markdown view
  const config = getRoleConfig(message.role);
  const Icon = config.icon;

  // Get content - handle string or object
  let content = '';
  if (typeof message.content === 'string') {
    content = message.content;
  } else if (Array.isArray(message.content)) {
    // Handle multi-part content (e.g., images + text)
    content = message.content.map(part => {
      if (typeof part === 'string') return part;
      if (part.type === 'text') return part.text;
      if (part.type === 'image_url') return '[Image]';
      return JSON.stringify(part);
    }).join('\n');
  } else if (message.content) {
    content = JSON.stringify(message.content, null, 2);
  }

  // For assistant messages with no content but with tool_calls, show the tool calls inline
  const hasToolCallsOnly = message.role === 'assistant' && !content && message.tool_calls && message.tool_calls.length > 0;

  const maxLength = 500;
  const needsTruncation = content.length > maxLength && showRaw;
  const displayContent = isExpanded || !needsTruncation
    ? content
    : content.slice(0, maxLength) + '...';

  // Check if content likely has markdown (heuristic)
  const hasMarkdownSyntax = content && (
    content.includes('```') ||
    content.includes('**') ||
    content.includes('# ') ||
    content.includes('- ') ||
    content.includes('1. ') ||
    content.includes('[') && content.includes('](')
  );

  return (
    <div className={`rounded-lg border ${config.borderColor} ${config.bgColor} p-3`}>
      <div className="flex items-start gap-2">
        <div className={`flex-shrink-0 w-6 h-6 rounded-full ${config.bgColor} flex items-center justify-center`}>
          <Icon className={`w-4 h-4 ${config.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold ${config.textColor}`}>
                {config.label}
              </span>
              {message.role === 'assistant' && message._model && (
                <span className="text-xs text-gray-400 font-mono font-normal">
                  {message._model}
                </span>
              )}
              {message.name && (
                <Badge variant="outline" className="text-xs">
                  {message.name}
                </Badge>
              )}
              {message.tool_call_id && (
                <Badge variant="outline" className="text-xs bg-amber-50">
                  ID: {message.tool_call_id.slice(0, 8)}...
                </Badge>
              )}
            </div>
            {/* Markdown/Raw toggle button */}
            {content && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowRaw(!showRaw);
                }}
                className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs transition-colors ${
                  showRaw
                    ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                }`}
                title={showRaw ? 'Switch to rendered markdown' : 'Switch to raw text'}
              >
                {showRaw ? (
                  <>
                    <FileText className="w-3 h-3" />
                    <span>Markdown</span>
                  </>
                ) : (
                  <>
                    <Code className="w-3 h-3" />
                    <span>Raw</span>
                  </>
                )}
              </button>
            )}
          </div>
          {/* Content display - either text content or inline tool calls */}
          {hasToolCallsOnly ? (
            /* Show tool calls inline when assistant message has no text content */
            <div className="space-y-2">
              {message.tool_calls.map((toolCall, idx) => {
                const functionName = toolCall.function?.name || 'unknown';
                let args = '';
                try {
                  if (typeof toolCall.function?.arguments === 'string') {
                    args = JSON.stringify(JSON.parse(toolCall.function.arguments), null, 2);
                  } else if (toolCall.function?.arguments) {
                    args = JSON.stringify(toolCall.function.arguments, null, 2);
                  }
                } catch {
                  args = toolCall.function?.arguments || '';
                }
                return (
                  <div key={idx} className="bg-amber-50 border border-amber-200 rounded p-2">
                    <div className="flex items-center gap-2 mb-1">
                      <Zap className="w-3.5 h-3.5 text-amber-600" />
                      <span className="text-xs font-semibold text-amber-800">Calling: {functionName}</span>
                      {toolCall.id && (
                        <span className="text-xs text-amber-600">ID: {toolCall.id.slice(0, 8)}...</span>
                      )}
                    </div>
                    {args && (
                      <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap break-words bg-amber-100/50 rounded p-1.5 mt-1">
                        {args}
                      </pre>
                    )}
                  </div>
                );
              })}
            </div>
          ) : showRaw ? (
            <div className="text-sm text-gray-700 whitespace-pre-wrap break-words font-mono bg-white/50 rounded p-2">
              {displayContent}
            </div>
          ) : (
            <MarkdownContent content={displayContent} />
          )}
          {needsTruncation && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-1 mt-2 text-xs text-indigo-600 hover:text-indigo-500"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  Show more
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Main LLM Call Card component
const LLMCallCard = ({ llmCall }) => {
  const [isExpanded, setIsExpanded] = useState(true); // Default expanded
  const messages = llmCall.messages || [];
  const toolCalls = llmCall.tool_calls || [];
  const totalTokens = (llmCall.input_tokens || 0) + (llmCall.output_tokens || 0);

  return (
    <div className="rounded-lg border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50 overflow-hidden">
      {/* Header */}
      <div
        className="p-3 cursor-pointer hover:bg-indigo-100/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between gap-3">
          {/* Left side: Icon + Model info */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <Bot className="w-5 h-5 text-indigo-600" />
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold text-gray-900">
                  {llmCall.model || 'Unknown Model'}
                </span>
                {llmCall.provider && (
                  <Badge className={`text-xs border ${getProviderColor(llmCall.provider)}`}>
                    {llmCall.provider}
                  </Badge>
                )}
                {getFinishReasonBadge(llmCall.finish_reason)}
                {llmCall.logged_externally && (
                  <Badge className="text-xs bg-gray-100 text-gray-600">
                    Logged Externally
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Right side: Cost + Expand */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-900">
              {formatCost(llmCall.cost_usd)}
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </div>
        </div>

        {/* Metrics row */}
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            <span>{formatLatency(llmCall.latency_ms)}</span>
          </div>

          <div className="flex items-center gap-1">
            <Hash className="w-3.5 h-3.5" />
            <span>{totalTokens.toLocaleString()} tokens</span>
            <span className="text-gray-400">
              ({llmCall.input_tokens?.toLocaleString() || 0} in / {llmCall.output_tokens?.toLocaleString() || 0} out)
            </span>
          </div>

          {toolCalls.length > 0 && (
            <div className="flex items-center gap-1 text-amber-600">
              <Zap className="w-3.5 h-3.5" />
              <span>{toolCalls.length} tool call{toolCalls.length !== 1 ? 's' : ''}</span>
            </div>
          )}

          {messages.length > 0 && (
            <div className="flex items-center gap-1 text-gray-500">
              <MessageSquare className="w-3.5 h-3.5" />
              <span>{messages.length} message{messages.length !== 1 ? 's' : ''}</span>
            </div>
          )}
        </div>
      </div>

      {/* Expanded content: Messages + Tool Calls */}
      {isExpanded && (
        <div className="border-t border-indigo-100 bg-white/50 p-3 space-y-2">
          {/* Messages */}
          {messages.map((message, index) => (
            <LLMMessageCard key={index} message={message} index={index} />
          ))}

          {/* Response content (if separate from messages) */}
          {llmCall.response_content && !messages.some(m => m.role === 'assistant' && m.content === llmCall.response_content) && (
            <LLMMessageCard
              message={{ role: 'assistant', content: llmCall.response_content }}
              index={messages.length}
            />
          )}
        </div>
      )}
    </div>
  );
};

// Export LLMMessageCard for use in unified trace view
export { LLMMessageCard };
export default LLMCallCard;
