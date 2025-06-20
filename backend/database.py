from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv
from models import (
    User, UserCreate, ChatSession, SessionCreate, ChatMessage, MessageCreate,
    LearningProgress, Exercise, ExerciseSubmission, LearningPath,
    Achievement, UserAchievement, LearningStreak, RewardSystem, StudyGroup, GroupActivity,
    StreamingSession, StreamInterruption, FactCheckResult
)
import logging

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'test_database')
            
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB successfully at {mongo_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    # User operations
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(**user_data.dict())
        result = await self.db.users.insert_one(user.dict())
        user.id = str(result.inserted_id) if result.inserted_id != user.id else user.id
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = await self.db.users.find_one({"id": user_id})
        return User(**user_data) if user_data else None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = await self.db.users.find_one({"email": email})
        return User(**user_data) if user_data else None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # Session operations
    async def create_session(self, session_data: SessionCreate) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(**session_data.dict())
        await self.db.sessions.insert_one(session.dict())
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        session_data = await self.db.sessions.find_one({"id": session_id})
        return ChatSession(**session_data) if session_data else None
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[ChatSession]:
        """Get all sessions for a user"""
        query = {"user_id": user_id}
        if active_only:
            query["is_active"] = True
            
        sessions = await self.db.sessions.find(query).sort("created_at", -1).to_list(50)
        return [ChatSession(**session) for session in sessions]
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        result = await self.db.sessions.update_one(
            {"id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def end_session(self, session_id: str) -> bool:
        """Mark session as inactive"""
        return await self.update_session(session_id, {"is_active": False})
    
    # Message operations
    async def save_message(self, message_data: MessageCreate) -> ChatMessage:
        """Save a chat message"""
        message = ChatMessage(**message_data.dict())
        await self.db.messages.insert_one(message.dict())
        return message
    
    async def get_session_messages(
        self, 
        session_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a session"""
        messages = await self.db.messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).skip(offset).limit(limit).to_list(limit)
        
        return [ChatMessage(**message) for message in messages]
    
    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for context"""
        messages = await self.db.messages.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return [ChatMessage(**message) for message in reversed(messages)]
    
    # Learning progress operations
    async def save_progress(self, progress: LearningProgress) -> LearningProgress:
        """Save learning progress"""
        await self.db.progress.insert_one(progress.dict())
        return progress
    
    async def get_user_progress(self, user_id: str, subject: str = None) -> List[LearningProgress]:
        """Get user's learning progress"""
        query = {"user_id": user_id}
        if subject:
            query["subject"] = subject
            
        progress_data = await self.db.progress.find(query).to_list(100)
        return [LearningProgress(**progress) for progress in progress_data]
    
    async def update_progress(
        self, 
        user_id: str, 
        subject: str, 
        topic: str, 
        competency_level: float
    ) -> bool:
        """Update learning progress for a topic"""
        result = await self.db.progress.update_one(
            {"user_id": user_id, "subject": subject, "topic": topic},
            {
                "$set": {
                    "competency_level": competency_level,
                    "last_reviewed": "datetime.utcnow()"
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    # Exercise operations
    async def save_exercise(self, exercise: Exercise) -> Exercise:
        """Save an exercise"""
        await self.db.exercises.insert_one(exercise.dict())
        return exercise
    
    async def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get exercise by ID"""
        exercise_data = await self.db.exercises.find_one({"id": exercise_id})
        return Exercise(**exercise_data) if exercise_data else None
    
    async def save_submission(self, submission: ExerciseSubmission) -> ExerciseSubmission:
        """Save exercise submission"""
        await self.db.submissions.insert_one(submission.dict())
        return submission
    
    async def get_user_submissions(self, user_id: str, exercise_id: str = None) -> List[ExerciseSubmission]:
        """Get user's exercise submissions"""
        # For now, we'll implement a simple lookup
        # In a real app, you'd want to track user-exercise relationships
        query = {}
        if exercise_id:
            query["exercise_id"] = exercise_id
            
        submissions = await self.db.submissions.find(query).to_list(100)
        return [ExerciseSubmission(**sub) for sub in submissions]
    
    # Learning path operations
    async def save_learning_path(self, path: LearningPath) -> LearningPath:
        """Save learning path"""
        await self.db.learning_paths.insert_one(path.dict())
        return path
    
    async def get_user_learning_paths(self, user_id: str) -> List[LearningPath]:
        """Get user's learning paths"""
        paths = await self.db.learning_paths.find({"user_id": user_id}).to_list(50)
        return [LearningPath(**path) for path in paths]
    
    async def update_learning_path_progress(
        self, 
        path_id: str, 
        milestone: int
    ) -> bool:
        """Update learning path progress"""
        result = await self.db.learning_paths.update_one(
            {"id": path_id},
            {"$set": {"current_milestone": milestone}}
        )
        return result.modified_count > 0

    # Gamification operations
    async def create_achievement(self, achievement: Achievement) -> Achievement:
        """Create a new achievement"""
        await self.db.achievements.insert_one(achievement.dict())
        return achievement
    
    async def get_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        achievements = await self.db.achievements.find({}).to_list(100)
        return [Achievement(**ach) for ach in achievements]
    
    async def unlock_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Unlock an achievement for a user"""
        # Check if already unlocked
        existing = await self.db.user_achievements.find_one({
            "user_id": user_achievement.user_id,
            "achievement_id": user_achievement.achievement_id
        })
        
        if not existing:
            await self.db.user_achievements.insert_one(user_achievement.dict())
        return user_achievement
    
    async def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get user's unlocked achievements"""
        achievements = await self.db.user_achievements.find({"user_id": user_id}).to_list(100)
        return [UserAchievement(**ach) for ach in achievements]
    
    async def get_or_create_streak(self, user_id: str) -> LearningStreak:
        """Get or create learning streak for user"""
        streak_data = await self.db.learning_streaks.find_one({"user_id": user_id})
        
        if streak_data:
            return LearningStreak(**streak_data)
        else:
            streak = LearningStreak(user_id=user_id)
            await self.db.learning_streaks.insert_one(streak.dict())
            return streak
    
    async def update_streak(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update learning streak"""
        result = await self.db.learning_streaks.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def get_or_create_reward_system(self, user_id: str) -> RewardSystem:
        """Get or create reward system for user"""
        reward_data = await self.db.reward_systems.find_one({"user_id": user_id})
        
        if reward_data:
            return RewardSystem(**reward_data)
        else:
            reward = RewardSystem(user_id=user_id)
            await self.db.reward_systems.insert_one(reward.dict())
            return reward
    
    async def update_reward_system(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update reward system"""
        result = await self.db.reward_systems.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def create_study_group(self, study_group: StudyGroup) -> StudyGroup:
        """Create a new study group"""
        await self.db.study_groups.insert_one(study_group.dict())
        return study_group
    
    async def get_study_groups(self, user_id: str = None) -> List[StudyGroup]:
        """Get study groups (user's groups or all public groups)"""
        if user_id:
            groups = await self.db.study_groups.find({
                "$or": [
                    {"members": user_id},
                    {"admin_id": user_id}
                ]
            }).to_list(50)
        else:
            groups = await self.db.study_groups.find({"is_public": True}).to_list(50)
        
        return [StudyGroup(**group) for group in groups]
    
    async def join_study_group(self, group_id: str, user_id: str) -> bool:
        """Join a study group"""
        result = await self.db.study_groups.update_one(
            {"id": group_id, "members": {"$ne": user_id}},
            {"$push": {"members": user_id}}
        )
        return result.modified_count > 0
    
    async def add_group_activity(self, activity: GroupActivity) -> GroupActivity:
        """Add activity to study group"""
        await self.db.group_activities.insert_one(activity.dict())
        
        # Update group activity feed
        await self.db.study_groups.update_one(
            {"id": activity.group_id},
            {"$push": {"activity_feed": activity.dict()}}
        )
        return activity
    
    async def get_group_activities(self, group_id: str, limit: int = 50) -> List[GroupActivity]:
        """Get activities for a study group"""
        activities = await self.db.group_activities.find(
            {"group_id": group_id}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return [GroupActivity(**activity) for activity in activities]
    
    # Advanced Streaming operations
    async def create_streaming_session(self, streaming_session: StreamingSession) -> StreamingSession:
        """Create a new streaming session"""
        await self.db.streaming_sessions.insert_one(streaming_session.dict())
        return streaming_session
    
    async def get_streaming_session(self, session_id: str) -> Optional[StreamingSession]:
        """Get streaming session by session ID"""
        stream_data = await self.db.streaming_sessions.find_one({"session_id": session_id})
        return StreamingSession(**stream_data) if stream_data else None
    
    async def update_streaming_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update streaming session"""
        result = await self.db.streaming_sessions.update_one(
            {"session_id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def save_stream_interruption(self, interruption: StreamInterruption) -> StreamInterruption:
        """Save stream interruption"""
        await self.db.stream_interruptions.insert_one(interruption.dict())
        return interruption
    
    async def save_fact_check_result(self, fact_check: FactCheckResult) -> FactCheckResult:
        """Save fact check result"""
        await self.db.fact_check_results.insert_one(fact_check.dict())
        return fact_check

# Global database instance
db_service = DatabaseService()
