import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, Target, Flame, Star, Users, Award, TrendingUp, 
  Zap, Crown, Sparkles, BarChart3, Calendar
} from 'lucide-react';
import { GlassCard, GlassButton } from './GlassCard';
import { useApp } from '../context/AppContext';

export function GamificationDashboard({ isVisible, onClose }) {
  const { state, actions } = useApp();
  const [gamificationData, setGamificationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [celebrationMode, setCelebrationMode] = useState(false);

  useEffect(() => {
    if (isVisible && state.user) {
      loadGamificationData();
    }
  }, [isVisible, state.user]);

  const loadGamificationData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/${state.user.id}/gamification`);
      const data = await response.json();
      setGamificationData(data);
    } catch (error) {
      console.error('Error loading gamification data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSessionComplete = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/users/${state.user.id}/gamification/session-complete`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: state.currentSession?.id,
            context: { subject: state.currentSession?.subject }
          })
        }
      );
      
      const result = await response.json();
      
      // Show celebration for achievements or level up
      if (result.new_achievements?.length > 0 || result.points?.level_up) {
        setCelebrationMode(true);
        setTimeout(() => setCelebrationMode(false), 3000);
      }
      
      // Reload data to show updates
      await loadGamificationData();
      
      return result;
    } catch (error) {
      console.error('Error recording session completion:', error);
    }
  };

  if (!isVisible) return null;

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
          className="w-full max-w-6xl h-[90vh] overflow-y-auto"
        >
          <GlassCard className="p-6 h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Trophy className="h-8 w-8 text-yellow-400" />
                  {celebrationMode && (
                    <motion.div
                      className="absolute -inset-2"
                      animate={{ 
                        scale: [1, 1.2, 1],
                        rotate: [0, 5, -5, 0]
                      }}
                      transition={{ 
                        duration: 0.5,
                        repeat: Infinity,
                        repeatType: "reverse"
                      }}
                    >
                      <Sparkles className="h-12 w-12 text-yellow-300" />
                    </motion.div>
                  )}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Learning Progress</h2>
                  <p className="text-gray-400">Track your achievements and growth</p>
                </div>
              </div>
              <GlassButton onClick={onClose} variant="secondary">
                ✕
              </GlassButton>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Stats */}
                <div className="lg:col-span-1 space-y-4">
                  <LearningStreakCard 
                    streak={gamificationData?.streak} 
                    onSessionComplete={handleSessionComplete}
                  />
                  <RewardSystemCard rewards={gamificationData?.rewards} />
                  <StudyGroupsCard groups={gamificationData?.study_groups} />
                </div>

                {/* Middle Column - Achievements */}
                <div className="lg:col-span-1">
                  <AchievementsPanel 
                    achievements={gamificationData?.achievements}
                    celebrationMode={celebrationMode}
                  />
                </div>

                {/* Right Column - Analytics */}
                <div className="lg:col-span-1 space-y-4">
                  <MotivationProfileCard 
                    profile={gamificationData?.motivation_profile}
                  />
                  <NextMilestonesCard 
                    milestones={gamificationData?.next_milestones}
                  />
                </div>
              </div>
            )}
          </GlassCard>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

function LearningStreakCard({ streak, onSessionComplete }) {
  if (!streak) return null;

  const streakEmoji = streak.current_streak >= 30 ? '💎' : 
                     streak.current_streak >= 7 ? '🔥' : '⚡';

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Flame className="h-5 w-5 text-orange-400" />
          <span>Learning Streak</span>
        </h3>
        <span className="text-2xl">{streakEmoji}</span>
      </div>
      
      <div className="space-y-3">
        <div className="text-center">
          <div className="text-3xl font-bold text-orange-400">
            {streak.current_streak}
          </div>
          <div className="text-sm text-gray-400">Days in a row</div>
        </div>
        
        <div className="flex justify-between text-sm">
          <div>
            <div className="text-white font-medium">{streak.longest_streak}</div>
            <div className="text-gray-400">Best streak</div>
          </div>
          <div>
            <div className="text-white font-medium">{streak.total_learning_days}</div>
            <div className="text-gray-400">Total days</div>
          </div>
          <div>
            <div className="text-white font-medium">{streak.freeze_count}</div>
            <div className="text-gray-400">Freezes left</div>
          </div>
        </div>

        <GlassButton 
          onClick={onSessionComplete}
          className="w-full"
          size="sm"
        >
          <Target className="h-4 w-4 mr-2" />
          Complete Session
        </GlassButton>
      </div>
    </GlassCard>
  );
}

