import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  MessageSquare, 
  Settings, 
  User, 
  BookOpen, 
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Target,
  Brain
} from 'lucide-react';
import { GlassCard, GlassButton } from './GlassCard';
import { useApp } from '../context/AppContext';

export function Sidebar({ isCollapsed, onToggle }) {
  const { state, actions } = useApp();
  const [showNewSessionForm, setShowNewSessionForm] = useState(false);

  const handleNewSession = async () => {
    if (!state.user) return;
    
    try {
      await actions.createSession({
        user_id: state.user.id,
        subject: "General Learning",
        difficulty_level: "beginner"
      });
      setShowNewSessionForm(false);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleSessionSelect = async (session) => {
    actions.setCurrentSession(session);
    await actions.loadSessionMessages(session.id);
  };

  const handleNavigationClick = (action) => {
    // Handle navigation based on the action
    console.log(`Navigating to: ${action}`);
    // TODO: Implement actual navigation logic
    switch (action) {
      case 'learning-paths':
        // Navigate to learning paths
        actions.setError(null); // Clear any errors
        console.log('Opening Learning Paths');
        break;
      case 'progress':
        // Navigate to progress view
        console.log('Opening Progress View');
        break;
      case 'goals':
        // Navigate to goals
        console.log('Opening Goals');
        break;
      case 'achievements':
        // Navigate to achievements
        console.log('Opening Achievements');
        break;
      default:
        console.log(`Unknown action: ${action}`);
    }
  };

  const handleSettingsClick = () => {
    console.log('Opening Settings');
    // TODO: Implement settings modal or navigation
  };

  const handleLogout = () => {
    console.log('Logging out');
    // TODO: Implement logout functionality
    if (window.confirm('Are you sure you want to logout?')) {
      actions.setUser(null);
      actions.setCurrentSession(null);
      actions.setSessions([]);
      actions.setMessages([]);
      localStorage.removeItem('masterx_user');
    }
  };

  return (
    <div className={`relative transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-80'}`}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-6 z-10 p-1 rounded-full bg-gray-800 border border-white/20 text-gray-300 hover:text-white transition-colors"
      >
        {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      <div className="h-full border-r border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="p-4 h-full flex flex-col">
          {/* Logo/Brand */}
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500">
              <Brain className="h-6 w-6 text-white" />
            </div>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex-1"
              >
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  MasterX
                </h1>
                <p className="text-xs text-gray-400">AI Learning Mentor</p>
              </motion.div>
            )}
          </div>

          {/* New Session Button */}
          <div className="mb-6">
            <GlassButton
              onClick={handleNewSession}
              className={`${isCollapsed ? 'w-12 h-12 p-0' : 'w-full'} justify-center`}
              disabled={!state.user}
            >
              <Plus className="h-4 w-4" />
              {!isCollapsed && <span className="ml-2">New Session</span>}
            </GlassButton>
          </div>

          {/* Sessions List */}
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-2 mb-6 flex-1 overflow-hidden"
            >
              <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Sessions</h3>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {state.sessions.map((session) => (
                  <motion.button
                    key={session.id}
                    onClick={() => handleSessionSelect(session)}
                    className={`w-full text-left p-3 rounded-xl transition-all duration-300 ${
                      state.currentSession?.id === session.id
                        ? 'bg-blue-500/20 border border-blue-400/30'
                        : 'bg-white/5 border border-white/10 hover:bg-white/10'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="h-4 w-4 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-200 truncate">
                          {session.subject || 'General Learning'}
                        </p>
                        <p className="text-xs text-gray-400 truncate">
                          {session.difficulty_level} • {new Date(session.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Navigation Items */}
          <div className="space-y-2 mb-20">
            {[
              { icon: BookOpen, label: 'Learning Paths', badge: null, action: 'learning-paths' },
              { icon: TrendingUp, label: 'Progress', badge: '3', action: 'progress' },
              { icon: Target, label: 'Goals', badge: null, action: 'goals' },
              { icon: Sparkles, label: 'Achievements', badge: '2', action: 'achievements' },
            ].map((item, index) => (
              <motion.button
                key={item.label}
                onClick={() => handleNavigationClick(item.action)}
                className={`${
                  isCollapsed ? 'w-12 h-12 p-0' : 'w-full px-3 py-2'
                } flex items-center justify-center rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300 text-gray-300 hover:text-white cursor-pointer relative z-10`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="ml-3 flex-1 text-left text-sm">{item.label}</span>
                    {item.badge && (
                      <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-0.5 ml-2 flex-shrink-0">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* User Profile */}
        {!isCollapsed && state.user && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute bottom-4 left-4 right-4 z-20"
          >
            <GlassCard className="p-3">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-200 truncate">
                    {state.user.name}
                  </p>
                  <p className="text-xs text-gray-400 truncate">
                    {state.user.email}
                  </p>
                </div>
                <div className="flex space-x-1 flex-shrink-0">
                  <button 
                    onClick={handleSettingsClick}
                    className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                    title="Settings"
                  >
                    <Settings className="h-4 w-4 text-gray-400 hover:text-white" />
                  </button>
                  <button 
                    onClick={handleLogout}
                    className="p-1.5 rounded-lg hover:bg-red-500/20 transition-colors"
                    title="Logout"
                  >
                    <svg className="h-4 w-4 text-gray-400 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>
    </div>
  );
}
