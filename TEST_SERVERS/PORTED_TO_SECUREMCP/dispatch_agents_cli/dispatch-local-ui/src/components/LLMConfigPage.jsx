import React, { useState, useEffect } from "react";
import { KeyRound, RefreshCw, Plus, Trash2, Check, X, Shield } from "lucide-react";
import { Button } from "@ui/button";

const LLMConfigPage = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Add key form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [apiKey, setApiKey] = useState("");

  const loadProviders = async () => {
    try {
      const response = await fetch("/api/unstable/llm-config/local");
      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers || []);
      } else {
        setError("Failed to load provider configuration");
      }
    } catch (err) {
      console.error("Failed to load LLM config:", err);
      setError("Failed to connect to router");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);
    await loadProviders();
  };

  const handleAddKey = async (e) => {
    e.preventDefault();
    if (!selectedProvider || !apiKey.trim()) return;

    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch("/api/unstable/llm-config/local", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: selectedProvider, api_key: apiKey.trim() }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(data.message);
        setShowAddForm(false);
        setSelectedProvider("");
        setApiKey("");
        await loadProviders();
      } else {
        const data = await response.json();
        setError(data.detail || "Failed to save API key");
      }
    } catch (err) {
      setError("Failed to connect to router");
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveKey = async (provider) => {
    if (!confirm(`Remove API key for ${provider}? This will delete it from your Keychain.`)) {
      return;
    }

    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch(`/api/unstable/llm-config/local/${provider}`, {
        method: "DELETE",
      });

      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(data.message);
        await loadProviders();
      } else {
        const data = await response.json();
        setError(data.detail || "Failed to remove API key");
      }
    } catch (err) {
      setError("Failed to connect to router");
    }
  };

  // Auto-clear messages after 4 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 6000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const unconfiguredProviders = providers.filter((p) => !p.configured);

  if (loading && providers.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <KeyRound className="h-8 w-8 text-[var(--color-brand-blue-600)]" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">LLM Keys</h1>
            <p className="text-sm text-gray-500 mt-1">Manage API keys for local LLM providers</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-gray-600">Loading provider configuration...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <KeyRound className="h-8 w-8 text-[var(--color-brand-blue-600)]" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">LLM Keys</h1>
            <p className="text-sm text-gray-500 mt-1">Manage API keys for local LLM providers</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {unconfiguredProviders.length > 0 && (
            <Button
              onClick={() => {
                setShowAddForm(true);
                if (unconfiguredProviders.length > 0) {
                  setSelectedProvider(unconfiguredProviders[0].provider);
                }
              }}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Key
            </Button>
          )}
          <Button
            onClick={handleRefresh}
            disabled={loading}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Info Banner */}
      <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <Shield className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-blue-800">
          <span className="font-medium">Local Development Only</span> &mdash; API keys are stored
          securely in your macOS Keychain. Changes take effect immediately without restarting the
          router.
        </div>
      </div>

      {/* Status Messages */}
      {successMessage && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
          <Check className="w-4 h-4 flex-shrink-0" />
          {successMessage}
        </div>
      )}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
          <X className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Add Key Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Add API Key</h3>
          <form onSubmit={handleAddKey} className="flex items-end gap-4">
            <div className="flex-shrink-0">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Provider</label>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="block w-40 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {providers.map((p) => (
                  <option key={p.provider} value={p.provider}>
                    {p.provider.charAt(0).toUpperCase() + p.provider.slice(1)}
                    {p.configured ? " (update)" : ""}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={
                  selectedProvider
                    ? `Enter ${selectedProvider} API key...`
                    : "Select a provider first"
                }
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                disabled={!selectedProvider}
              />
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button type="submit" disabled={!selectedProvider || !apiKey.trim() || saving}>
                {saving ? "Saving..." : "Save"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowAddForm(false);
                  setSelectedProvider("");
                  setApiKey("");
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Providers Table */}
      <div className="bg-white rounded-lg border border-[var(--color-warm-gray-200)] overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Provider
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Storage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Environment Variable
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {providers.map((provider) => (
              <tr key={provider.provider} className="hover:bg-gray-50 transition-colors duration-150">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <KeyRound
                      className={`w-4 h-4 mr-3 ${
                        provider.configured ? "text-[var(--color-brand-blue-500)]" : "text-gray-300"
                      }`}
                    />
                    <span className="text-sm font-medium text-gray-900">
                      {provider.provider.charAt(0).toUpperCase() + provider.provider.slice(1)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {provider.configured ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                      Configured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                      <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                      Not configured
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-500">
                    {provider.storage_type || (provider.configured ? "unknown" : "\u2014")}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <code className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                    {provider.env_var}
                  </code>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => {
                        setShowAddForm(true);
                        setSelectedProvider(provider.provider);
                        setApiKey("");
                      }}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {provider.configured ? "Update" : "Add"}
                    </button>
                    {provider.configured && (
                      <button
                        onClick={() => handleRemoveKey(provider.provider)}
                        className="text-xs text-red-500 hover:text-red-700 font-medium flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        Remove
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LLMConfigPage;
