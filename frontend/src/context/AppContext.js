import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { api } from '../services/api';

// Initial state
const initialState = {
  user: null,
  currentSession: null,
  sessions: [],
  messages: [],
  isLoading: false,
  error: null,
  isTyping: false,
  streamingMessage: '',
  darkMode: true,
  progress: {},
  // Gamification state
  gamificationData: null,
  achievements: [],
  streak: null,
  rewards: null
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_USER: 'SET_USER',
  SET_CURRENT_SESSION: 'SET_CURRENT_SESSION',
  SET_SESSIONS: 'SET_SESSIONS',
  ADD_SESSION: 'ADD_SESSION',
  SET_MESSAGES: 'SET_MESSAGES',
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_TYPING: 'SET_TYPING',
  SET_STREAMING_MESSAGE: 'SET_STREAMING_MESSAGE',
  CLEAR_STREAMING_MESSAGE: 'CLEAR_STREAMING_MESSAGE',
  TOGGLE_DARK_MODE: 'TOGGLE_DARK_MODE',
  SET_PROGRESS: 'SET_PROGRESS',
  // Gamification actions
  SET_GAMIFICATION_DATA: 'SET_GAMIFICATION_DATA',
  UPDATE_STREAK: 'UPDATE_STREAK',
  ADD_ACHIEVEMENT: 'ADD_ACHIEVEMENT',
  UPDATE_REWARDS: 'UPDATE_REWARDS'
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false };
    
    case ActionTypes.SET_USER:
      return { ...state, user: action.payload };
    
    case ActionTypes.SET_CURRENT_SESSION:
      return { ...state, currentSession: action.payload };
    
    case ActionTypes.SET_SESSIONS:
      return { ...state, sessions: action.payload };
    
    case ActionTypes.ADD_SESSION:
      return { ...state, sessions: [action.payload, ...state.sessions] };
    
    case ActionTypes.SET_MESSAGES:
      return { ...state, messages: action.payload };
    
    case ActionTypes.ADD_MESSAGE:
      return { ...state, messages: [...state.messages, action.payload] };
    
    case ActionTypes.SET_TYPING:
      return { ...state, isTyping: action.payload };
    
    case ActionTypes.SET_STREAMING_MESSAGE:
      return { ...state, streamingMessage: state.streamingMessage + action.payload };
    
    case ActionTypes.CLEAR_STREAMING_MESSAGE:
      return { ...state, streamingMessage: '' };
    
    case ActionTypes.TOGGLE_DARK_MODE:
      return { ...state, darkMode: !state.darkMode };
    
    case ActionTypes.SET_PROGRESS:
      return { ...state, progress: { ...state.progress, ...action.payload } };
    
    // Gamification reducer cases
    case ActionTypes.SET_GAMIFICATION_DATA:
      return { 
        ...state, 
        gamificationData: action.payload,
        achievements: action.payload?.achievements?.details || [],
        streak: action.payload?.streak || null,
        rewards: action.payload?.rewards || null
      };
    
    case ActionTypes.UPDATE_STREAK:
      return { 
        ...state, 
        streak: { ...state.streak, ...action.payload }
      };
    
    case ActionTypes.ADD_ACHIEVEMENT:
      return {
        ...state,
        achievements: [...state.achievements, action.payload]
      };
    
    case ActionTypes.UPDATE_REWARDS:
      return {
        ...state,
        rewards: { ...state.rewards, ...action.payload }
      };
    
    default:
      return state;
  }
}

