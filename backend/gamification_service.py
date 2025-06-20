"""
Intelligent Gamification Service for MasterX
Handles adaptive rewards, learning streaks, achievements, and virtual study groups
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

from models import (
    Achievement, UserAchievement, LearningStreak, RewardSystem, StudyGroup, GroupActivity,
    ChatSession, User
)
from database import db_service

logger = logging.getLogger(__name__)

class GamificationService:
    """Intelligent gamification system with adaptive rewards"""
    
    def __init__(self):
        self.achievement_templates = []
        self.motivation_profiles = {
            "achiever": {"points_multiplier": 1.5, "prefers": "achievements"},
            "socializer": {"points_multiplier": 1.2, "prefers": "group_activities"},
            "explorer": {"points_multiplier": 1.3, "prefers": "new_topics"},
            "competitor": {"points_multiplier": 1.4, "prefers": "challenges"}
        }
        
    async def initialize_achievements(self):
        """Initialize default achievement system"""
        default_achievements = [
            # Learning Achievements
            Achievement(
                name="First Steps",
                description="Complete your first learning session",
                icon="🎯",
                category="learning",
                requirement_type="session_count",
                requirement_value=1,
                points_reward=50,
                badge_color="green"
            ),
            Achievement(
                name="Knowledge Seeker",
                description="Complete 10 learning sessions",
                icon="📚",
                category="learning",
                requirement_type="session_count",
                requirement_value=10,
                points_reward=200,
                badge_color="blue"
            ),
            Achievement(
                name="Learning Master",
                description="Complete 50 learning sessions",
                icon="🏆",
                category="learning",
                requirement_type="session_count",
                requirement_value=50,
                points_reward=1000,
                badge_color="gold",
                is_premium=True
            ),
            # Streak Achievements
            Achievement(
                name="Consistency Champion",
                description="Maintain a 7-day learning streak",
                icon="🔥",
                category="streak",
                requirement_type="streak_days",
                requirement_value=7,
                points_reward=300,
                badge_color="orange"
            ),
            Achievement(
                name="Dedication Diamond",
                description="Maintain a 30-day learning streak",
                icon="💎",
                category="streak",
                requirement_type="streak_days",
                requirement_value=30,
                points_reward=1500,
                badge_color="purple",
                is_premium=True
            ),
            # Milestone Achievements
            Achievement(
                name="Concept Collector",
                description="Master 25 concepts across any subject",
                icon="🧠",
                category="milestone",
                requirement_type="concepts_mastered",
                requirement_value=25,
                points_reward=500,
                badge_color="cyan"
            ),
            Achievement(
                name="Expert Explorer",
                description="Master 100 concepts across any subject",
                icon="🌟",
                category="milestone",
                requirement_type="concepts_mastered",
                requirement_value=100,
                points_reward=2500,
                badge_color="gold",
                is_premium=True
            ),
            # Collaboration Achievements
            Achievement(
                name="Team Player",
                description="Join your first study group",
                icon="👥",
                category="collaboration",
                requirement_type="groups_joined",
                requirement_value=1,
                points_reward=150,
                badge_color="pink"
            ),
            Achievement(
                name="Community Builder",
                description="Create a study group with 5+ members",
                icon="🏗️",
                category="collaboration",
                requirement_type="group_members_recruited",
                requirement_value=5,
                points_reward=750,
                badge_color="purple",
                is_premium=True
            )
        ]
        
        # Create achievements if they don't exist
        existing_achievements = await db_service.get_achievements()
        existing_names = {ach.name for ach in existing_achievements}
        
        for achievement in default_achievements:
            if achievement.name not in existing_names:
                await db_service.create_achievement(achievement)
                
        self.achievement_templates = await db_service.get_achievements()
        logger.info(f"Initialized {len(self.achievement_templates)} achievements")
    
    async def analyze_user_motivation(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior to determine motivation profile"""
        # Get user's activity history
        sessions = await db_service.get_user_sessions(user_id, active_only=False)
        achievements = await db_service.get_user_achievements(user_id)
        groups = await db_service.get_study_groups(user_id)
        
        # Simple heuristic analysis
        motivation_scores = {
            "achiever": 0,
            "socializer": 0,
            "explorer": 0,
            "competitor": 0
        }
        
        # Analyze session patterns
        if len(sessions) > 10:
            motivation_scores["achiever"] += 2
        
        # Analyze group participation
        if len(groups) > 0:
            motivation_scores["socializer"] += 3
            
        # Analyze subject diversity
        subjects = set(session.subject for session in sessions if session.subject)
        if len(subjects) > 3:
            motivation_scores["explorer"] += 2
            
        # Analyze challenge-seeking behavior (simplified)
        challenge_sessions = [s for s in sessions if s.difficulty_level == "advanced"]
        if len(challenge_sessions) > len(sessions) * 0.3:
            motivation_scores["competitor"] += 2
        
        # Default to achiever if no clear pattern
        dominant_type = max(motivation_scores, key=motivation_scores.get)
        if motivation_scores[dominant_type] == 0:
            dominant_type = "achiever"
            
        return {
            "primary_motivation": dominant_type,
            "scores": motivation_scores,
            "profile": self.motivation_profiles[dominant_type]
        }
    
    async def update_learning_streak(self, user_id: str, session_date: datetime = None) -> Dict[str, Any]:
        """Update user's learning streak with smart recovery mechanisms"""
        if not session_date:
            session_date = datetime.utcnow()
            
        streak = await db_service.get_or_create_streak(user_id)
        
        # Calculate days since last activity
        if streak.last_activity_date:
            days_diff = (session_date.date() - streak.last_activity_date.date()).days
        else:
            days_diff = 0
            
        updates = {}
        streak_broken = False
        streak_extended = False
        
        if not streak.last_activity_date or days_diff == 1:
            # Continue or start streak
            updates["current_streak"] = streak.current_streak + 1
            updates["total_learning_days"] = streak.total_learning_days + 1
            streak_extended = True
            
            if updates["current_streak"] > streak.longest_streak:
                updates["longest_streak"] = updates["current_streak"]
                
        elif days_diff == 0:
            # Same day activity - no streak change but update total days
            pass
            
        elif days_diff == 2 and streak.freeze_count > 0:
            # Use streak freeze (recovery mechanism)
            updates["freeze_count"] = streak.freeze_count - 1
            updates["total_learning_days"] = streak.total_learning_days + 1
            # Streak continues
            
        else:
            # Streak broken
            if streak.current_streak > 0:
                streak_broken = True
            updates["current_streak"] = 1
            updates["total_learning_days"] = streak.total_learning_days + 1
            
        updates["last_activity_date"] = session_date
        updates["updated_at"] = datetime.utcnow()
        
        await db_service.update_streak(user_id, updates)
        
        return {
            "streak_broken": streak_broken,
            "streak_extended": streak_extended,
            "current_streak": updates.get("current_streak", streak.current_streak),
            "freeze_used": "freeze_count" in updates and updates["freeze_count"] < streak.freeze_count
        }
    
    async def award_adaptive_points(self, user_id: str, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Award points based on user's motivation profile and action context"""
        motivation = await self.analyze_user_motivation(user_id)
        reward_system = await db_service.get_or_create_reward_system(user_id)
        
        # Base points for different actions
        base_points = {
            "session_complete": 50,
            "concept_mastered": 25,
            "exercise_correct": 15,
            "streak_day": 30,
            "achievement_unlock": 100,
            "group_participation": 20,
            "help_given": 35
        }
        
        points = base_points.get(action, 0)
        
        # Apply motivation-based multiplier
        multiplier = motivation["profile"]["points_multiplier"]
        points = int(points * multiplier)  # Ensure points is an integer
        
        # Context-based bonuses
        if context:
            if context.get("difficulty") == "advanced":
                points = int(points * 1.3)
            if context.get("first_time"):
                points = int(points * 1.5)
            if context.get("streak_milestone"):
                points = int(points * 2.0)
                
        # Update reward system
        new_total = reward_system.total_points + points
        new_exp = reward_system.experience_points + points
        new_level = reward_system.level
        
        # Level up calculation
        points_needed = 100 * (new_level ** 1.5)  # Exponential scaling
        while new_exp >= points_needed:
            new_exp -= int(points_needed)
            new_level += 1
            points_needed = 100 * (new_level ** 1.5)
            
        updates = {
            "total_points": new_total,
            "experience_points": new_exp,
            "level": new_level,
            "points_to_next_level": int(points_needed - new_exp),
            "updated_at": datetime.utcnow()
        }
        
        # Add to reward history
        reward_entry = {
            "action": action,
            "points": points,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        # Get current history and append
        current_history = reward_system.reward_history or []
        current_history.append(reward_entry)
        # Keep only last 100 entries
        updates["reward_history"] = current_history[-100:]
        
        await db_service.update_reward_system(user_id, updates)
        
        level_up = new_level > reward_system.level
        
        return {
            "points_awarded": points,
            "total_points": new_total,
            "level": new_level,
            "level_up": level_up,
            "next_level_progress": (new_exp / points_needed) * 100
        }
    
    async def check_achievement_unlocks(self, user_id: str, context: Dict[str, Any] = None) -> List[Achievement]:
        """Check and unlock any achievements the user has earned"""
        user_achievements = await db_service.get_user_achievements(user_id)
        unlocked_achievement_ids = {ua.achievement_id for ua in user_achievements}
        
        newly_unlocked = []
        
        for achievement in self.achievement_templates:
            if achievement.id in unlocked_achievement_ids:
                continue
                
            if await self._check_achievement_requirement(user_id, achievement, context):
                # Unlock achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress_when_unlocked=context or {}
                )
                
                await db_service.unlock_achievement(user_achievement)
                newly_unlocked.append(achievement)
                
                # Award points for achievement
                await self.award_adaptive_points(
                    user_id, 
                    "achievement_unlock", 
                    {"achievement_name": achievement.name, "points": achievement.points_reward}
                )
                
        return newly_unlocked
    
    async def _check_achievement_requirement(self, user_id: str, achievement: Achievement, context: Dict[str, Any] = None) -> bool:
        """Check if user meets achievement requirements"""
        if achievement.requirement_type == "session_count":
            sessions = await db_service.get_user_sessions(user_id, active_only=False)
            return len(sessions) >= achievement.requirement_value
            
        elif achievement.requirement_type == "streak_days":
            streak = await db_service.get_or_create_streak(user_id)
            return streak.current_streak >= achievement.requirement_value
            
        elif achievement.requirement_type == "concepts_mastered":
            progress_list = await db_service.get_user_progress(user_id)
            total_concepts = sum(len(p.concepts_mastered) for p in progress_list)
            return total_concepts >= achievement.requirement_value
            
        elif achievement.requirement_type == "groups_joined":
            groups = await db_service.get_study_groups(user_id)
            return len(groups) >= achievement.requirement_value
            
        return False
    
    async def create_ai_facilitated_study_group(self, admin_id: str, subject: str, description: str) -> StudyGroup:
        """Create an AI-facilitated study group"""
        study_group = StudyGroup(
            name=f"AI-Guided {subject} Study Group",
            description=description,
            subject=subject,
            admin_id=admin_id,
            members=[admin_id],
            ai_facilitator_active=True,
            group_goals=[
                f"Master core concepts in {subject}",
                "Support each other's learning journey",
                "Participate in AI-guided discussions"
            ]
        )
        
        return await db_service.create_study_group(study_group)
    
    async def generate_group_activity(self, group_id: str, user_id: str, activity_type: str, content: str) -> GroupActivity:
        """Generate and save group activity"""
        activity = GroupActivity(
            group_id=group_id,
            user_id=user_id,
            activity_type=activity_type,
            content=content,
            metadata={
                "ai_facilitated": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return await db_service.add_group_activity(activity)
    
    async def get_user_gamification_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification status for user"""
        # Get all gamification data
        streak = await db_service.get_or_create_streak(user_id)
        reward_system = await db_service.get_or_create_reward_system(user_id)
        achievements = await db_service.get_user_achievements(user_id)
        groups = await db_service.get_study_groups(user_id)
        motivation = await self.analyze_user_motivation(user_id)
        
        # Get achievement details
        all_achievements = await db_service.get_achievements()
        achievement_details = {}
        for ach in all_achievements:
            is_unlocked = any(ua.achievement_id == ach.id for ua in achievements)
            achievement_details[ach.id] = {
                "achievement": ach.dict(),
                "unlocked": is_unlocked,
                "progress": await self._get_achievement_progress(user_id, ach) if not is_unlocked else 100
            }
        
        return {
            "streak": streak.dict(),
            "rewards": reward_system.dict(),
            "achievements": {
                "unlocked_count": len(achievements),
                "total_count": len(all_achievements),
                "details": achievement_details
            },
            "study_groups": [g.dict() for g in groups],
            "motivation_profile": motivation,
            "next_milestones": await self._get_next_milestones(user_id)
        }
    
    async def _get_achievement_progress(self, user_id: str, achievement: Achievement) -> float:
        """Get progress percentage for an achievement"""
        if achievement.requirement_type == "session_count":
            sessions = await db_service.get_user_sessions(user_id, active_only=False)
            return min((len(sessions) / achievement.requirement_value) * 100, 100)
            
        elif achievement.requirement_type == "streak_days":
            streak = await db_service.get_or_create_streak(user_id)
            return min((streak.current_streak / achievement.requirement_value) * 100, 100)
            
        elif achievement.requirement_type == "concepts_mastered":
            progress_list = await db_service.get_user_progress(user_id)
            total_concepts = sum(len(p.concepts_mastered) for p in progress_list)
            return min((total_concepts / achievement.requirement_value) * 100, 100)
            
        return 0.0
    
    async def _get_next_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """Get next achievable milestones for user"""
        user_achievements = await db_service.get_user_achievements(user_id)
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        
        next_milestones = []
        for achievement in self.achievement_templates:
            if achievement.id not in unlocked_ids:
                progress = await self._get_achievement_progress(user_id, achievement)
                if progress > 0:  # Only include started achievements
                    next_milestones.append({
                        "achievement": achievement.dict(),
                        "progress": progress,
                        "priority": "high" if progress > 75 else "medium" if progress > 25 else "low"
                    })
        
        # Sort by progress descending
        next_milestones.sort(key=lambda x: x["progress"], reverse=True)
        return next_milestones[:5]  # Return top 5

# Global gamification service instance
gamification_service = GamificationService()