function RewardSystemCard({ rewards }) {
  if (!rewards) return null;

  const progressPercentage = ((rewards.points_to_next_level || 100) - rewards.experience_points) / (rewards.points_to_next_level || 100) * 100;

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Star className="h-5 w-5 text-yellow-400" />
          <span>Level & Points</span>
        </h3>
        <Crown className="h-5 w-5 text-yellow-400" />
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold text-yellow-400">
              Level {rewards.level}
            </div>
            <div className="text-sm text-gray-400">
              {rewards.total_points.toLocaleString()} total points
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-semibold text-white">
              {rewards.experience_points}
            </div>
            <div className="text-sm text-gray-400">
              / {rewards.points_to_next_level || 100} XP
            </div>
          </div>
        </div>
        
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Progress to Level {rewards.level + 1}</span>
            <span>{Math.round(100 - progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-yellow-400 to-orange-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${100 - progressPercentage}%` }}
              transition={{ duration: 1 }}
            />
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

function StudyGroupsCard({ groups }) {
  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Users className="h-5 w-5 text-purple-400" />
          <span>Study Groups</span>
        </h3>
      </div>
      
      <div className="space-y-2">
        {groups && groups.length > 0 ? (
          groups.slice(0, 3).map((group, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
              <div>
                <div className="text-sm font-medium text-white">{group.name}</div>
                <div className="text-xs text-gray-400">{group.members?.length || 0} members</div>
              </div>
              <div className="text-xs text-purple-400">{group.subject}</div>
            </div>
          ))
        ) : (
          <div className="text-center py-4">
            <Users className="h-8 w-8 text-gray-500 mx-auto mb-2" />
            <div className="text-sm text-gray-400">No study groups yet</div>
            <GlassButton size="sm" className="mt-2">
              Create Group
            </GlassButton>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

function AchievementsPanel({ achievements, celebrationMode }) {
  if (!achievements) return null;

  const { unlocked_count, total_count, details } = achievements;
  const unlockedAchievements = Object.values(details || {}).filter(a => a.unlocked);
  const nearbyAchievements = Object.values(details || {})
    .filter(a => !a.unlocked && a.progress > 0)
    .sort((a, b) => b.progress - a.progress)
    .slice(0, 3);

  return (
    <GlassCard className="p-4 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Award className="h-5 w-5 text-blue-400" />
          <span>Achievements</span>
        </h3>
        <div className="text-sm text-gray-400">
          {unlocked_count} / {total_count}
        </div>
      </div>
      
      <div className="space-y-4 h-full overflow-y-auto">
        {/* Recently Unlocked */}
        {unlockedAchievements.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Unlocked</h4>
            <div className="space-y-2">
              {unlockedAchievements.slice(0, 3).map((achievement, index) => (
                <motion.div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    celebrationMode ? 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-400/30' 
                    : 'bg-green-500/10 border-green-400/30'
                  }`}
                  animate={celebrationMode ? { scale: [1, 1.02, 1] } : {}}
                  transition={{ duration: 0.5, repeat: celebrationMode ? Infinity : 0 }}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{achievement.achievement.icon}</span>
                    <div className="flex-1">
                      <div className="font-medium text-white text-sm">
                        {achievement.achievement.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {achievement.achievement.description}
                      </div>
                      <div className="text-xs text-green-400 mt-1">
                        +{achievement.achievement.points_reward} points
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* In Progress */}
        {nearbyAchievements.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">In Progress</h4>
            <div className="space-y-2">
              {nearbyAchievements.map((achievement, index) => (
                <div key={index} className="p-3 bg-white/5 rounded-lg border border-white/10">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl opacity-50">{achievement.achievement.icon}</span>
                    <div className="flex-1">
                      <div className="font-medium text-white text-sm">
                        {achievement.achievement.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {achievement.achievement.description}
                      </div>
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(achievement.progress)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div
                            className="bg-blue-400 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${achievement.progress}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

function MotivationProfileCard({ profile }) {
  if (!profile) return null;

  const motivationEmojis = {
    achiever: '🎯',
    socializer: '👥',
    explorer: '🔍',
    competitor: '🏆'
  };

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-cyan-400" />
          <span>Learning Style</span>
        </h3>
        <span className="text-2xl">
          {motivationEmojis[profile.primary_motivation] || '🎯'}
        </span>
      </div>
      
      <div className="space-y-3">
        <div>
          <div className="text-lg font-medium text-white capitalize">
            {profile.primary_motivation}
          </div>
          <div className="text-sm text-gray-400">
            Primary learning motivation
          </div>
        </div>
        
        <div className="space-y-2">
          {Object.entries(profile.scores || {}).map(([type, score]) => (
            <div key={type}>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span className="capitalize">{type}</span>
                <span>{score}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1">
                <div
                  className="bg-cyan-400 h-1 rounded-full transition-all duration-500"
                  style={{ width: `${(score / Math.max(...Object.values(profile.scores || {}))) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </GlassCard>
  );
}

function NextMilestonesCard({ milestones }) {
  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <TrendingUp className="h-5 w-5 text-green-400" />
          <span>Next Goals</span>
        </h3>
      </div>
      
      <div className="space-y-3">
        {milestones && milestones.length > 0 ? (
          milestones.slice(0, 3).map((milestone, index) => (
            <div key={index} className="p-3 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-lg">{milestone.achievement.icon}</span>
                <div className="flex-1">
                  <div className="font-medium text-white text-sm">
                    {milestone.achievement.name}
                  </div>
                  <div className="mt-1">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(milestone.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full transition-all duration-500 ${
                          milestone.priority === 'high' ? 'bg-green-400' :
                          milestone.priority === 'medium' ? 'bg-yellow-400' : 'bg-blue-400'
                        }`}
                        style={{ width: `${milestone.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-4">
            <Target className="h-8 w-8 text-gray-500 mx-auto mb-2" />
            <div className="text-sm text-gray-400">Complete more sessions to unlock goals</div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}