// Context
const AppContext = createContext();

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions
  const actions = {
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    
    setUser: (user) => dispatch({ type: ActionTypes.SET_USER, payload: user }),
    
    setCurrentSession: (session) => dispatch({ type: ActionTypes.SET_CURRENT_SESSION, payload: session }),
    
    setSessions: (sessions) => dispatch({ type: ActionTypes.SET_SESSIONS, payload: sessions }),
    
    addSession: (session) => dispatch({ type: ActionTypes.ADD_SESSION, payload: session }),
    
    setMessages: (messages) => dispatch({ type: ActionTypes.SET_MESSAGES, payload: messages }),
    
    addMessage: (message) => dispatch({ type: ActionTypes.ADD_MESSAGE, payload: message }),
    
    setTyping: (typing) => dispatch({ type: ActionTypes.SET_TYPING, payload: typing }),
    
    setStreamingMessage: (content) => dispatch({ type: ActionTypes.SET_STREAMING_MESSAGE, payload: content }),
    
    clearStreamingMessage: () => dispatch({ type: ActionTypes.CLEAR_STREAMING_MESSAGE }),
    
    toggleDarkMode: () => dispatch({ type: ActionTypes.TOGGLE_DARK_MODE }),
    
    setProgress: (progress) => dispatch({ type: ActionTypes.SET_PROGRESS, payload: progress }),

    // API Actions
    async healthCheck() {
      try {
        const response = await api.healthCheck();
        return response;
      } catch (error) {
        actions.setError('Unable to connect to MasterX AI Mentor System');
        throw error;
      }
    },

    async createUser(userData) {
      try {
        actions.setLoading(true);
        const user = await api.createUser(userData);
        actions.setUser(user);
        return user;
      } catch (error) {
        actions.setError(error.message);
        throw error;
      } finally {
        actions.setLoading(false);
      }
    },

    async getUserByEmail(email) {
      try {
        const user = await api.getUserByEmail(email);
        return user;
      } catch (error) {
        actions.setError(error.message);
        throw error;
      }
    },

    async createSession(sessionData) {
      try {
        actions.setLoading(true);
        const session = await api.createSession(sessionData);
        actions.addSession(session);
        actions.setCurrentSession(session);
        actions.setMessages([]); // Clear messages for new session
        return session;
      } catch (error) {
        actions.setError(error.message);
        throw error;
      } finally {
        actions.setLoading(false);
      }
    },

    async loadUserSessions(userId) {
      try {
        const sessions = await api.getUserSessions(userId);
        actions.setSessions(sessions);
        return sessions;
      } catch (error) {
        actions.setError(error.message);
        throw error;
      }
    },

    async loadSessionMessages(sessionId) {
      try {
        const messages = await api.getSessionMessages(sessionId);
        actions.setMessages(messages);
        return messages;
      } catch (error) {
        actions.setError(error.message);
        throw error;
      }
    },

    async sendMessage(sessionId, message) {
      try {
        // Add user message immediately
        const userMessage = {
          id: Date.now().toString(),
          session_id: sessionId,
          message: message,
          sender: 'user',
          timestamp: new Date().toISOString()
        };
        actions.addMessage(userMessage);

        // Set up streaming
        actions.setTyping(true);
        actions.clearStreamingMessage();

        // Call streaming API
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            user_message: message
          })
        });

        if (!response.ok) {
          throw new Error('Failed to send message');
        }

        const reader = response.body.getReader();
        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'chunk' && data.content) {
                  fullResponse += data.content;
                  actions.setStreamingMessage(data.content);
                } else if (data.type === 'complete') {
                  actions.setTyping(false);
                  
                  // Add the complete AI response
                  const aiMessage = {
                    id: (Date.now() + 1).toString(),
                    session_id: sessionId,
                    message: fullResponse,
                    sender: 'mentor',
                    timestamp: new Date().toISOString(),
                    suggestions: data.suggestions || []
                  };
                  actions.addMessage(aiMessage);
                  actions.clearStreamingMessage();
                } else if (data.type === 'error') {
                  actions.setTyping(false);
                  actions.setError(data.message);
                  actions.clearStreamingMessage();
                }
              } catch (e) {
                console.error('Error parsing streaming data:', e);
              }
            }
          }
        }

        return fullResponse;
      } catch (error) {
        actions.setTyping(false);
        actions.clearStreamingMessage();
        actions.setError(error.message);
        throw error;
      }
    },

    async sendPremiumMessage(sessionId, message, context = {}) {
      try {
        // Add user message immediately
        const userMessage = {
          id: Date.now().toString(),
          session_id: sessionId,
          message: message,
          sender: 'user',
          timestamp: new Date().toISOString()
        };
        actions.addMessage(userMessage);

        // Set up streaming
        actions.setTyping(true);
        actions.clearStreamingMessage();

        // Call premium streaming API
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/premium/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            user_message: message,
            context: context
          })
        });

        if (!response.ok) {
          throw new Error('Failed to send premium message');
        }

        const reader = response.body.getReader();
        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'chunk' && data.content) {
                  fullResponse += data.content;
                  actions.setStreamingMessage(data.content);
                } else if (data.type === 'complete') {
                  actions.setTyping(false);
                  
                  // Add the complete AI response with premium features
                  const aiMessage = {
                    id: (Date.now() + 1).toString(),
                    session_id: sessionId,
                    message: fullResponse,
                    sender: 'mentor',
                    timestamp: new Date().toISOString(),
                    suggestions: data.suggestions || [],
                    next_steps: data.next_steps,
                    learning_mode: data.mode || context.learning_mode
                  };
                  actions.addMessage(aiMessage);
                  actions.clearStreamingMessage();
                } else if (data.type === 'error') {
                  actions.setTyping(false);
                  actions.setError(data.message);
                  actions.clearStreamingMessage();
                }
              } catch (e) {
                console.error('Error parsing premium streaming data:', e);
              }
            }
          }
        }

        return fullResponse;
      } catch (error) {
        actions.setTyping(false);
        actions.clearStreamingMessage();
        actions.setError(error.message);
        throw error;
      }
    },

    // Gamification actions
    setGamificationData: (data) => dispatch({ type: ActionTypes.SET_GAMIFICATION_DATA, payload: data }),
    
    updateStreak: (streak) => dispatch({ type: ActionTypes.UPDATE_STREAK, payload: streak }),
    
    addAchievement: (achievement) => dispatch({ type: ActionTypes.ADD_ACHIEVEMENT, payload: achievement }),
    
    updateRewards: (rewards) => dispatch({ type: ActionTypes.UPDATE_REWARDS, payload: rewards }),

    async loadGamificationData(userId) {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/${userId}/gamification`);
        const data = await response.json();
        actions.setGamificationData(data);
        return data;
      } catch (error) {
        console.error('Error loading gamification data:', error);
        actions.setError('Failed to load gamification data');
      }
    },

    async recordSessionCompletion(userId, sessionId, context = {}) {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/users/${userId}/gamification/session-complete`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: sessionId,
              context: context
            })
          }
        );
        
        const result = await response.json();
        
        // Update local state with new data
        if (result.streak) {
          actions.updateStreak(result.streak);
        }
        if (result.points) {
          actions.updateRewards(result.points);
        }
        if (result.new_achievements) {
          result.new_achievements.forEach(achievement => {
            actions.addAchievement(achievement);
          });
        }
        
        return result;
      } catch (error) {
        console.error('Error recording session completion:', error);
        actions.setError('Failed to record session completion');
      }
    },

    async recordConceptMastery(userId, concept, subject, difficulty = 'medium') {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/users/${userId}/gamification/concept-mastered`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              concept,
              subject,
              difficulty,
              first_time: true
            })
          }
        );
        
        const result = await response.json();
        
        // Update local state
        if (result.points) {
          actions.updateRewards(result.points);
        }
        if (result.new_achievements) {
          result.new_achievements.forEach(achievement => {
            actions.addAchievement(achievement);
          });
        }
        
        return result;
      } catch (error) {
        console.error('Error recording concept mastery:', error);
        actions.setError('Failed to record concept mastery');
      }
    }
  };

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('masterx_user');
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser);
        actions.setUser(user);
        actions.loadUserSessions(user.id);
      } catch (error) {
        console.error('Error loading saved user:', error);
        localStorage.removeItem('masterx_user');
      }
    }
  }, []);

  // Save user to localStorage when user changes
  useEffect(() => {
    if (state.user) {
      localStorage.setItem('masterx_user', JSON.stringify(state.user));
    } else {
      localStorage.removeItem('masterx_user');
    }
  }, [state.user]);

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export { ActionTypes };
