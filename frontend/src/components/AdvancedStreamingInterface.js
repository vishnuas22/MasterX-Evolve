import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Pause, SkipForward, Settings, MessageSquare, 
  Zap, CheckCircle, AlertCircle, GitBranch, Eye
} from 'lucide-react';
import { GlassCard, GlassButton } from './GlassCard';
import { useApp } from '../context/AppContext';

export function AdvancedStreamingInterface({ 
  message, 
  sessionId, 
  onStreamComplete, 
  streamingConfig = {} 
}) {
  const { state } = useApp();
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [streamMetadata, setStreamMetadata] = useState({});
  const [canInterrupt, setCanInterrupt] = useState(false);
  const [showInterruptDialog, setShowInterruptDialog] = useState(false);
  const [showMultiBranch, setShowMultiBranch] = useState(false);
  const [factChecks, setFactChecks] = useState([]);
  const [readingSpeed, setReadingSpeed] = useState('normal');
  const [interruptMessage, setInterruptMessage] = useState('');
  const [branchResponses, setBranchResponses] = useState(null);
  
  const streamRef = useRef(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (message && sessionId) {
      startAdvancedStream();
    }
    
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [message, sessionId]);

  const startAdvancedStream = async () => {
    try {
      setIsStreaming(true);
      setStreamContent('');
      setFactChecks([]);
      setStreamMetadata({});

      // Create streaming session with user preferences
      const streamingSession = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/streaming/session`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            user_id: state.user.id,
            preferences: {
              reading_speed: readingSpeed,
              interrupt_enabled: true,
              multi_branch_mode: streamingConfig.multiBranch || false,
              fact_check_enabled: streamingConfig.factCheck !== false,
              ...streamingConfig
            }
          })
        }
      );

      if (!streamingSession.ok) {
        throw new Error('Failed to create streaming session');
      }

      // Start the advanced stream
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/streaming/${sessionId}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            context: {
              streaming_preferences: {
                reading_speed: readingSpeed,
                adaptive_pacing: true
              }
            }
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to start stream');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleStreamChunk(data);
            } catch (error) {
              console.error('Error parsing stream data:', error);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setIsStreaming(false);
    }
  };

  const handleStreamChunk = (data) => {
    switch (data.type) {
      case 'chunk':
        setStreamContent(prev => prev + data.content);
        setStreamMetadata(prev => ({ ...prev, ...data.metadata }));
        setCanInterrupt(data.metadata?.can_interrupt || false);
        break;
        
      case 'complete':
        setIsStreaming(false);
        setStreamMetadata(prev => ({ ...prev, ...data.metadata }));
        
        if (data.metadata?.fact_checks) {
          setFactChecks(data.metadata.fact_checks);
        }
        
        if (onStreamComplete) {
          onStreamComplete({
            content: streamContent,
            metadata: data.metadata
          });
        }
        break;
        
      case 'error':
        console.error('Stream error:', data.message);
        setIsStreaming(false);
        break;
        
      default:
        console.log('Unknown stream data type:', data);
    }
  };

  const handleInterrupt = async () => {
    if (!interruptMessage.trim()) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/streaming/${sessionId}/interrupt`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: state.user.id,
            message: interruptMessage
          })
        }
      );

      const result = await response.json();
      
      if (result.interruption_handled) {
        // Add interruption response to stream
        setStreamContent(prev => 
          prev + `\n\n**[Interruption Response]**\n${result.immediate_response}\n\n`
        );
      }

      setShowInterruptDialog(false);
      setInterruptMessage('');
    } catch (error) {
      console.error('Error handling interruption:', error);
    }
  };

  const generateMultiBranchResponse = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/streaming/multi-branch`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            message,
            branches: ['visual', 'logical', 'practical', 'simplified']
          })
        }
      );

      const result = await response.json();
      setBranchResponses(result);
      setShowMultiBranch(true);
    } catch (error) {
      console.error('Error generating multi-branch response:', error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Streaming Controls */}
      <GlassCard className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-blue-400" />
            <span className="text-white font-medium">Advanced Streaming</span>
            {isStreaming && (
              <motion.div
                className="h-2 w-2 bg-green-400 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <select
              value={readingSpeed}
              onChange={(e) => setReadingSpeed(e.target.value)}
              className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-sm"
              disabled={isStreaming}
            >
              <option value="slow">Slow</option>
              <option value="normal">Normal</option>
              <option value="fast">Fast</option>
            </select>
            
            <GlassButton
              size="sm"
              onClick={generateMultiBranchResponse}
              disabled={isStreaming}
            >
              <GitBranch className="h-4 w-4" />
            </GlassButton>
            
            <GlassButton
              size="sm"
              onClick={() => setShowInterruptDialog(true)}
              disabled={!canInterrupt || !isStreaming}
            >
              <MessageSquare className="h-4 w-4" />
            </GlassButton>
          </div>
        </div>

        {/* Stream Metadata */}
        {streamMetadata.word_count && (
          <div className="flex items-center space-x-4 text-sm text-gray-400 mb-3">
            <span>Words: {streamMetadata.word_count}</span>
            {streamMetadata.reading_time_estimate && (
              <span>Est. reading time: {Math.round(streamMetadata.reading_time_estimate)}s</span>
            )}
            {streamMetadata.interruption_points && (
              <span>Interrupt points: {streamMetadata.interruption_points}</span>
            )}
          </div>
        )}

        {/* Streaming Content */}
        <div className="relative">
          <div className="prose prose-invert max-w-none">
            {streamContent}
            {isStreaming && (
              <motion.span
                className="inline-block w-2 h-5 bg-blue-400 ml-1"
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
              />
            )}
          </div>
        </div>

        {/* Fact Checks */}
        {factChecks.length > 0 && (
          <div className="mt-4 pt-4 border-t border-white/10">
            <h4 className="text-sm font-medium text-white mb-2 flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span>Fact Checks</span>
            </h4>
            <div className="space-y-2">
              {factChecks.map((factCheck, index) => (
                <FactCheckCard key={index} factCheck={factCheck} />
              ))}
            </div>
          </div>
        )}
      </GlassCard>

      {/* Interrupt Dialog */}
      <AnimatePresence>
        {showInterruptDialog && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed inset-x-4 bottom-4 z-50"
          >
            <GlassCard className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                <MessageSquare className="h-5 w-5 text-blue-400" />
                <span className="text-white font-medium">Ask a Question</span>
              </div>
              
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={interruptMessage}
                  onChange={(e) => setInterruptMessage(e.target.value)}
                  placeholder="What would you like to clarify?"
                  className="flex-1 bg-white/10 border border-white/20 rounded px-3 py-2 text-white placeholder-gray-400"
                  onKeyPress={(e) => e.key === 'Enter' && handleInterrupt()}
                  autoFocus
                />
                <GlassButton onClick={handleInterrupt}>
                  Send
                </GlassButton>
                <GlassButton 
                  variant="secondary" 
                  onClick={() => setShowInterruptDialog(false)}
                >
                  Cancel
                </GlassButton>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Multi-Branch Response Modal */}
      <MultiBranchModal
        isVisible={showMultiBranch}
        branches={branchResponses}
        onClose={() => setShowMultiBranch(false)}
        onSelectBranch={(branchType, content) => {
          setStreamContent(content);
          setShowMultiBranch(false);
        }}
      />
    </div>
  );
}

function FactCheckCard({ factCheck }) {
  const statusColors = {
    verified: 'text-green-400 border-green-400/30 bg-green-400/10',
    disputed: 'text-red-400 border-red-400/30 bg-red-400/10',
    unverified: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10'
  };

  const StatusIcon = factCheck.verification_status === 'verified' ? CheckCircle :
                   factCheck.verification_status === 'disputed' ? AlertCircle : Eye;

  return (
    <div className={`p-3 rounded-lg border ${statusColors[factCheck.verification_status] || statusColors.unverified}`}>
      <div className="flex items-start space-x-3">
        <StatusIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="text-sm text-white font-medium">
            {factCheck.verification_status === 'verified' ? 'Verified' :
             factCheck.verification_status === 'disputed' ? 'Disputed' : 'Checking...'}
          </div>
          <div className="text-xs text-gray-300 mt-1">
            "{factCheck.content.slice(0, 100)}..."
          </div>
          {factCheck.sources && factCheck.sources.length > 0 && (
            <div className="text-xs text-gray-400 mt-2">
              Sources: {factCheck.sources.map(s => s.title).join(', ')}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-1">
            Confidence: {Math.round(factCheck.confidence_score * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
}

function MultiBranchModal({ isVisible, branches, onClose, onSelectBranch }) {
  if (!isVisible || !branches) return null;

  const branchIcons = {
    visual: '👁️',
    logical: '🧠',
    practical: '🔧',
    theoretical: '📚',
    simplified: '✨'
  };

  const branchDescriptions = {
    visual: 'Visual analogies and diagrams',
    logical: 'Step-by-step logical progression',
    practical: 'Real-world examples and applications',
    theoretical: 'Academic depth and principles',
    simplified: 'Beginner-friendly explanation'
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-4xl max-h-[80vh] overflow-y-auto"
        >
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <GitBranch className="h-6 w-6 text-blue-400" />
                <div>
                  <h2 className="text-xl font-bold text-white">Multiple Explanation Paths</h2>
                  <p className="text-gray-400">Choose the approach that works best for you</p>
                </div>
              </div>
              <GlassButton onClick={onClose} variant="secondary">
                ✕
              </GlassButton>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(branches.branches || {}).map(([branchType, branchData]) => (
                <motion.div
                  key={branchType}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <GlassCard 
                    className="p-4 cursor-pointer hover:border-blue-400/50 transition-colors"
                    onClick={() => onSelectBranch(branchType, branchData.response)}
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <span className="text-2xl">{branchIcons[branchType] || '💡'}</span>
                      <div>
                        <h3 className="text-lg font-semibold text-white capitalize">
                          {branchType}
                        </h3>
                        <p className="text-sm text-gray-400">
                          {branchDescriptions[branchType]}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-300 line-clamp-3 mb-3">
                      {branchData.response.slice(0, 150)}...
                    </div>
                    
                    {branchData.suggested_actions && branchData.suggested_actions.length > 0 && (
                      <div className="text-xs text-blue-400">
                        {branchData.suggested_actions.length} suggested actions
                      </div>
                    )}
                  </GlassCard>
                </motion.div>
              ))}
            </div>

            {branches.adaptive_recommendation && (
              <div className="mt-4 p-3 bg-blue-500/10 border border-blue-400/30 rounded-lg">
                <div className="text-sm text-blue-300">
                  <strong>AI Recommendation:</strong> The <span className="capitalize">
                    {branches.adaptive_recommendation}
                  </span> approach might work best for you based on your learning style.
                </div>
              </div>
            )}
          </GlassCard>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}