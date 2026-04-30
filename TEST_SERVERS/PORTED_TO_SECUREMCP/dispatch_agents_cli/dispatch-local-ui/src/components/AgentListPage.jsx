import React from 'react';
import { Button } from '@ui/button';
import { Waypoints, RefreshCw } from 'lucide-react';
import { LocalAgentTable } from './LocalAgentTable';

const AgentListPage = ({ appState }) => {
  const {
    loading,
    agents,
    showAgentDetails,
    refreshAgents,
    runningAgents,
    totalTopics
  } = appState;

  const handleAgentSelect = (agent) => {
    showAgentDetails(agent);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Waypoints className="h-8 w-8 text-[var(--color-brand-blue-600)]" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Local Agents</h1>
            <p className="text-sm text-[var(--color-warm-gray-600)]">
              Manage and monitor your agents • {runningAgents} running • {totalTopics} topics
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={refreshAgents}
            variant="outline"
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Agent Table */}
      <LocalAgentTable
        agents={agents}
        onAgentSelect={handleAgentSelect}
        isLoading={loading}
      />
    </div>
  );
};

export default AgentListPage;