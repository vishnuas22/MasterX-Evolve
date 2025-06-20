import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Key, 
  Plus, 
  Check, 
  X, 
  Zap,
  TrendingUp,
  Settings,
  Star,
  Lock,
  Unlock
} from 'lucide-react';
import { GlassCard, GlassButton, GlassInput } from './GlassCard';
import { api } from '../services/api';

const modelProviders = [
  {
    id: 'groq',
    name: 'Groq',
    description: 'Ultra-fast inference with DeepSeek R1 70B',
    models: ['DeepSeek R1 70B'],
    specialties: ['Reasoning', 'Learning', 'Explanation'],
    color: 'blue',
    icon: '🚀',
    keyPattern: 'gsk_*',
    docUrl: 'https://groq.com/docs'
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Advanced reasoning with Claude 3.5 Sonnet',
    models: ['Claude 3.5 Sonnet'],
    specialties: ['Mentoring', 'Analysis', 'Complex Reasoning'],
    color: 'purple',
    icon: '🧠',
    keyPattern: 'sk-ant-*',
    docUrl: 'https://docs.anthropic.com'
  },
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'Creative and comprehensive with GPT-4o',
    models: ['GPT-4o'],
    specialties: ['Creative Learning', 'Multimodal', 'Voice'],
    color: 'green',
    icon: '✨',
    keyPattern: 'sk-*',
    docUrl: 'https://platform.openai.com/docs'
  },
  {
    id: 'google',
    name: 'Google',
    description: 'Multimodal capabilities with Gemini Pro',
    models: ['Gemini 1.5 Pro'],
    specialties: ['Multimodal', 'Creative', 'Voice'],
    color: 'yellow',
    icon: '🌟',
    keyPattern: 'AIza*',
    docUrl: 'https://ai.google.dev/docs'
  }
];

