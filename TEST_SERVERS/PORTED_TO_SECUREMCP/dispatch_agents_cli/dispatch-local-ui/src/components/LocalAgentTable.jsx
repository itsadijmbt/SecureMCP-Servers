import React from "react";
import { Badge } from "@ui/badge";
import { Waypoints } from "lucide-react";

export function LocalAgentTable({ agents, onAgentSelect, isLoading = false }) {

  const formatLastRun = (lastRun) => {
    if (!lastRun || lastRun === 'never') return 'Never';
    return lastRun;
  };

  const getStatusBadgeVariant = (status) => {
    const normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'success';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'secondary';
    }
    return 'secondary';
  };

  const getStatusColor = (status) => {
    const normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'bg-green-500';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'bg-yellow-500';
    }
    return 'bg-red-500';
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Loading agents...</span>
        </div>
      </div>
    );
  }

  if (agents.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8">
        <div className="text-center">
          <Waypoints className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-sm font-medium text-gray-900">No agents found</h3>
          <p className="mt-2 text-sm text-gray-500">
            Deploy an agent to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              URL
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {agents.map((agent, index) => (
            <tr
              key={agent.name || index}
              className="hover:bg-gray-50 cursor-pointer transition-colors duration-150"
              onClick={() => onAgentSelect(agent)}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <Waypoints className="w-4 h-4 text-[var(--color-brand-blue-500)] mr-3" />
                  <div className="text-sm font-medium text-gray-900">{agent.name}</div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500 font-mono">{agent.url || '-'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${getStatusColor(agent.status)}`} />
                  <Badge variant={getStatusBadgeVariant(agent.status)} className="text-xs">
                    {agent.status || 'unknown'}
                  </Badge>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}