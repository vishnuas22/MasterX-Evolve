import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, BookOpen, Target, Settings, Brain, Trophy, Zap, Eye, Heart } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { GlassCard, GlassButton, GlassInput } from './GlassCard';
import { TypingIndicator } from './LoadingSpinner';
import { PremiumLearningModes, LearningModeIndicator } from './PremiumLearningModes';
import { ModelManagement } from './ModelManagement';
import { GamificationDashboard } from './GamificationDashboard';
import { AdvancedStreamingInterface } from './AdvancedStreamingInterface';
import ContextAwareChatInterface from './ContextAwareChatInterface';
import LiveLearningInterface from './LiveLearningInterface';
import { useApp } from '../context/AppContext';

export function ChatInterface() {
  const { state, actions } = useApp();
  const [inputMessage, setInputMessage] = useState('');
  const [learningMode, setLearningMode] = useState('adaptive');
  const [showLearningModes, setShowLearningModes] = useState(false);
  const [showModelManagement, setShowModelManagement] = useState(false);
  const [showGamification, setShowGamification] = useState(false);
  const [showLiveLearning, setShowLiveLearning] = useState(false);
  const [useAdvancedStreaming, setUseAdvancedStreaming] = useState(false);
  const [useContextAwareness, setUseContextAwareness] = useState(true);
  const [currentView, setCurrentView] = useState('chat'); // 'chat', 'live-learning'
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize context awareness component
  const contextAwareChat = ContextAwareChatInterface({
    sessionId: state.currentSession?.id,
    userId: state.user?.id,
    onMessage: (response) => {
      // Handle context-aware message response
      actions.addMessage({
        id: Date.now().toString(),
        message: response.response,
        sender: 'mentor',
        timestamp: new Date().toISOString(),
        learning_mode: 'context_aware',
        suggestions: response.suggested_actions,
        next_steps: response.next_steps,
        metadata: response.metadata
      });
    }
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, state.streamingMessage]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !state.currentSession || state.isTyping) return;

    const message = inputMessage.trim();
    setInputMessage('');

    try {
      if (useContextAwareness) {
        // Use context-aware premium chat
        const conversationContext = state.messages.map(msg => ({
          sender: msg.sender,
          message: msg.message,
          timestamp: msg.timestamp
        }));
        
        await contextAwareChat.sendContextAwareMessage(message, conversationContext);
      } else if (useAdvancedStreaming) {
        // Use advanced streaming interface
        // The AdvancedStreamingInterface component will handle the streaming
        return;
      } else {
        // Use regular premium message
        await actions.sendPremiumMessage(state.currentSession.id, message, {
          learning_mode: learningMode,
          user_preferences: {
            difficulty_preference: 'adaptive',
            interaction_style: 'collaborative'
          }
        });
      }
    } catch (error) {
      console.error('Error sending premium message:', error);
      // Fallback to regular message
      try {
        await actions.sendMessage(state.currentSession.id, message);
      } catch (fallbackError) {
        console.error('Error sending fallback message:', fallbackError);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  if (!state.currentSession) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <GlassCard className="p-8 text-center max-w-md">
          <Bot className="h-16 w-16 text-blue-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-100 mb-2">Welcome to MasterX</h3>
          <p className="text-gray-400 mb-6">
            Your AI-powered learning companion. Start a new session to begin your learning journey.
          </p>
          
          {/* Quick start options */}
          <div className="space-y-3">
            <GlassButton
              onClick={async () => {
                try {
                  if (!state.user?.id) {
                    actions.setError('User not found. Please refresh and try again.');
                    return;
                  }

                  actions.setLoading(true);
                  
                  // Create a new session with default settings
                  const sessionData = {
                    user_id: state.user.id,
                    subject: 'General Learning',
                    difficulty_level: 'intermediate',
                    learning_objectives: ['Explore new topics', 'Interactive learning', 'Skill development']
                  };
                  
                  await actions.createSession(sessionData);
                  console.log('New session created successfully');
                } catch (error) {
                  console.error('Error creating session:', error);
                  actions.setError('Failed to create session. Please try again.');
                } finally {
                  actions.setLoading(false);
                }
              }}
              className="w-full"
              disabled={state.isLoading}
            >
              <BookOpen className="h-4 w-4 mr-2" />
              {state.isLoading ? 'Creating Session...' : 'Start Learning'}
            </GlassButton>
            
            {/* Subject-specific quick start buttons */}
            <div className="grid grid-cols-2 gap-2 mt-4">
              {[
                { subject: 'Programming', icon: '💻' },
                { subject: 'Mathematics', icon: '🔢' },
                { subject: 'Science', icon: '🔬' },
                { subject: 'Language', icon: '🗣️' }
              ].map(({ subject, icon }) => (
                <GlassButton
                  key={subject}
                  size="sm"
                  variant="secondary"
                  onClick={async () => {
                    try {
                      if (!state.user?.id) {
                        actions.setError('User not found. Please refresh and try again.');
                        return;
                      }

                      actions.setLoading(true);
                      
                      const sessionData = {
                        user_id: state.user.id,
                        subject: subject,
                        difficulty_level: 'intermediate',
                        learning_objectives: [`Learn ${subject}`, 'Practice skills', 'Build understanding']
                      };
                      
                      await actions.createSession(sessionData);
                    } catch (error) {
                      console.error('Error creating session:', error);
                      actions.setError('Failed to create session. Please try again.');
                    } finally {
                      actions.setLoading(false);
                    }
                  }}
                  disabled={state.isLoading}
                  className="flex flex-col items-center p-3"
                >
                  <span className="text-lg mb-1">{icon}</span>
                  <span className="text-xs">{subject}</span>
                </GlassButton>
              ))}
            </div>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Enhanced Chat Header */}
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Bot className="h-8 w-8 text-blue-400" />
              <div className="absolute -bottom-1 -right-1 h-3 w-3 bg-green-400 rounded-full border-2 border-gray-900"></div>
              {useContextAwareness && (
                <div className="absolute -top-1 -right-1 h-3 w-3 bg-purple-400 rounded-full border-2 border-gray-900" title="Context Awareness Active">
                  <Brain className="h-2 w-2 text-white" />
                </div>
              )}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-100">MasterX AI Mentor</h2>
              <p className="text-sm text-gray-400">
                {state.currentSession.subject || 'General Learning'} • {state.currentSession.difficulty_level}
                {useContextAwareness && <span className="text-purple-400 ml-2">• Context Aware</span>}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {/* View Toggle */}
            <div className="flex bg-gray-800 rounded-lg p-1">
              <GlassButton
                size="sm"
                variant={currentView === 'chat' ? 'primary' : 'secondary'}
                onClick={() => setCurrentView('chat')}
                className="px-3 py-1"
              >
                Chat
              </GlassButton>
              <GlassButton
                size="sm"
                variant={currentView === 'live-learning' ? 'primary' : 'secondary'}
                onClick={() => setCurrentView('live-learning')}
                className="px-3 py-1"
              >
                <Zap className="h-3 w-3 mr-1" />
                Live
              </GlassButton>
            </div>
            
            {/* Context Awareness Toggle */}
            <GlassButton
              size="sm"
              variant={useContextAwareness ? 'primary' : 'secondary'}
              onClick={() => setUseContextAwareness(!useContextAwareness)}
              title="Toggle Context Awareness"
            >
              <Brain className="h-4 w-4" />
            </GlassButton>
            
            <LearningModeIndicator 
              currentMode={learningMode}
              onClick={() => setShowLearningModes(true)}
            />
            <GlassButton 
              size="sm" 
              variant="secondary"
              onClick={() => setShowGamification(true)}
            >
              <Trophy className="h-4 w-4" />
            </GlassButton>
            <GlassButton 
              size="sm" 
              variant="secondary"
              onClick={() => setShowModelManagement(true)}
            >
              <Settings className="h-4 w-4" />
            </GlassButton>
          </div>
        </div>
        
        {/* Context Awareness Panel */}
        {useContextAwareness && currentView === 'chat' && (
          <contextAwareChat.ContextInsightsPanel />
        )}
      </div>

      {/* Main Content Area */}
      <AnimatePresence mode="wait">
        {currentView === 'chat' ? (
          <motion.div
            key="chat"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="flex-1 flex flex-col"
          >
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <AnimatePresence>
                {state.messages.map((message, index) => (
                  <ChatMessage key={message.id || index} message={message} />
                ))}
                
                {/* Advanced Streaming Interface */}
                {useAdvancedStreaming && inputMessage && (
                  <AdvancedStreamingInterface
                    message={inputMessage}
                    sessionId={state.currentSession?.id}
                    onStreamComplete={(result) => {
                      // Handle stream completion
                      setUseAdvancedStreaming(false);
                      setInputMessage('');
                    }}
                    streamingConfig={{
                      multiBranch: true,
                      factCheck: true,
                      interruptible: true
                    }}
                  />
                )}
                
                {/* Regular Streaming message */}
                {state.isTyping && !useAdvancedStreaming && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="flex items-start space-x-3"
                  >
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <GlassCard className="p-4">
                        {state.streamingMessage ? (
                          <div className="prose prose-invert max-w-none">
                            <ReactMarkdown>{state.streamingMessage}</ReactMarkdown>
                            <span className="inline-block w-2 h-5 bg-blue-400 animate-pulse ml-1"></span>
                          </div>
                        ) : (
                          <TypingIndicator />
                        )}
                      </GlassCard>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Enhanced Input Area */}
            <div className="border-t border-white/10 p-4">
              <form onSubmit={handleSendMessage} className="flex space-x-3">
                <div className="flex-1 relative">
                  <GlassInput
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={useContextAwareness ? "Ask me anything... (Context aware)" : "Ask me anything..."}
                    className="w-full pr-16"
                    disabled={state.isTyping}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                    {useContextAwareness && <Brain className="h-3 w-3 text-purple-400" />}
                    <Sparkles className="h-4 w-4 text-blue-400" />
                  </div>
                </div>
                <GlassButton
                  type="submit"
                  disabled={!inputMessage.trim() || state.isTyping}
                  className="px-4"
                >
                  <Send className="h-4 w-4" />
                </GlassButton>
              </form>
              
              {/* Enhanced Quick Actions */}
              <div className="flex flex-wrap gap-2 mt-3">
                <GlassButton
                  size="sm"
                  variant={useContextAwareness ? "primary" : "secondary"}
                  onClick={() => setUseContextAwareness(!useContextAwareness)}
                >
                  <Brain className="h-3 w-3 mr-1" />
                  Context Aware
                </GlassButton>
                <GlassButton
                  size="sm"
                  variant={useAdvancedStreaming ? "primary" : "secondary"}
                  onClick={() => setUseAdvancedStreaming(!useAdvancedStreaming)}
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  Advanced Stream
                </GlassButton>
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => setInputMessage("Can you create an exercise for me?")}
                  disabled={state.isTyping}
                >
                  Generate Exercise
                </GlassButton>
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => setInputMessage("Explain this concept step by step")}
                  disabled={state.isTyping}
                >
                  Step-by-Step
                </GlassButton>
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => setInputMessage("Give me a real-world example")}
                  disabled={state.isTyping}
                >
                  Real Example
                </GlassButton>
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    setLearningMode('challenge');
                    setInputMessage("Give me a challenge problem");
                  }}
                  disabled={state.isTyping}
                >
                  Challenge Me
                </GlassButton>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="live-learning"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex-1"
          >
            <LiveLearningInterface
              userId={state.user?.id}
              onSessionUpdate={(session) => {
                console.log('Live session updated:', session);
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Emotional State Indicator */}
      {useContextAwareness && <contextAwareChat.EmotionalStateIndicator />}

      {/* Modals */}
      <GamificationDashboard
        isVisible={showGamification}
        onClose={() => setShowGamification(false)}
      />

      <PremiumLearningModes
        currentMode={learningMode}
        onModeChange={setLearningMode}
        isVisible={showLearningModes}
        onClose={() => setShowLearningModes(false)}
      />

      <ModelManagement
        isVisible={showModelManagement}
        onClose={() => setShowModelManagement(false)}
      />
    </div>
  );
}