export function ModelManagement({ isVisible, onClose }) {
  const [availableModels, setAvailableModels] = useState({});
  const [analytics, setAnalytics] = useState(null);
  const [addingProvider, setAddingProvider] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (isVisible) {
      loadModelData();
    }
  }, [isVisible]);

  const loadModelData = async () => {
    try {
      setIsLoading(true);
      const [modelsResponse, analyticsResponse] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/models/available`),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/models`)
      ]);

      if (modelsResponse.ok) {
        const modelsData = await modelsResponse.json();
        setAvailableModels(modelsData);
      }

      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }
    } catch (error) {
      console.error('Error loading model data:', error);
      setError('Failed to load model information');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddApiKey = async (providerId) => {
    if (!apiKey.trim()) {
      setError('Please enter a valid API key');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/models/add-key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: providerId,
          api_key: apiKey
        })
      });

      const result = await response.json();

      if (result.success) {
        setSuccess(`Successfully added ${providerId} models!`);
        setApiKey('');
        setAddingProvider(null);
        await loadModelData(); // Reload data
      } else {
        setError(result.message || 'Failed to add API key');
      }
    } catch (error) {
      console.error('Error adding API key:', error);
      setError('Failed to add API key');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="w-full max-w-5xl max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <GlassCard className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">AI Model Management</h2>
                  <p className="text-gray-400">Manage your AI models and API keys</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Analytics Summary */}
            {analytics && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <GlassCard className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-blue-500/20">
                      <Zap className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">{analytics.available_models?.length || 0}</div>
                      <div className="text-sm text-gray-400">Available Models</div>
                    </div>
                  </div>
                </GlassCard>

                <GlassCard className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-green-500/20">
                      <TrendingUp className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">{analytics.total_calls || 0}</div>
                      <div className="text-sm text-gray-400">Total API Calls</div>
                    </div>
                  </div>
                </GlassCard>

                <GlassCard className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-purple-500/20">
                      <Star className="h-5 w-5 text-purple-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">Premium</div>
                      <div className="text-sm text-gray-400">Service Level</div>
                    </div>
                  </div>
                </GlassCard>
              </div>
            )}

            {/* Error/Success Messages */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-400/30 text-red-300"
              >
                {error}
              </motion.div>
            )}

            {success && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-3 rounded-lg bg-green-500/20 border border-green-400/30 text-green-300"
              >
                {success}
              </motion.div>
            )}

            {/* Model Providers Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {modelProviders.map((provider) => {
                const isAvailable = availableModels.model_capabilities?.[provider.id === 'groq' ? 'deepseek-r1' : `${provider.id === 'anthropic' ? 'claude-sonnet' : provider.id === 'openai' ? 'gpt-4o' : 'gemini-pro'}`]?.available;
                const isAdding = addingProvider === provider.id;

                return (
                  <motion.div
                    key={provider.id}
                    layout
                    className={`p-5 rounded-xl border transition-all duration-300 ${
                      isAvailable
                        ? `bg-${provider.color}-500/10 border-${provider.color}-400/30`
                        : 'bg-white/5 border-white/10'
                    }`}
                  >
                    {/* Provider Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">{provider.icon}</div>
                        <div>
                          <h3 className="font-semibold text-white">{provider.name}</h3>
                          <p className="text-sm text-gray-400">{provider.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {isAvailable ? (
                          <div className="flex items-center space-x-1 text-green-400">
                            <Unlock className="h-4 w-4" />
                            <span className="text-xs">Active</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-1 text-gray-400">
                            <Lock className="h-4 w-4" />
                            <span className="text-xs">Locked</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Models List */}
                    <div className="mb-4">
                      <div className="text-xs text-gray-400 font-medium mb-2">Models:</div>
                      <div className="flex flex-wrap gap-2">
                        {provider.models.map((model, index) => (
                          <span
                            key={index}
                            className={`text-xs px-2 py-1 rounded ${
                              isAvailable
                                ? `bg-${provider.color}-500/20 text-${provider.color}-300`
                                : 'bg-gray-700 text-gray-400'
                            }`}
                          >
                            {model}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Specialties */}
                    <div className="mb-4">
                      <div className="text-xs text-gray-400 font-medium mb-2">Specialties:</div>
                      <div className="flex flex-wrap gap-1">
                        {provider.specialties.map((specialty, index) => (
                          <span
                            key={index}
                            className="text-xs px-2 py-1 rounded bg-white/10 text-gray-300"
                          >
                            {specialty}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* API Key Section */}
                    {!isAvailable && (
                      <div className="space-y-3">
                        {!isAdding ? (
                          <GlassButton
                            size="sm"
                            onClick={() => setAddingProvider(provider.id)}
                            className="w-full"
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Add API Key
                          </GlassButton>
                        ) : (
                          <div className="space-y-3">
                            <div>
                              <label className="block text-xs text-gray-400 mb-2">
                                API Key (Pattern: {provider.keyPattern})
                              </label>
                              <GlassInput
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder={`Enter your ${provider.name} API key`}
                                className="w-full text-sm"
                              />
                            </div>
                            <div className="flex space-x-2">
                              <GlassButton
                                size="sm"
                                onClick={() => handleAddApiKey(provider.id)}
                                disabled={isLoading}
                                className="flex-1"
                              >
                                <Check className="h-4 w-4 mr-2" />
                                {isLoading ? 'Adding...' : 'Add'}
                              </GlassButton>
                              <GlassButton
                                size="sm"
                                variant="secondary"
                                onClick={() => {
                                  setAddingProvider(null);
                                  setApiKey('');
                                  setError('');
                                }}
                                className="flex-1"
                              >
                                <X className="h-4 w-4 mr-2" />
                                Cancel
                              </GlassButton>
                            </div>
                            <a
                              href={provider.docUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                            >
                              📚 How to get API key →
                            </a>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Usage Stats for Available Models */}
                    {isAvailable && analytics?.usage_stats && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <div className="text-xs text-gray-400 mb-2">Usage this session:</div>
                        <div className="text-sm text-gray-300">
                          Active and ready for premium learning
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>

            {/* Footer */}
            <div className="flex justify-between items-center mt-6 pt-6 border-t border-white/10">
              <div className="text-sm text-gray-400">
                💡 Add multiple AI models to unlock advanced learning modes and better performance
              </div>
              <GlassButton onClick={onClose}>
                Done
              </GlassButton>
            </div>
          </GlassCard>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}