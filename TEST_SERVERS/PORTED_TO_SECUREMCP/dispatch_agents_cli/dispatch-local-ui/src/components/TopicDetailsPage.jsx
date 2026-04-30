import React, { useState, useEffect } from 'react';
import { Button } from '@ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { Radio, Waypoints } from 'lucide-react';
import SendTestEventCard from './SendTestEventCard';
import MessageFeedCard from './MessageFeedCard';

const TopicDetailsPage = ({ appState }) => {
  const {
    selectedTopic,
    agents,
    showTopicsList,
    showAgentDetails
  } = appState;


  if (!selectedTopic) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No topic selected</p>
        <Button
          onClick={showTopicsList}
          variant="outline"
          className="mt-4"
        >
          Back to Topics
        </Button>
      </div>
    );
  }

  // Get the topic name properly
  const topicName = typeof selectedTopic === 'string' ? selectedTopic : selectedTopic?.name;

  // Get agents that subscribe to this topic
  // Use the real data structure from the router
  const subscribingAgents = agents.filter(agent => {
    if (!agent.topics || !Array.isArray(agent.topics)) return false;
    return agent.topics.includes(topicName);
  });

  // Create a mock selected agent for the event cards to work properly
  // This allows us to reuse the existing SendTestEventCard and MessageFeedCard
  const mockSelectedAgent = {
    name: topicName,
    // Create mock functions structure for compatibility with SendTestEventCard
    functions: [{
      name: 'topic_handler',
      triggers: [{
        type: 'topic',
        topic: topicName
      }]
    }]
  };

  // Enhanced app state for the cards - configured specifically for Topic Details
  const topicAppState = {
    ...appState,
    selectedAgent: mockSelectedAgent,
    topics: [topicName], // Single topic for this page
    isTopicDetailsPage: true // Flag to indicate this is Topic Details page
  };

  return (
    <div className="space-y-6">
      {/* Topic Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Radio className="h-8 w-8 text-[var(--color-brand-blue-600)]" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{topicName}</h1>
            <div className="flex items-center mt-2 space-x-4">
              <span className="text-sm text-gray-500">{subscribingAgents.length} subscribing agents</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column Layout: Main Content + Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Main Column (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Send Test Event Card */}
          <SendTestEventCard appState={topicAppState} />

          {/* Message Feed Card */}
          <MessageFeedCard appState={topicAppState} />
        </div>

        {/* Sidebar Column (1/3 width) */}
        <div className="space-y-6">

          {/* Subscribing Agents Card */}
          <Card className="border-0 shadow-sm bg-gray-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-semibold text-gray-900">
                Subscribing Agents ({subscribingAgents.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0 pb-6">
              {subscribingAgents.length === 0 ? (
                <div className="text-center py-4">
                  <Waypoints className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">No agents subscribe to this topic</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {subscribingAgents.map((agent, index) => {
                    // Show topics this agent subscribes to
                    const relevantTopics = agent.topics || [];

                    return (
                      <div key={agent.name || index} className="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                           onClick={() => showAgentDetails(agent)}>
                        <div className="flex items-center mb-2">
                          <Waypoints className="w-4 h-4 text-[var(--color-brand-blue-500)] mr-2" />
                          <span className="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors">{agent.name}</span>
                          <span className="ml-auto text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            {agent.status || 'unknown'}
                          </span>
                        </div>
                        {relevantTopics.length > 0 && (
                          <div className="ml-6">
                            <p className="text-xs text-gray-500 mb-1">Subscribed topics:</p>
                            {relevantTopics.map((topic, topicIndex) => (
                              <div key={topicIndex} className="text-xs text-gray-600">
                                • {topic}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Topic Details Card */}
          <Card className="border-0 shadow-sm bg-gray-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-semibold text-gray-900">Topic Details</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 pb-6">
              <div className="grid grid-cols-1 gap-4">
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Name</span>
                  <span className="text-sm text-gray-900 font-medium">{topicName}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Subscribers</span>
                  <span className="text-sm text-gray-900">{subscribingAgents.length} agents</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Type</span>
                  <span className="text-sm text-gray-900">Event Topic</span>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};

export default TopicDetailsPage;