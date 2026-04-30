import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { ChevronDown, ChevronRight, Github, Search, ExternalLink } from 'lucide-react';
import githubEventsSchema from '../data/github-events.json';

/**
 * GitHubEventsReference - Documentation component for GitHub webhook events
 *
 * Displays all supported GitHub events from the auto-generated schema,
 * grouped by event type with links to Python type docs.
 */
const GitHubEventsReference = () => {
  const [expandedTypes, setExpandedTypes] = useState(new Set());
  const [searchQuery, setSearchQuery] = useState('');

  const { events, event_types, total } = githubEventsSchema;

  // Filter events based on search query
  const filteredEventTypes = useMemo(() => {
    if (!searchQuery.trim()) {
      return event_types;
    }

    const query = searchQuery.toLowerCase();
    return event_types.filter(eventType => {
      if (eventType.toLowerCase().includes(query)) {
        return true;
      }
      const eventList = events[eventType] || [];
      return eventList.some(event =>
        event.action?.toLowerCase().includes(query) ||
        event.class.toLowerCase().includes(query) ||
        event.topic.toLowerCase().includes(query)
      );
    });
  }, [searchQuery, event_types, events]);

  const toggleEventType = (eventType) => {
    setExpandedTypes(prev => {
      const next = new Set(prev);
      if (next.has(eventType)) {
        next.delete(eventType);
      } else {
        next.add(eventType);
      }
      return next;
    });
  };

  const formatEventTypeName = (name) => {
    return name.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <Github className="w-5 h-5 mr-2" />
            GitHub Events Reference
          </div>
          <span className="text-sm font-normal text-gray-500">
            {total} events
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Search */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Event Types List */}
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {filteredEventTypes.map(eventType => {
            const eventList = events[eventType] || [];
            const isExpanded = expandedTypes.has(eventType);

            return (
              <div key={eventType} className="border border-gray-200 rounded-lg">
                {/* Event Type Header */}
                <button
                  onClick={() => toggleEventType(eventType)}
                  className="w-full px-4 py-2 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 mr-2 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 mr-2 text-gray-500" />
                    )}
                    <span className="font-medium text-gray-900">
                      {formatEventTypeName(eventType)}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      ({eventList.length})
                    </span>
                  </div>
                  <a
                    href={`https://docs.github.com/en/webhooks/webhook-events-and-payloads#${eventType}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-gray-400 hover:text-blue-600"
                    title="View GitHub docs"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </button>

                {/* Actions List */}
                {isExpanded && (
                  <div className="border-t border-gray-200 bg-gray-50 px-4 py-2">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-xs text-gray-500 uppercase">
                          <th className="pb-1">Action</th>
                          <th className="pb-1">Class</th>
                          <th className="pb-1">Topic</th>
                        </tr>
                      </thead>
                      <tbody>
                        {eventList.map(event => (
                          <tr key={event.topic} className="border-t border-gray-100">
                            <td className="py-1">
                              <code className="text-purple-700 font-mono text-xs">
                                {event.action || '(default)'}
                              </code>
                            </td>
                            <td className="py-1">
                              <code className="text-blue-700 font-mono text-xs">
                                {event.class}
                              </code>
                            </td>
                            <td className="py-1">
                              <code className="text-gray-600 font-mono text-xs">
                                {event.topic}
                              </code>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}

          {filteredEventTypes.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No events match "{searchQuery}"
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default GitHubEventsReference;
