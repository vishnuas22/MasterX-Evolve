"""
Advanced Context Awareness Service for MasterX AI Mentor System

This service provides sophisticated context awareness features including:
- Emotional State Detection
- Learning Style Adaptation
- Cognitive Load Management
- Multi-Session Memory
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from groq import AsyncGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """Emotional states that the AI can detect"""
    FRUSTRATED = "frustrated"
    CONFIDENT = "confident"
    CONFUSED = "confused"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    FOCUSED = "focused"
    TIRED = "tired"
    MOTIVATED = "motivated"

class LearningStyle(Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MULTIMODAL = "multimodal"

class CognitiveLoad(Enum):
    """Cognitive load levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    OVERLOAD = "overload"

@dataclass
class ContextState:
    """Comprehensive context state for a user"""
    user_id: str
    session_id: str
    timestamp: datetime
    
    # Emotional State
    emotional_state: EmotionalState
    emotional_confidence: float  # 0.0 to 1.0
    emotional_indicators: Dict[str, Any]
    
    # Learning Style
    learning_style: LearningStyle
    style_confidence: float
    style_adaptations: Dict[str, Any]
    
    # Cognitive Load
    cognitive_load: CognitiveLoad
    load_factors: Dict[str, float]
    response_complexity: float
    
    # Multi-Session Memory
    session_history: List[Dict[str, Any]]
    concept_mastery: Dict[str, float]
    learning_patterns: Dict[str, Any]
    
    # Adaptive Features
    preferred_pace: float
    explanation_depth: float
    interaction_style: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'emotional_state': self.emotional_state.value,
            'emotional_confidence': self.emotional_confidence,
            'emotional_indicators': self.emotional_indicators,
            'learning_style': self.learning_style.value,
            'style_confidence': self.style_confidence,
            'style_adaptations': self.style_adaptations,
            'cognitive_load': self.cognitive_load.value,
            'load_factors': self.load_factors,
            'response_complexity': self.response_complexity,
            'session_history': self.session_history,
            'concept_mastery': self.concept_mastery,
            'learning_patterns': self.learning_patterns,
            'preferred_pace': self.preferred_pace,
            'explanation_depth': self.explanation_depth,
            'interaction_style': self.interaction_style
        }

