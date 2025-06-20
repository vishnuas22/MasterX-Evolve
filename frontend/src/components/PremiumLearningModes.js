import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Target, 
  Bug, 
  Trophy, 
  GraduationCap,
  Sparkles,
  Settings,
  Zap,
  Users,
  BookOpen
} from 'lucide-react';
import { GlassCard, GlassButton } from './GlassCard';
import { useApp } from '../context/AppContext';

const learningModes = [
  {
    id: 'adaptive',
    name: 'Adaptive',
    icon: Brain,
    color: 'blue',
    description: 'AI automatically adapts to your learning style and pace',
    features: ['Personalized explanations', 'Dynamic difficulty', 'Multi-modal content'],
    bestFor: 'General learning and exploration'
  },
  {
    id: 'socratic',
    name: 'Socratic',
    icon: Target,
    color: 'purple',
    description: 'Learn through guided questions and discovery',
    features: ['Thought-provoking questions', 'Self-discovery', 'Critical thinking'],
    bestFor: 'Deep understanding and concept mastery'
  },
  {
    id: 'debug',
    name: 'Debug',
    icon: Bug,
    color: 'red',
    description: 'Identify and fix knowledge gaps systematically',
    features: ['Gap analysis', 'Targeted fixes', 'Misconception correction'],
    bestFor: 'Troubleshooting confusion and errors'
  },
  {
    id: 'challenge',
    name: 'Challenge',
    icon: Trophy,
    color: 'yellow',
    description: 'Progressive difficulty with hint system',
    features: ['Increasing difficulty', 'Progressive hints', 'Achievement tracking'],
    bestFor: 'Skill building and confidence growth'
  },
  {
    id: 'mentor',
    name: 'Mentor',
    icon: GraduationCap,
    color: 'green',
    description: 'Professional guidance and industry insights',
    features: ['Career advice', 'Industry context', 'Professional best practices'],
    bestFor: 'Career development and real-world application'
  }
];

export function PremiumLearningModes({ currentMode, onModeChange, isVisible, onClose }) {
  const { state, actions } = useApp();
  const [selectedMode, setSelectedMode] = useState(currentMode || 'adaptive');
  const [preferences, setPreferences] = useState({
    cost_effective: false,
    difficulty_preference: 'adaptive',
    interaction_style: 'collaborative'
  });

  const handleModeSelect = async (mode) => {
    setSelectedMode(mode.id);
    onModeChange(mode.id);

    // Update user preferences on the backend
    if (state.user) {
      try {
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/${state.user.id}/learning-mode`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            preferred_mode: mode.id,
            preferences: preferences
          })
        });
      } catch (error) {
        console.error('Error updating learning mode:', error);
      }
    }
  };

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
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
          className="w-full max-w-4xl max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <GlassCard className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Premium Learning Modes</h2>
                  <p className="text-gray-400">Choose your AI mentor's teaching style</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Learning Modes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {learningModes.map((mode) => {
                const IconComponent = mode.icon;
                const isSelected = selectedMode === mode.id;
                
                return (
                  <motion.button
                    key={mode.id}
                    onClick={() => handleModeSelect(mode)}
                    className={`p-4 rounded-xl text-left transition-all duration-300 ${
                      isSelected
                        ? `bg-${mode.color}-500/20 border border-${mode.color}-400/50`
                        : 'bg-white/5 border border-white/10 hover:bg-white/10'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`p-2 rounded-lg bg-${mode.color}-500/20`}>
                        <IconComponent className={`h-5 w-5 text-${mode.color}-400`} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white">{mode.name}</h3>
                        {isSelected && (
                          <div className="flex items-center space-x-1 text-xs text-green-400">
                            <Zap className="h-3 w-3" />
                            <span>Active</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-300 mb-3">{mode.description}</p>
                    
                    <div className="space-y-2">
                      <div className="text-xs text-gray-400 font-medium">Features:</div>
                      <ul className="text-xs text-gray-400 space-y-1">
                        {mode.features.map((feature, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                      
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <div className="text-xs text-gray-400 font-medium mb-1">Best for:</div>
                        <div className="text-xs text-gray-300">{mode.bestFor}</div>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>

            {/* Preferences Section */}
            <div className="border-t border-white/10 pt-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Learning Preferences</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Cost Effectiveness */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Cost Optimization
                  </label>
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={preferences.cost_effective}
                      onChange={(e) => handlePreferenceChange('cost_effective', e.target.checked)}
                      className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                    />
                    <span className="text-sm text-gray-400">
                      Prefer cost-effective models when quality is similar
                    </span>
                  </div>
                </div>

                {/* Difficulty Preference */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Difficulty Preference
                  </label>
                  <select
                    value={preferences.difficulty_preference}
                    onChange={(e) => handlePreferenceChange('difficulty_preference', e.target.value)}
                    className="w-full p-2 rounded-lg bg-white/10 border border-white/20 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="easy">Take it easy</option>
                    <option value="adaptive">Adaptive (recommended)</option>
                    <option value="challenging">Challenge me</option>
                  </select>
                </div>

                {/* Interaction Style */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Interaction Style
                  </label>
                  <select
                    value={preferences.interaction_style}
                    onChange={(e) => handlePreferenceChange('interaction_style', e.target.value)}
                    className="w-full p-2 rounded-lg bg-white/10 border border-white/20 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="collaborative">Collaborative</option>
                    <option value="direct">Direct & concise</option>
                    <option value="detailed">Detailed explanations</option>
                    <option value="encouraging">Extra encouraging</option>
                  </select>
                </div>
              </div>
            </div>

            {/* AI Model Information */}
            <div className="border-t border-white/10 pt-6 mt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-1">Current AI Model</h4>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-sm text-gray-400">DeepSeek R1 70B (Groq)</span>
                    <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">Premium</span>
                  </div>
                </div>
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    // This could open a model management modal
                    console.log('Open model management');
                  }}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Manage Models
                </GlassButton>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Advanced reasoning model optimized for learning and education
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mt-6">
              <GlassButton variant="secondary" onClick={onClose}>
                Cancel
              </GlassButton>
              <GlassButton onClick={onClose}>
                <BookOpen className="h-4 w-4 mr-2" />
                Start Learning
              </GlassButton>
            </div>
          </GlassCard>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export function LearningModeIndicator({ currentMode, onClick }) {
  const mode = learningModes.find(m => m.id === currentMode) || learningModes[0];
  const IconComponent = mode.icon;

  return (
    <motion.button
      onClick={onClick}
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg bg-${mode.color}-500/20 border border-${mode.color}-400/30 text-${mode.color}-300 hover:bg-${mode.color}-500/30 transition-all duration-300`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <IconComponent className="h-4 w-4" />
      <span className="text-sm font-medium">{mode.name}</span>
      <Settings className="h-3 w-3 opacity-60" />
    </motion.button>
  );
}