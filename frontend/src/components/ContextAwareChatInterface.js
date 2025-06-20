import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Heart, 
  Gauge, 
  Clock, 
  Eye,
  Ear,
  Hand,
  BookOpen,
  Zap,
  Target
} from 'lucide-react';
import { api } from '../services/api';

const ContextAwareChatInterface = ({ sessionId, userId, onMessage }) => {
  const [contextState, setContextState] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [adaptiveSettings, setAdaptiveSettings] = useState({
    responseComplexity: 0.5,
    preferredPace: 0.5,
    explanationDepth: 0.5,
    interactionStyle: 'balanced'
  });
  const [emotionalInsights, setEmotionalInsights] = useState(null);
  const [learningStyleAdaptations, setLearningStyleAdaptations] = useState({});

  // Emotion icons mapping
  const emotionIcons = {
    frustrated: '😤',
    confident: '😎',
    confused: '🤔',
    excited: '🤩',
    anxious: '😰',
    focused: '🎯',
    tired: '😴',
    motivated: '💪'
  };

  // Learning style icons
  const learningStyleIcons = {
    visual: <Eye className="w-4 h-4" />,
    auditory: <Ear className="w-4 h-4" />,
    kinesthetic: <Hand className="w-4 h-4" />,
    reading: <BookOpen className="w-4 h-4" />,
    multimodal: <Brain className="w-4 h-4" />
  };

  // Cognitive load colors
  const cognitiveLoadColors = {
    low: 'text-green-400',
    medium: 'text-yellow-400',
    high: 'text-orange-400',
    overload: 'text-red-400'
  };

  const analyzeContext = async (message, conversationContext) => {
    if (!message.trim()) return;
    
    setIsAnalyzing(true);
    try {
      const response = await api.axiosInstance.post('/context/analyze', {
        user_id: userId,
        session_id: sessionId,
        message: message,
        conversation_context: conversationContext
      });

      const { context_state, recommendations, adaptations, emotional_insights } = response.data;
      
      setContextState(context_state);
      setAdaptiveSettings({
        responseComplexity: recommendations.response_complexity,
        preferredPace: recommendations.preferred_pace,
        explanationDepth: recommendations.explanation_depth,
        interactionStyle: recommendations.interaction_style
      });
      setLearningStyleAdaptations(adaptations);
      setEmotionalInsights(emotional_insights);

    } catch (error) {
      console.error('Error analyzing context:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sendContextAwareMessage = async (message, conversationContext) => {
    try {
      // First analyze context
      await analyzeContext(message, conversationContext);
      
      // Then send message with context awareness
      const response = await api.axiosInstance.post('/chat/premium-context', {
        session_id: sessionId,
        user_message: message,
        context: {
          learning_mode: 'adaptive',
          enable_context_awareness: true,
          adaptive_settings: adaptiveSettings
        }
      });

      if (onMessage) {
        onMessage(response.data);
      }

      return response.data;
    } catch (error) {
      console.error('Error sending context-aware message:', error);
      throw error;
    }
  };

  const ContextInsightsPanel = () => {
    if (!contextState) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-gray-700/50 mb-4"
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-400" />
            Context Awareness
          </h3>
          {isAnalyzing && (
            <div className="flex items-center gap-2 text-blue-400">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-400 border-t-transparent"></div>
              <span className="text-sm">Analyzing...</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Emotional State */}
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Heart className="w-4 h-4 text-pink-400" />
              <span className="text-sm font-medium text-pink-400">Emotional State</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">
                {emotionalInsights?.state ? emotionIcons[emotionalInsights.state] : '🎯'}
              </span>
              <div>
                <div className="text-white text-sm capitalize">
                  {emotionalInsights?.state || 'focused'}
                </div>
                <div className="text-gray-400 text-xs">
                  {Math.round((emotionalInsights?.confidence || 0.5) * 100)}% confidence
                </div>
              </div>
            </div>
          </div>

          {/* Learning Style */}
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="text-purple-400">
                {learningStyleIcons[contextState.learning_style]}
              </div>
              <span className="text-sm font-medium text-purple-400">Learning Style</span>
            </div>
            <div className="text-white text-sm capitalize">
              {contextState.learning_style}
            </div>
            <div className="text-gray-400 text-xs">
              {Math.round(contextState.style_confidence * 100)}% confidence
            </div>
          </div>

          {/* Cognitive Load */}
          <div className="bg-gray-900/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Gauge className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium text-cyan-400">Cognitive Load</span>
            </div>
            <div className={`text-sm capitalize ${cognitiveLoadColors[contextState.cognitive_load]}`}>
              {contextState.cognitive_load}
            </div>
            <div className="text-gray-400 text-xs">
              Load: {Math.round(contextState.response_complexity * 100)}%
            </div>
          </div>
        </div>

        {/* Adaptive Settings */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-900/50 rounded-lg p-2">
            <div className="flex items-center gap-1 mb-1">
              <Zap className="w-3 h-3 text-yellow-400" />
              <span className="text-xs text-yellow-400">Pace</span>
            </div>
            <div className="text-white text-xs">
              {Math.round(adaptiveSettings.preferredPace * 100)}%
            </div>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-2">
            <div className="flex items-center gap-1 mb-1">
              <Target className="w-3 h-3 text-green-400" />
              <span className="text-xs text-green-400">Depth</span>
            </div>
            <div className="text-white text-xs">
              {Math.round(adaptiveSettings.explanationDepth * 100)}%
            </div>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-2">
            <div className="flex items-center gap-1 mb-1">
              <Brain className="w-3 h-3 text-blue-400" />
              <span className="text-xs text-blue-400">Complexity</span>
            </div>
            <div className="text-white text-xs">
              {Math.round(adaptiveSettings.responseComplexity * 100)}%
            </div>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-2">
            <div className="flex items-center gap-1 mb-1">
              <Clock className="w-3 h-3 text-purple-400" />
              <span className="text-xs text-purple-400">Style</span>
            </div>
            <div className="text-white text-xs capitalize">
              {adaptiveSettings.interactionStyle}
            </div>
          </div>
        </div>

        {/* Learning Adaptations */}
        {Object.keys(learningStyleAdaptations).length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Active Adaptations</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(learningStyleAdaptations).map(([key, value]) => (
                value && (
                  <span
                    key={key}
                    className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full"
                  >
                    {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                  </span>
                )
              ))}
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  const EmotionalStateIndicator = () => {
    if (!emotionalInsights) return null;

    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="fixed top-4 right-4 z-50"
      >
        <div className="bg-gray-800/90 backdrop-blur-xl rounded-full p-3 border border-gray-700/50 shadow-lg">
          <div className="flex items-center gap-2">
            <span className="text-xl">
              {emotionIcons[emotionalInsights.state] || '🎯'}
            </span>
            <div className="text-white text-sm">
              <div className="capitalize">{emotionalInsights.state}</div>
              <div className="text-xs text-gray-400">
                {Math.round(emotionalInsights.confidence * 100)}%
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  return {
    ContextInsightsPanel,
    EmotionalStateIndicator,
    analyzeContext,
    sendContextAwareMessage,
    contextState,
    adaptiveSettings,
    emotionalInsights
  };
};

export default ContextAwareChatInterface;