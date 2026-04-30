import React, { useState, useEffect } from 'react';
import { LocalSidebar } from './LocalSidebar';
import { LocalHeader } from './LocalHeader';
import AgentListPage from './AgentListPage';
import AgentDetailsPage from './AgentDetailsPage';
import TopicsPage from './TopicsPage';
import TopicDetailsPage from './TopicDetailsPage';
import LLMConfigPage from './LLMConfigPage';

const App = () => {
  // Navigation state
  const [currentView, setCurrentView] = useState('agent-list'); // 'agent-list' | 'agent-details' | 'topics-list' | 'topic-details' | 'llm-config'
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);

  // Core app state
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [topics, setTopics] = useState([]);
  const [healthStatus, setHealthStatus] = useState('loading');

  // Navigation functions
  const showAgentList = () => {
    setCurrentView('agent-list');
    setSelectedAgent(null);
    setSelectedAgentId(null);
  };

  const showAgentDetails = (agent) => {
    setSelectedAgent(agent);
    setSelectedAgentId(agent.name);
    setSelectedTopic(null);
    setCurrentView('agent-details');
  };

  const showTopicsList = () => {
    setCurrentView('topics-list');
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setSelectedTopic(null);
  };

  const showTopicDetails = (topic) => {
    setSelectedTopic(topic);
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setCurrentView('topic-details');
  };

  const showLLMConfig = () => {
    setCurrentView('llm-config');
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setSelectedTopic(null);
  };

  // Status helper methods
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

  const statusBadgeClass = (status) => {
    const level = statusLevel(status);
    if (level === 'good') return 'bg-emerald-500 text-white px-2 py-1 text-xs font-medium rounded-md';
    if (level === 'pending') return 'bg-amber-500 text-white px-2 py-1 text-xs font-medium rounded-md';
    return 'bg-red-500 text-white px-2 py-1 text-xs font-medium rounded-md';
  };

  // Computed properties
  const runningAgents = agents.filter(agent => statusLevel(agent.status) === 'good').length;
  const totalTopics = topics.length || 0;


  // API functions
  const checkHealth = async () => {
    try {
      const response = await fetch('/health');
      setHealthStatus(response.ok ? 'healthy' : 'error');
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus('error');
    }
  };

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/system/status');
      if (response.ok) {
        setSystemStatus(await response.json());
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/unstable/agents/list');
      if (response.ok) {
        const data = await response.json();
        setAgents((data || []).map(agent => ({
          ...agent,
          status: agent?.status ? agent.status.toString().toLowerCase() : '',
        })));
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      setAgents([]);
    }
  };

  const loadTopics = async () => {
    try {
      const response = await fetch('/ui/topics');
      if (response.ok) {
        const data = await response.json();
        setTopics(data.topics || []);
      } else {
        setTopics([]);
      }
    } catch (error) {
      console.error('Failed to load topics:', error);
      setTopics([]);
    }
  };

  const refreshAgents = async () => {
    setLoading(true);
    await loadAgents();
    setLoading(false);
  };

  // Initialization
  useEffect(() => {
    const initializeApp = async () => {

      // Load initial data
      await checkHealth();
      await loadSystemStatus();
      await loadAgents();
      await loadTopics();
      setLoading(false);


      // Set up refresh interval
      const interval = setInterval(() => {
        checkHealth();
        if (Math.random() < 0.6) {
          loadSystemStatus();
          loadTopics();
        }
        if (currentView === 'agent-list' && Math.random() < 0.8) {
          loadAgents();
        }
      }, 5000);

      return () => clearInterval(interval);
    };

    initializeApp();
  }, [currentView]);


  // Application state object for passing to components
  const appState = {
    // Navigation
    currentView,
    selectedAgent,
    selectedAgentId,
    selectedTopic,
    showAgentList,
    showAgentDetails,
    showTopicsList,
    showTopicDetails,
    showLLMConfig,

    // Core data
    loading,
    setLoading,
    agents,
    setAgents,
    systemStatus,
    topics,
    healthStatus,

    // Computed values
    runningAgents,
    totalTopics,

    // Utility functions
    statusLevel,
    statusBadgeClass,
    refreshAgents,

    // API functions
    checkHealth,
    loadSystemStatus,
    loadAgents,
    loadTopics
  };

  // Generate breadcrumbs based on current view
  const getBreadcrumbs = () => {
    if (currentView === 'agent-list') {
      return [{ label: 'Agent Registry' }];
    }
    if (currentView === 'agent-details' && selectedAgent) {
      return [
        {
          label: 'Agent Registry',
          onClick: showAgentList
        },
        { label: selectedAgent.name }
      ];
    }
    if (currentView === 'topics-list') {
      return [{ label: 'Topics' }];
    }
    if (currentView === 'topic-details' && selectedTopic) {
      return [
        {
          label: 'Topics',
          onClick: showTopicsList
        },
        { label: typeof selectedTopic === 'string' ? selectedTopic : selectedTopic.name }
      ];
    }
    if (currentView === 'llm-config') {
      return [{ label: 'LLM Keys' }];
    }
    return [];
  };

  return (
    <div className="h-screen flex relative app-background">
      <LocalSidebar appState={appState} />
      <div className="flex-1 flex flex-col overflow-hidden bg-white m-3 rounded-xl">
        <LocalHeader breadcrumbs={getBreadcrumbs()} />
        <div className="flex-1 overflow-auto bg-white p-6 relative">
          {currentView === 'agent-list' && (
            <AgentListPage appState={appState} />
          )}
          {currentView === 'agent-details' && (
            <AgentDetailsPage appState={appState} />
          )}
          {currentView === 'topics-list' && (
            <TopicsPage appState={appState} />
          )}
          {currentView === 'topic-details' && (
            <TopicDetailsPage appState={appState} />
          )}
          {currentView === 'llm-config' && (
            <LLMConfigPage />
          )}
        </div>
      </div>
    </div>
  );
};

export default App;