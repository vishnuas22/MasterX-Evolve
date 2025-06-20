import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Monitor, 
  Code, 
  PenTool, 
  Video,
  Square,
  Play,
  Pause,
  VolumeX,
  Volume2,
  Settings,
  Users,
  Clock,
  Activity,
  Zap
} from 'lucide-react';
import { api } from '../services/api';

const LiveLearningInterface = ({ userId, onSessionUpdate }) => {
  const [activeSession, setActiveSession] = useState(null);
  const [sessionType, setSessionType] = useState('voice_interaction');
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [voiceActive, setVoiceActive] = useState(false);
  const [screenSharing, setScreenSharing] = useState(false);
  const [codeEnvironment, setCodeEnvironment] = useState({
    code: '',
    language: 'python',
    output: '',
    errors: []
  });
  const [whiteboardElements, setWhiteboardElements] = useState([]);
  const [sessionInsights, setSessionInsights] = useState({});
  
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingTool, setDrawingTool] = useState('pen');

  const sessionTypes = [
    { 
      id: 'voice_interaction', 
      name: 'Voice Interaction', 
      icon: <Mic className="w-5 h-5" />,
      description: 'Real-time voice chat with AI mentor'
    },
    { 
      id: 'screen_sharing', 
      name: 'Screen Sharing', 
      icon: <Monitor className="w-5 h-5" />,
      description: 'Share your screen for guided learning'
    },
    { 
      id: 'live_coding', 
      name: 'Live Coding', 
      icon: <Code className="w-5 h-5" />,
      description: 'Collaborative coding with AI assistance'
    },
    { 
      id: 'interactive_whiteboard', 
      name: 'Interactive Whiteboard', 
      icon: <PenTool className="w-5 h-5" />,
      description: 'Visual learning with digital whiteboard'
    }
  ];

  const createLiveSession = async (type, title, duration = 60) => {
    setIsCreatingSession(true);
    try {
      const response = await api.axiosInstance.post('/live-sessions/create', {
        user_id: userId,
        session_type: type,
        title: title || `${sessionTypes.find(t => t.id === type)?.name} Session`,
        duration_minutes: duration,
        features: {
          ai_mentor: true,
          real_time_feedback: true,
          voice_interaction: type === 'voice_interaction',
          screen_sharing: type === 'screen_sharing',
          collaborative_editing: type === 'live_coding',
          whiteboard: type === 'interactive_whiteboard',
          code_execution: type === 'live_coding'
        }
      });

      setActiveSession(response.data);
      if (onSessionUpdate) {
        onSessionUpdate(response.data);
      }
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setIsCreatingSession(false);
    }
  };

  const endSession = async () => {
    if (!activeSession) return;
    
    try {
      const response = await api.axiosInstance.post(`/live-sessions/${activeSession.session_id}/end`);
      setActiveSession(null);
      setVoiceActive(false);
      setScreenSharing(false);
      setCodeEnvironment({ code: '', language: 'python', output: '', errors: [] });
      setWhiteboardElements([]);
      
      if (onSessionUpdate) {
        onSessionUpdate(null);
      }
    } catch (error) {
      console.error('Error ending session:', error);
    }
  };

  const handleVoiceInteraction = async (audioData) => {
    if (!activeSession || activeSession.session_type !== 'voice_interaction') return;
    
    try {
      const response = await api.axiosInstance.post(`/live-sessions/${activeSession.session_id}/voice`, {
        user_id: userId,
        audio_data: audioData
      });
      
      setSessionInsights(prev => ({
        ...prev,
        voice: response.data
      }));
    } catch (error) {
      console.error('Error handling voice interaction:', error);
    }
  };

  const handleScreenShare = async (screenData) => {
    if (!activeSession || activeSession.session_type !== 'screen_sharing') return;
    
    try {
      const response = await api.axiosInstance.post(`/live-sessions/${activeSession.session_id}/screen-share`, {
        user_id: userId,
        screen_data: screenData
      });
      
      setSessionInsights(prev => ({
        ...prev,
        screen: response.data
      }));
    } catch (error) {
      console.error('Error handling screen share:', error);
    }
  };

  const handleLiveCoding = async (codeUpdate) => {
    if (!activeSession || activeSession.session_type !== 'live_coding') return;
    
    try {
      const response = await api.axiosInstance.post(`/live-sessions/${activeSession.session_id}/code`, {
        user_id: userId,
        code_update: codeUpdate
      });
      
      setCodeEnvironment(prev => ({
        ...prev,
        output: response.data.execution_result?.output || '',
        errors: response.data.execution_result?.errors || []
      }));
      
      setSessionInsights(prev => ({
        ...prev,
        coding: response.data
      }));
    } catch (error) {
      console.error('Error handling live coding:', error);
    }
  };

  const handleWhiteboardUpdate = async (update) => {
    if (!activeSession || activeSession.session_type !== 'interactive_whiteboard') return;
    
    try {
      const response = await api.axiosInstance.post(`/live-sessions/${activeSession.session_id}/whiteboard`, {
        user_id: userId,
        whiteboard_update: update
      });
      
      setSessionInsights(prev => ({
        ...prev,
        whiteboard: response.data
      }));
    } catch (error) {
      console.error('Error handling whiteboard update:', error);
    }
  };

  // Voice interaction controls
  const toggleVoice = () => {
    setVoiceActive(!voiceActive);
    if (!voiceActive) {
      // Start voice recording (simulated)
      handleVoiceInteraction("user_speech_data");
    }
  };

  // Screen sharing controls
  const toggleScreenSharing = async () => {
    setScreenSharing(!screenSharing);
    if (!screenSharing) {
      // Start screen sharing (simulated)
      handleScreenShare("screen_capture_data");
    }
  };

  // Code execution
  const executeCode = () => {
    handleLiveCoding({
      code: codeEnvironment.code,
      language: codeEnvironment.language,
      execute: true,
      change_type: 'execute'
    });
  };

  // Whiteboard drawing
  const startDrawing = (e) => {
    if (!canvasRef.current) return;
    setIsDrawing(true);
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    handleWhiteboardUpdate({
      type: 'draw',
      data: { startX: x, startY: y },
      style: { tool: drawingTool, color: '#ffffff', width: 2 }
    });
  };

  const draw = (e) => {
    if (!isDrawing || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const ctx = canvasRef.current.getContext('2d');
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const SessionCreator = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700/50"
    >
      <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
        <Zap className="w-6 h-6 text-blue-400" />
        Live Learning Sessions
      </h2>
      <p className="text-gray-300 mb-6">
        Choose your premium learning experience with real-time AI mentoring
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {sessionTypes.map((type) => (
          <motion.button
            key={type.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setSessionType(type.id)}
            className={`p-4 rounded-xl border-2 transition-all ${
              sessionType === type.id
                ? 'border-blue-400 bg-blue-500/20'
                : 'border-gray-600 bg-gray-700/50 hover:border-gray-500'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className={`${sessionType === type.id ? 'text-blue-400' : 'text-gray-400'}`}>
                {type.icon}
              </div>
              <h3 className={`font-medium ${sessionType === type.id ? 'text-blue-300' : 'text-white'}`}>
                {type.name}
              </h3>
            </div>
            <p className="text-sm text-gray-400 text-left">
              {type.description}
            </p>
          </motion.button>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => createLiveSession(sessionType)}
        disabled={isCreatingSession}
        className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50"
      >
        {isCreatingSession ? (
          <div className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            Creating Session...
          </div>
        ) : (
          `Start ${sessionTypes.find(t => t.id === sessionType)?.name} Session`
        )}
      </motion.button>
    </motion.div>
  );

  const VoiceInteractionPanel = () => (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <Mic className="w-5 h-5 text-green-400" />
          Voice Interaction
        </h3>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded-full text-xs ${voiceActive ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
            {voiceActive ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-center mb-6">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleVoice}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
            voiceActive 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          {voiceActive ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
        </motion.button>
      </div>

      {sessionInsights.voice && (
        <div className="bg-gray-900/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">AI Mentor Response</h4>
          <p className="text-white text-sm mb-2">{sessionInsights.voice.mentor_response?.text}</p>
          <div className="text-xs text-gray-400">
            Confidence: {Math.round((sessionInsights.voice.mentor_response?.confidence || 0.8) * 100)}%
          </div>
        </div>
      )}
    </div>
  );

  const ScreenSharingPanel = () => (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <Monitor className="w-5 h-5 text-blue-400" />
          Screen Sharing
        </h3>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleScreenSharing}
          className={`px-4 py-2 rounded-lg transition-all ${
            screenSharing 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {screenSharing ? 'Stop Sharing' : 'Start Sharing'}
        </motion.button>
      </div>

      <div className="bg-gray-900/50 rounded-lg p-4 h-48 flex items-center justify-center">
        {screenSharing ? (
          <div className="text-center">
            <Video className="w-12 h-12 text-blue-400 mx-auto mb-2" />
            <p className="text-white">Screen sharing active</p>
            <p className="text-sm text-gray-400">AI is analyzing your screen content</p>
          </div>
        ) : (
          <div className="text-center">
            <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-400">Click "Start Sharing" to begin</p>
          </div>
        )}
      </div>

      {sessionInsights.screen && (
        <div className="mt-4 bg-gray-900/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">AI Analysis</h4>
          <p className="text-white text-sm">{sessionInsights.screen.feedback?.feedback_text}</p>
        </div>
      )}
    </div>
  );

  const LiveCodingPanel = () => (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <Code className="w-5 h-5 text-purple-400" />
          Live Coding
        </h3>
        <div className="flex items-center gap-2">
          <select
            value={codeEnvironment.language}
            onChange={(e) => setCodeEnvironment(prev => ({ ...prev, language: e.target.value }))}
            className="bg-gray-700 text-white px-3 py-1 rounded text-sm"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={executeCode}
            className="px-4 py-1 bg-green-500 hover:bg-green-600 text-white rounded text-sm flex items-center gap-1"
          >
            <Play className="w-3 h-3" />
            Run
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-2">Code Editor</h4>
          <textarea
            value={codeEnvironment.code}
            onChange={(e) => {
              setCodeEnvironment(prev => ({ ...prev, code: e.target.value }));
              handleLiveCoding({
                code: e.target.value,
                language: codeEnvironment.language,
                change_type: 'edit'
              });
            }}
            className="w-full h-48 bg-gray-900 text-white p-3 rounded-lg font-mono text-sm resize-none"
            placeholder="Start coding... AI will provide real-time feedback"
          />
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-2">Output & Feedback</h4>
          <div className="bg-gray-900 rounded-lg p-3 h-48 overflow-y-auto">
            {codeEnvironment.output && (
              <div className="mb-3">
                <h5 className="text-xs text-green-400 mb-1">Output:</h5>
                <pre className="text-white text-sm whitespace-pre-wrap">{codeEnvironment.output}</pre>
              </div>
            )}
            {codeEnvironment.errors.length > 0 && (
              <div className="mb-3">
                <h5 className="text-xs text-red-400 mb-1">Errors:</h5>
                {codeEnvironment.errors.map((error, index) => (
                  <pre key={index} className="text-red-300 text-sm">{error}</pre>
                ))}
              </div>
            )}
            {sessionInsights.coding?.mentor_feedback && (
              <div>
                <h5 className="text-xs text-blue-400 mb-1">AI Mentor:</h5>
                <p className="text-white text-sm">{sessionInsights.coding.mentor_feedback.feedback}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const WhiteboardPanel = () => (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <PenTool className="w-5 h-5 text-yellow-400" />
          Interactive Whiteboard
        </h3>
        <div className="flex items-center gap-2">
          {['pen', 'eraser', 'text'].map((tool) => (
            <motion.button
              key={tool}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setDrawingTool(tool)}
              className={`px-3 py-1 rounded text-sm capitalize ${
                drawingTool === tool 
                  ? 'bg-yellow-500 text-black' 
                  : 'bg-gray-700 text-white hover:bg-gray-600'
              }`}
            >
              {tool}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="w-full bg-gray-900 rounded-lg cursor-crosshair"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
        />
        <div className="absolute top-2 left-2 text-xs text-gray-400">
          Draw, write, or diagram your ideas. AI will provide insights!
        </div>
      </div>

      {sessionInsights.whiteboard && (
        <div className="mt-4 bg-gray-900/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">AI Suggestions</h4>
          <p className="text-white text-sm">{sessionInsights.whiteboard.ai_suggestions?.suggestions}</p>
        </div>
      )}
    </div>
  );

  const ActiveSessionHeader = () => (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-gray-700/50 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <div>
            <h2 className="text-lg font-semibold text-white">{activeSession.title}</h2>
            <p className="text-sm text-gray-400">
              {sessionTypes.find(t => t.id === activeSession.session_type)?.name} • 
              Started {new Date(activeSession.start_time).toLocaleTimeString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-sm text-gray-400">
            <Clock className="w-4 h-4" />
            {Math.round((Date.now() - new Date(activeSession.start_time).getTime()) / 60000)} min
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={endSession}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm"
          >
            End Session
          </motion.button>
        </div>
      </div>
    </div>
  );

  const renderSessionInterface = () => {
    if (!activeSession) return null;

    switch (activeSession.session_type) {
      case 'voice_interaction':
        return <VoiceInteractionPanel />;
      case 'screen_sharing':
        return <ScreenSharingPanel />;
      case 'live_coding':
        return <LiveCodingPanel />;
      case 'interactive_whiteboard':
        return <WhiteboardPanel />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <AnimatePresence mode="wait">
        {!activeSession ? (
          <motion.div
            key="creator"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <SessionCreator />
          </motion.div>
        ) : (
          <motion.div
            key="session"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ActiveSessionHeader />
            {renderSessionInterface()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LiveLearningInterface;