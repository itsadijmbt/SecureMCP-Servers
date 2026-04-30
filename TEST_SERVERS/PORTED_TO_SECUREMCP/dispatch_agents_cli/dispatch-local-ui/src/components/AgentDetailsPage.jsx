import React, { useState, useEffect } from 'react';
import { Button } from '@ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@ui/card';
import { Badge } from '@ui/badge';
import { Waypoints, Info, Clock, Rocket, Construction, Upload } from 'lucide-react';
import SendTestEventCard from './SendTestEventCard';
import MessageFeedCard from './MessageFeedCard';
import FunctionsCard from './FunctionsCard';

const AgentDetailsPage = ({ appState }) => {
  const {
    selectedAgent,
    statusBadgeClass,
    showAgentList
  } = appState;



  if (!selectedAgent) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No agent selected</p>
        <Button
          onClick={showAgentList}
          variant="outline"
          className="mt-4"
        >
          Back to Agents
        </Button>
      </div>
    );
  }

  const formatLastRun = (lastRun) => {
    if (!lastRun || lastRun === 'never') return 'Never';
    return lastRun;
  };

  const statusLevel = (status) => {
    const normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'good';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'pending';
    }
    return 'bad';
  };

  return (
    <div className="space-y-6">
      {/* Agent Header - Web-app style */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Waypoints className="h-8 w-8 text-[var(--color-brand-blue-600)]" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{selectedAgent.name}</h1>
            <div className="flex items-center mt-2 space-x-4">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                statusLevel(selectedAgent.status) === 'good'
                  ? 'bg-green-100 text-green-800'
                  : statusLevel(selectedAgent.status) === 'pending'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {selectedAgent.status || 'unknown'}
              </span>
              <span className="text-sm text-gray-500">Version {selectedAgent.version || 'v1'}</span>
              <span className="text-sm text-gray-400">•</span>
              <span className="text-sm text-gray-500">Last run {formatLastRun(selectedAgent.last_run)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column Layout: Main Content + Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Main Column (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Send Test Event Card */}
          <SendTestEventCard appState={{ ...appState, isAgentDetailsPage: true }} />

          {/* Functions Card - Shows @on and @fn handlers with invoke capability */}
          <FunctionsCard appState={appState} />

          {/* Message Feed Card */}
          <MessageFeedCard appState={appState} />
        </div>

        {/* Sidebar Column (1/3 width) */}
        <div className="space-y-6">

          {/* Agent Details Card - Web-app style */}
          <Card className="border-0 shadow-sm bg-gray-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-semibold text-gray-900">Agent Details</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 pb-6">
              <div className="grid grid-cols-1 gap-4">
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Name</span>
                  <span className="text-sm text-gray-900 font-medium">{selectedAgent.name}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Status</span>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    statusLevel(selectedAgent.status) === 'good'
                      ? 'bg-green-100 text-green-800'
                      : statusLevel(selectedAgent.status) === 'pending'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {selectedAgent.status || 'unknown'}
                  </span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Version</span>
                  <span className="text-sm text-gray-900">{selectedAgent.version || 'v1'}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-gray-600">Last Run</span>
                  <span className="text-sm text-gray-900">{formatLastRun(selectedAgent.last_run)}</span>
                </div>
                {selectedAgent.functions && selectedAgent.functions.length > 0 && (
                  <div className="flex justify-between py-2">
                    <span className="text-sm font-medium text-gray-600">Functions</span>
                    <span className="text-sm text-gray-900">{selectedAgent.functions.length} available</span>
                  </div>
                )}
                {selectedAgent.image && (
                  <div className="flex justify-between py-2">
                    <span className="text-sm font-medium text-gray-600">Image</span>
                    <span className="text-sm text-gray-900 font-mono text-xs break-all max-w-xs truncate">
                      {selectedAgent.image}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>


        </div>
      </div>
    </div>
  );
};

export default AgentDetailsPage;