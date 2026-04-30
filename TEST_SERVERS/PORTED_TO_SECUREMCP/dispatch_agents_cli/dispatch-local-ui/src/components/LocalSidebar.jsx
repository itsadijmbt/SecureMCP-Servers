import React from 'react';
import { Waypoints, Radio, KeyRound } from 'lucide-react';

export function LocalSidebar({ appState }) {
  const { currentView, showAgentList, showTopicsList, showLLMConfig } = appState;

  const isAgentsActive = currentView === 'agent-list' || currentView === 'agent-details';
  const isTopicsActive = currentView === 'topics-list' || currentView === 'topic-details';
  const isLLMConfigActive = currentView === 'llm-config';

  return (
    <div
      className="flex flex-col m-3 rounded-xl relative transition-all duration-300 ease-out"
      style={{
        width: '244px',
        background: 'linear-gradient(to bottom, rgba(239, 246, 255, 0.8), rgba(219, 234, 254, 0.8))',
        boxShadow: `
          inset -10px -8px 0px -11px rgba(255, 255, 255, 0.6),
          inset 0px -9px 0px -8px rgba(255, 255, 255, 0.4),
          inset 10px 10px 20px -10px rgba(255, 255, 255, 0.3),
          inset -10px -10px 20px -10px rgba(0, 0, 0, 0.05)
        `,
        backdropFilter: `blur(2px) saturate(160%)`,
      }}>
      {/* Glass shine overlay */}
      <div
        className="absolute inset-0 rounded-xl pointer-events-none"
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(1px)',
          WebkitBackdropFilter: 'blur(1px)',
          boxShadow: `
            inset -10px -8px 0px -11px rgba(255, 255, 255, 1),
            inset 0px -9px 0px -8px rgba(255, 255, 255, 1)
          `,
          opacity: 0.6,
          zIndex: -1,
          filter: 'blur(8px) drop-shadow(10px 4px 6px rgba(0, 0, 0, 1)) brightness(115%)'
        }}
      />

      {/* Gold bar at top - indicates LOCAL DEV UI */}
      <div className="h-1 bg-gradient-to-r from-yellow-400 via-yellow-500 to-amber-500 rounded-t-xl"></div>

      {/* Logo section */}
      <div className="flex items-center gap-3 p-4 pb-2 flex-shrink-0" style={{filter: 'blur(0px) brightness(100%)'}}>
        <h1 className="text-lg font-bold text-[var(--color-brand-blue-700)] tracking-wider uppercase">DISPATCH</h1>
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r from-yellow-100 to-amber-100 border border-yellow-300">
          <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-yellow-500 to-amber-500"></div>
          <span className="text-xs text-yellow-800 font-semibold uppercase tracking-wider">
            LOCAL
          </span>
        </div>
      </div>

      <div className="flex-1 flex flex-col pt-1 overflow-y-auto" style={{filter: 'blur(0px) brightness(100%)'}}>
        <nav className="mt-1 flex flex-col flex-1 px-2 space-y-0.5">
          {/* Navigation section */}
          <div className="px-3 py-1.5">
            <p className="text-xs font-semibold text-[var(--color-warm-gray-600)] uppercase tracking-wider">
              Local
            </p>
          </div>

          {/* Agent List link */}
          <div>
            <button
              onClick={showAgentList}
              className={`flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ${
                !isAgentsActive ? 'hover:bg-white hover:bg-opacity-20' : ''
              }`}
              style={{
                background: isAgentsActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
                color: isAgentsActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
              }}
            >
              <Waypoints className="w-4 h-4 mr-3" />
              Agents
            </button>
          </div>

          {/* Topics List link */}
          <div>
            <button
              onClick={showTopicsList}
              className={`flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ${
                !isTopicsActive ? 'hover:bg-white hover:bg-opacity-20' : ''
              }`}
              style={{
                background: isTopicsActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
                color: isTopicsActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
              }}
            >
              <Radio className="w-4 h-4 mr-3" />
              Topics
            </button>
          </div>

          {/* Settings section */}
          <div className="px-3 py-1.5 mt-4">
            <p className="text-xs font-semibold text-[var(--color-warm-gray-600)] uppercase tracking-wider">
              Settings
            </p>
          </div>

          {/* LLM Keys link */}
          <div>
            <button
              onClick={showLLMConfig}
              className={`flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ${
                !isLLMConfigActive ? 'hover:bg-white hover:bg-opacity-20' : ''
              }`}
              style={{
                background: isLLMConfigActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
                color: isLLMConfigActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
              }}
            >
              <KeyRound className="w-4 h-4 mr-3" />
              LLM Keys
            </button>
          </div>
        </nav>
      </div>
    </div>
  );
}