function ChatMessage({ message }) {
  const isUser = message.sender === 'user';
  const isTyping = message.sender === 'mentor' && !message.message;
  const isPremium = message.learning_mode && message.learning_mode !== 'adaptive';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-start space-x-3`}
    >
      {!isUser && (
        <div className="flex-shrink-0">
          <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
            isPremium 
              ? 'bg-gradient-to-r from-purple-500 to-pink-500' 
              : 'bg-gradient-to-r from-blue-500 to-purple-500'
          }`}>
            <Bot className="h-4 w-4 text-white" />
          </div>
        </div>
      )}
      
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        <GlassCard 
          className={`p-4 ${isUser 
            ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-blue-400/30' 
            : isPremium
              ? 'bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-purple-400/20'
              : 'bg-white/5 border-white/10'
          }`}
        >
          {isPremium && (
            <div className="flex items-center space-x-2 mb-2 pb-2 border-b border-white/10">
              <Sparkles className="h-3 w-3 text-purple-400" />
              <span className="text-xs text-purple-300 capitalize">{message.learning_mode} Mode</span>
            </div>
          )}
          
          {message.message ? (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown>{message.message}</ReactMarkdown>
            </div>
          ) : (
            <TypingIndicator />
          )}
          
          {/* Message suggestions */}
          {!isUser && message.suggestions && message.suggestions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-xs text-gray-400 mb-2">Suggested actions:</p>
              <div className="flex flex-wrap gap-2">
                {message.suggestions.map((suggestion, index) => (
                  <GlassButton
                    key={index}
                    size="sm"
                    variant="secondary"
                    className="text-xs"
                  >
                    {suggestion}
                  </GlassButton>
                ))}
              </div>
            </div>
          )}

          {/* Next steps for premium responses */}
          {!isUser && message.next_steps && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-xs text-purple-400 mb-1 flex items-center space-x-1">
                <Target className="h-3 w-3" />
                <span>Next Steps:</span>
              </p>
              <p className="text-xs text-gray-300">{message.next_steps}</p>
            </div>
          )}
        </GlassCard>
        
        <div className={`flex items-center mt-2 text-xs text-gray-500 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
          {isPremium && (
            <>
              <span className="mx-1">•</span>
              <span className="text-purple-400">Premium</span>
            </>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0">
          <div className="h-8 w-8 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center">
            <User className="h-4 w-4 text-white" />
          </div>
        </div>
      )}
    </motion.div>
  );
}