class AdvancedContextService:
    """Advanced context awareness service"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "deepseek-r1-distill-llama-70b"
        
        # Context memory storage (in production, use Redis or similar)
        self.context_memory: Dict[str, ContextState] = {}
        self.session_memories: Dict[str, List[Dict[str, Any]]] = {}
        
        # Cognitive load tracking
        self.response_times: Dict[str, List[float]] = {}
        self.interaction_patterns: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Advanced Context Service initialized")

    async def analyze_emotional_state(self, user_message: str, conversation_context: List[Dict[str, Any]]) -> Tuple[EmotionalState, float, Dict[str, Any]]:
        """Analyze user's emotional state from their message and conversation context"""
        try:
            # Prepare context for analysis
            context_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in conversation_context[-5:]])
            
            prompt = f"""
            Analyze the emotional state of the user based on their latest message and conversation context.

            Conversation Context:
            {context_text}

            Latest User Message: "{user_message}"

            Analyze the emotional indicators in the text. Consider:
            - Frustration indicators: confusion, repeated questions, negative language
            - Confidence indicators: assertive language, follow-up questions, engagement
            - Confusion indicators: unclear questions, contradictory statements
            - Excitement indicators: enthusiastic language, multiple questions
            - Anxiety indicators: hesitation, self-doubt, worried tone
            - Focus indicators: clear questions, building on previous topics
            - Tiredness indicators: short responses, lack of engagement
            - Motivation indicators: goal-oriented language, determination

            Return ONLY a JSON object with:
            {{
                "emotional_state": "one of: frustrated, confident, confused, excited, anxious, focused, tired, motivated",
                "confidence": 0.8,
                "indicators": {{
                    "primary_signals": ["signal1", "signal2"],
                    "language_patterns": ["pattern1", "pattern2"],
                    "engagement_level": 0.7,
                    "complexity_preference": 0.6
                }}
            }}
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            
            emotional_state = EmotionalState(analysis['emotional_state'])
            confidence = analysis['confidence']
            indicators = analysis['indicators']
            
            return emotional_state, confidence, indicators
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {str(e)}")
            return EmotionalState.FOCUSED, 0.5, {}

    async def detect_learning_style(self, user_id: str, interaction_history: List[Dict[str, Any]]) -> Tuple[LearningStyle, float, Dict[str, Any]]:
        """Detect user's learning style based on interaction history"""
        try:
            # Analyze interaction patterns
            style_signals = {
                'visual': 0.0,
                'auditory': 0.0,
                'kinesthetic': 0.0,
                'reading': 0.0
            }
            
            for interaction in interaction_history[-10:]:  # Last 10 interactions
                message = interaction.get('message', '')
                
                # Visual learning indicators
                if any(word in message.lower() for word in ['see', 'show', 'diagram', 'picture', 'visual', 'image', 'chart']):
                    style_signals['visual'] += 1
                
                # Auditory learning indicators
                if any(word in message.lower() for word in ['hear', 'listen', 'sound', 'speak', 'voice', 'audio', 'music']):
                    style_signals['auditory'] += 1
                
                # Kinesthetic learning indicators
                if any(word in message.lower() for word in ['do', 'practice', 'hands-on', 'try', 'exercise', 'activity', 'build']):
                    style_signals['kinesthetic'] += 1
                
                # Reading/writing indicators
                if any(word in message.lower() for word in ['read', 'write', 'list', 'steps', 'details', 'explanation']):
                    style_signals['reading'] += 1
            
            # Determine primary learning style
            if max(style_signals.values()) == 0:
                return LearningStyle.MULTIMODAL, 0.5, {}
            
            primary_style = max(style_signals, key=style_signals.get)
            confidence = style_signals[primary_style] / len(interaction_history[-10:])
            
            # Create adaptations based on style
            adaptations = {
                'visual': {
                    'include_diagrams': True,
                    'use_visual_metaphors': True,
                    'structure_with_headers': True,
                    'include_examples': True
                },
                'auditory': {
                    'conversational_tone': True,
                    'use_analogies': True,
                    'include_verbal_cues': True,
                    'rhythmic_explanations': True
                },
                'kinesthetic': {
                    'include_exercises': True,
                    'hands_on_examples': True,
                    'step_by_step_actions': True,
                    'practical_applications': True
                },
                'reading': {
                    'detailed_explanations': True,
                    'structured_content': True,
                    'include_references': True,
                    'comprehensive_coverage': True
                }
            }
            
            return LearningStyle(primary_style), confidence, adaptations.get(primary_style, {})
            
        except Exception as e:
            logger.error(f"Error detecting learning style: {str(e)}")
            return LearningStyle.MULTIMODAL, 0.5, {}

    async def assess_cognitive_load(self, user_id: str, session_data: Dict[str, Any]) -> Tuple[CognitiveLoad, Dict[str, float]]:
        """Assess cognitive load based on various factors"""
        try:
            load_factors = {}
            
            # Response time analysis
            response_times = self.response_times.get(user_id, [])
            if response_times:
                avg_response_time = sum(response_times[-5:]) / len(response_times[-5:])
                if avg_response_time > 30:  # > 30 seconds
                    load_factors['response_time'] = 0.8
                elif avg_response_time > 15:
                    load_factors['response_time'] = 0.6
                else:
                    load_factors['response_time'] = 0.3
            else:
                load_factors['response_time'] = 0.5
            
            # Question complexity
            recent_questions = session_data.get('recent_questions', [])
            if recent_questions:
                complex_questions = sum(1 for q in recent_questions if len(q.split()) > 10)
                load_factors['question_complexity'] = complex_questions / len(recent_questions)
            else:
                load_factors['question_complexity'] = 0.5
            
            # Error rate
            recent_errors = session_data.get('recent_errors', 0)
            total_interactions = session_data.get('total_interactions', 1)
            load_factors['error_rate'] = recent_errors / total_interactions
            
            # Session duration
            session_duration = session_data.get('duration_minutes', 0)
            if session_duration > 60:
                load_factors['session_fatigue'] = 0.8
            elif session_duration > 30:
                load_factors['session_fatigue'] = 0.6
            else:
                load_factors['session_fatigue'] = 0.2
            
            # Calculate overall cognitive load
            overall_load = sum(load_factors.values()) / len(load_factors)
            
            if overall_load > 0.8:
                cognitive_load = CognitiveLoad.OVERLOAD
            elif overall_load > 0.6:
                cognitive_load = CognitiveLoad.HIGH
            elif overall_load > 0.4:
                cognitive_load = CognitiveLoad.MEDIUM
            else:
                cognitive_load = CognitiveLoad.LOW
            
            return cognitive_load, load_factors
            
        except Exception as e:
            logger.error(f"Error assessing cognitive load: {str(e)}")
            return CognitiveLoad.MEDIUM, {}

    async def manage_multi_session_memory(self, user_id: str, session_id: str, current_interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Manage multi-session memory for continuity"""
        try:
            # Initialize or update session memory
            if user_id not in self.session_memories:
                self.session_memories[user_id] = []
            
            # Add current interaction to memory
            memory_entry = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'interaction': current_interaction,
                'concepts_discussed': self._extract_concepts(current_interaction.get('message', '')),
                'learning_progress': current_interaction.get('learning_progress', {})
            }
            
            self.session_memories[user_id].append(memory_entry)
            
            # Keep only last 50 interactions to manage memory
            self.session_memories[user_id] = self.session_memories[user_id][-50:]
            
            # Analyze learning patterns
            learning_patterns = self._analyze_learning_patterns(self.session_memories[user_id])
            
            # Concept mastery tracking
            concept_mastery = self._track_concept_mastery(self.session_memories[user_id])
            
            return {
                'session_history': self.session_memories[user_id][-10:],  # Last 10 for context
                'learning_patterns': learning_patterns,
                'concept_mastery': concept_mastery,
                'memory_insights': self._generate_memory_insights(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error managing multi-session memory: {str(e)}")
            return {}

    def _extract_concepts(self, message: str) -> List[str]:
        """Extract key concepts from message"""
        # Simple concept extraction (can be enhanced with NLP)
        concepts = []
        
        # Technical terms and concepts
        tech_terms = ['algorithm', 'data structure', 'programming', 'function', 'variable', 'loop', 'array', 'object']
        science_terms = ['physics', 'chemistry', 'biology', 'mathematics', 'equation', 'theory', 'experiment']
        
        message_lower = message.lower()
        for term in tech_terms + science_terms:
            if term in message_lower:
                concepts.append(term)
        
        return concepts

    def _analyze_learning_patterns(self, session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning patterns from session history"""
        patterns = {
            'preferred_times': [],
            'topic_transitions': [],
            'question_types': [],
            'engagement_levels': []
        }
        
        for entry in session_history:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            patterns['preferred_times'].append(timestamp.hour)
            
            concepts = entry.get('concepts_discussed', [])
            if concepts:
                patterns['topic_transitions'].extend(concepts)
        
        return patterns

    def _track_concept_mastery(self, session_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Track concept mastery over time"""
        concept_mastery = {}
        
        for entry in session_history:
            concepts = entry.get('concepts_discussed', [])
            for concept in concepts:
                if concept not in concept_mastery:
                    concept_mastery[concept] = 0.0
                
                # Increase mastery based on engagement
                concept_mastery[concept] = min(1.0, concept_mastery[concept] + 0.1)
        
        return concept_mastery

    def _generate_memory_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights from user's learning history"""
        if user_id not in self.session_memories:
            return {}
        
        history = self.session_memories[user_id]
        
        # Calculate insights
        total_sessions = len(set(entry['session_id'] for entry in history))
        avg_concepts_per_session = sum(len(entry.get('concepts_discussed', [])) for entry in history) / len(history)
        
        return {
            'total_sessions': total_sessions,
            'avg_concepts_per_session': avg_concepts_per_session,
            'learning_consistency': self._calculate_consistency(history),
            'growth_trajectory': self._calculate_growth(history)
        }

    def _calculate_consistency(self, history: List[Dict[str, Any]]) -> float:
        """Calculate learning consistency"""
        if len(history) < 2:
            return 0.5
        
        # Simple consistency metric based on regular interaction
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in history]
        time_gaps = [(timestamps[i+1] - timestamps[i]).days for i in range(len(timestamps)-1)]
        
        # Consistent if average gap is less than 3 days
        avg_gap = sum(time_gaps) / len(time_gaps)
        return max(0.0, min(1.0, 1.0 - (avg_gap / 7.0)))  # Normalize to 0-1

    def _calculate_growth(self, history: List[Dict[str, Any]]) -> float:
        """Calculate learning growth trajectory"""
        if len(history) < 3:
            return 0.5
        
        # Growth based on increasing concept mastery
        early_concepts = sum(len(entry.get('concepts_discussed', [])) for entry in history[:len(history)//2])
        later_concepts = sum(len(entry.get('concepts_discussed', [])) for entry in history[len(history)//2:])
        
        if early_concepts == 0:
            return 0.5
        
        growth_ratio = later_concepts / early_concepts
        return min(1.0, growth_ratio / 2.0)  # Normalize to 0-1

    async def get_context_state(self, user_id: str, session_id: str, conversation_context: List[Dict[str, Any]], current_message: str) -> ContextState:
        """Get comprehensive context state for user"""
        try:
            # Analyze emotional state
            emotional_state, emotional_confidence, emotional_indicators = await self.analyze_emotional_state(
                current_message, conversation_context
            )
            
            # Detect learning style
            learning_style, style_confidence, style_adaptations = await self.detect_learning_style(
                user_id, conversation_context
            )
            
            # Assess cognitive load
            session_data = {
                'recent_questions': [msg['message'] for msg in conversation_context if msg['sender'] == 'user'],
                'recent_errors': 0,  # Would be tracked from user feedback
                'total_interactions': len(conversation_context),
                'duration_minutes': 30  # Would be calculated from session start
            }
            cognitive_load, load_factors = await self.assess_cognitive_load(user_id, session_data)
            
            # Manage multi-session memory
            current_interaction = {
                'message': current_message,
                'timestamp': datetime.now().isoformat(),
                'sender': 'user'
            }
            memory_data = await self.manage_multi_session_memory(user_id, session_id, current_interaction)
            
            # Create context state
            context_state = ContextState(
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                emotional_state=emotional_state,
                emotional_confidence=emotional_confidence,
                emotional_indicators=emotional_indicators,
                learning_style=learning_style,
                style_confidence=style_confidence,
                style_adaptations=style_adaptations,
                cognitive_load=cognitive_load,
                load_factors=load_factors,
                response_complexity=self._calculate_response_complexity(cognitive_load, emotional_state),
                session_history=memory_data.get('session_history', []),
                concept_mastery=memory_data.get('concept_mastery', {}),
                learning_patterns=memory_data.get('learning_patterns', {}),
                preferred_pace=self._calculate_preferred_pace(cognitive_load, emotional_state),
                explanation_depth=self._calculate_explanation_depth(learning_style, cognitive_load),
                interaction_style=self._determine_interaction_style(emotional_state, learning_style)
            )
            
            # Cache context state
            self.context_memory[user_id] = context_state
            
            return context_state
            
        except Exception as e:
            logger.error(f"Error getting context state: {str(e)}")
            # Return default context state
            return ContextState(
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                emotional_state=EmotionalState.FOCUSED,
                emotional_confidence=0.5,
                emotional_indicators={},
                learning_style=LearningStyle.MULTIMODAL,
                style_confidence=0.5,
                style_adaptations={},
                cognitive_load=CognitiveLoad.MEDIUM,
                load_factors={},
                response_complexity=0.5,
                session_history=[],
                concept_mastery={},
                learning_patterns={},
                preferred_pace=0.5,
                explanation_depth=0.5,
                interaction_style="balanced"
            )

    def _calculate_response_complexity(self, cognitive_load: CognitiveLoad, emotional_state: EmotionalState) -> float:
        """Calculate appropriate response complexity"""
        base_complexity = 0.5
        
        # Adjust for cognitive load
        if cognitive_load == CognitiveLoad.OVERLOAD:
            base_complexity *= 0.3
        elif cognitive_load == CognitiveLoad.HIGH:
            base_complexity *= 0.6
        elif cognitive_load == CognitiveLoad.LOW:
            base_complexity *= 1.2
        
        # Adjust for emotional state
        if emotional_state in [EmotionalState.FRUSTRATED, EmotionalState.CONFUSED]:
            base_complexity *= 0.7
        elif emotional_state == EmotionalState.CONFIDENT:
            base_complexity *= 1.3
        
        return min(1.0, max(0.1, base_complexity))

    def _calculate_preferred_pace(self, cognitive_load: CognitiveLoad, emotional_state: EmotionalState) -> float:
        """Calculate preferred learning pace"""
        base_pace = 0.5
        
        if cognitive_load == CognitiveLoad.OVERLOAD:
            base_pace *= 0.3
        elif cognitive_load == CognitiveLoad.HIGH:
            base_pace *= 0.6
        elif emotional_state == EmotionalState.EXCITED:
            base_pace *= 1.2
        elif emotional_state == EmotionalState.TIRED:
            base_pace *= 0.4
        
        return min(1.0, max(0.1, base_pace))

    def _calculate_explanation_depth(self, learning_style: LearningStyle, cognitive_load: CognitiveLoad) -> float:
        """Calculate appropriate explanation depth"""
        base_depth = 0.5
        
        if learning_style == LearningStyle.READING:
            base_depth *= 1.3
        elif learning_style == LearningStyle.VISUAL:
            base_depth *= 0.8
        
        if cognitive_load == CognitiveLoad.OVERLOAD:
            base_depth *= 0.4
        elif cognitive_load == CognitiveLoad.LOW:
            base_depth *= 1.2
        
        return min(1.0, max(0.1, base_depth))

    def _determine_interaction_style(self, emotional_state: EmotionalState, learning_style: LearningStyle) -> str:
        """Determine appropriate interaction style"""
        if emotional_state == EmotionalState.FRUSTRATED:
            return "supportive"
        elif emotional_state == EmotionalState.EXCITED:
            return "energetic"
        elif emotional_state == EmotionalState.CONFUSED:
            return "clarifying"
        elif learning_style == LearningStyle.AUDITORY:
            return "conversational"
        elif learning_style == LearningStyle.KINESTHETIC:
            return "interactive"
        else:
            return "balanced"

# Create global instance
advanced_context_service = AdvancedContextService()