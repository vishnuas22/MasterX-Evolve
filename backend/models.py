from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# User 
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str
    learning_preferences: Optional[Dict[str, Any]] = None

# Session Models
class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: Optional[str] = None
    current_topic: Optional[str] = None
    learning_objectives: List[str] = Field(default_factory=list)
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    session_state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class SessionCreate(BaseModel):
    user_id: str
    subject: Optional[str] = None
    learning_objectives: Optional[List[str]] = []
    difficulty_level: str = "beginner"

# Message Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    sender: str  # "user" or "mentor"
    message_type: str = "text"  # text, exercise, feedback, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    session_id: str
    message: str
    sender: str = "user"
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = {}

# AI Request/Response Models
class MentorRequest(BaseModel):
    session_id: str
    user_message: str
    context: Optional[Dict[str, Any]] = None

class MentorResponse(BaseModel):
    response: str
    response_type: str = "explanation"  # explanation, exercise, feedback, summary
    suggested_actions: List[str] = Field(default_factory=list)
    concepts_covered: List[str] = Field(default_factory=list)
    next_steps: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Learning Progress Models
class LearningProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    topic: str
    competency_level: float = 0.0  # 0.0 to 1.0
    concepts_mastered: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    last_reviewed: datetime = Field(default_factory=datetime.utcnow)
    next_review_due: Optional[datetime] = None

# Exercise Models
class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    question: str
    exercise_type: str  # multiple_choice, short_answer, coding, problem_solving
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: str = "medium"
    concepts: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExerciseSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exercise_id: str
    user_answer: str
    is_correct: bool
    feedback: str
    score: float = 0.0
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

# Learning Path Models
class LearningPath(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    current_milestone: int = 0
    estimated_completion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Gamification Models
class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    category: str  # learning, streak, milestone, mastery, collaboration
    requirement_type: str  # session_count, streak_days, concepts_mastered, etc.
    requirement_value: int
    points_reward: int
    badge_color: str = "blue"
    is_premium: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserAchievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    achievement_id: str
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)
    progress_when_unlocked: Dict[str, Any] = Field(default_factory=dict)

class LearningStreak(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    freeze_count: int = 0  # Streak recovery mechanisms
    total_learning_days: int = 0
    streak_goals: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RewardSystem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    total_points: int = 0
    level: int = 1
    experience_points: int = 0
    points_to_next_level: int = 100
    motivation_profile: Dict[str, Any] = Field(default_factory=dict)  # adaptive rewards
    reward_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudyGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    subject: str
    members: List[str] = Field(default_factory=list)  # user_ids
    admin_id: str
    ai_facilitator_active: bool = True
    group_goals: List[str] = Field(default_factory=list)
    activity_feed: List[Dict[str, Any]] = Field(default_factory=list)
    study_sessions: List[str] = Field(default_factory=list)  # session_ids
    max_members: int = 10
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GroupActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    activity_type: str  # question, answer, achievement, milestone
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reactions: Dict[str, List[str]] = Field(default_factory=dict)  # emoji -> user_ids
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Advanced Streaming Models
class StreamingSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    typing_speed_wpm: int = 200  # words per minute
    reading_speed_preference: str = "normal"  # slow, normal, fast
    interrupt_enabled: bool = True
    multi_branch_mode: bool = False
    fact_check_enabled: bool = True
    stream_analytics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StreamInterruption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    streaming_session_id: str
    user_id: str
    interrupt_message: str
    interrupt_timestamp: datetime = Field(default_factory=datetime.utcnow)
    ai_response: Optional[str] = None
    context_preserved: Dict[str, Any] = Field(default_factory=dict)

class FactCheckResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    confidence_score: float  # 0.0 to 1.0
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    verification_status: str  # verified, disputed, unverified
    fact_check_timestamp: datetime = Field(default_factory=datetime.utcnow)
