"""
Premium AI Service with Advanced Learning Modes for MasterX
Integrates multi-model capabilities with specialized learning approaches
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from models import ChatSession, ChatMessage, MentorResponse
from model_manager import premium_model_manager, TaskType

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

class PremiumLearningModes:
    """Advanced learning modes for premium MasterX experience"""
    
    @staticmethod
    def get_socratic_prompt(user_message: str, session: ChatSession, context: Dict[str, Any]) -> str:
        """Generate Socratic mode prompt for question-based learning"""
        return f"""
🤔 **SOCRATIC LEARNING MODE ACTIVATED**

The user said: "{user_message}"

Your role: Guide discovery through strategic questions. Don't give direct answers - instead:

1. **Ask Probing Questions**: Help them think deeper about the concept
2. **Build on Responses**: Use their answers to ask progressively more insightful questions  
3. **Reveal Patterns**: Guide them to discover underlying principles themselves
4. **Encourage Reasoning**: Make them articulate their thinking process

**Session Context:**
- Subject: {session.subject or 'General Learning'}
- Level: {session.difficulty_level}
- User's Learning Style: {context.get('learning_style', 'adaptive')}

**Socratic Guidelines:**
- Start with "What do you think..." or "How would you explain..."
- If they seem confused, break down into smaller questions
- If they're on track, deepen with "Why do you think that is?"
- Always validate their thinking process, even if the answer isn't perfect
- End with a question that leads to the next discovery

Remember: The goal is insight through self-discovery, not just correct answers.
"""

    @staticmethod
    def get_debug_prompt(user_message: str, session: ChatSession, context: Dict[str, Any]) -> str:
        """Generate debug mode prompt for identifying knowledge gaps"""
        return f"""
🔍 **DEBUG MODE ACTIVATED**

The user said: "{user_message}"

Your role: Identify and fix knowledge gaps and misconceptions. Act like a debugging mentor:

1. **Analyze Understanding**: Look for specific gaps or misconceptions
2. **Pinpoint Issues**: Identify exactly where confusion lies
3. **Targeted Fixes**: Provide precise clarification for problem areas
4. **Verify Understanding**: Check that fixes actually resolved the issues

**Session Context:**
- Subject: {session.subject or 'General Learning'}
- Level: {session.difficulty_level}
- Previous Topics Covered: {context.get('topics_covered', [])}

**Debug Process:**
- First, identify what they understand correctly
- Then pinpoint specific areas of confusion or misconception
- Explain the correct concept clearly and concisely
- Use analogies or examples to clarify the corrected understanding
- Ask a quick verification question to ensure the gap is filled

**Response Format:**
✅ **What you understand correctly:** [acknowledge what's right]
❌ **The confusion/gap:** [specific issue identified]
🔧 **The fix:** [clear, targeted explanation]
✓ **Quick check:** [verification question]
"""

    @staticmethod
    def get_challenge_prompt(user_message: str, session: ChatSession, context: Dict[str, Any]) -> str:
        """Generate challenge mode prompt for progressive difficulty"""
        current_level = context.get('challenge_level', 1)
        max_level = 10
        
        return f"""
🏆 **CHALLENGE MODE ACTIVATED - Level {current_level}/{max_level}**

The user said: "{user_message}"

Your role: Provide progressively challenging problems that stretch their abilities:

1. **Assess Current Level**: Understand where they are now
2. **Design Challenge**: Create a problem slightly above their comfort zone
3. **Provide Scaffolding**: Offer hints if they struggle, but maintain challenge
4. **Level Up**: If they succeed easily, increase difficulty for next challenge

**Session Context:**
- Subject: {session.subject or 'General Learning'}
- Base Level: {session.difficulty_level}
- Challenge Level: {current_level}/{max_level}
- Recent Performance: {context.get('recent_performance', 'unknown')}

**Challenge Guidelines:**
- Make it 15-20% harder than their last successful attempt
- Include real-world applications when possible
- Provide 3 levels of hints: gentle nudge, specific guidance, detailed help
- If they nail it easily, bump up difficulty
- If they struggle significantly, provide more scaffolding
- Celebrate progress and effort, not just correct answers

**Response Structure:**
🎯 **Challenge:** [The problem/question at appropriate difficulty]
💡 **Hint System Ready:** "Ask for a hint if you need guidance"
🚀 **Why This Matters:** [Real-world relevance of this challenge]
"""

    @staticmethod
    def get_mentor_prompt(user_message: str, session: ChatSession, context: Dict[str, Any]) -> str:
        """Generate mentor mode prompt for professional guidance"""
        return f"""
👨‍💼 **MENTOR MODE ACTIVATED**

The user said: "{user_message}"

Your role: Act as a seasoned professional mentor providing industry-level guidance:

1. **Professional Perspective**: Share insights from real-world experience
2. **Career Connections**: Link learning to career advancement opportunities
3. **Industry Standards**: Explain how this knowledge applies in professional settings
4. **Best Practices**: Share proven strategies and approaches
5. **Growth Mindset**: Guide long-term professional development

**Session Context:**
- Subject: {session.subject or 'General Learning'}
- User's Career Goals: {context.get('career_goals', 'not specified')}
- Experience Level: {session.difficulty_level}
- Industry Focus: {context.get('target_industry', 'general')}

**Mentor Guidelines:**
- Speak from experience and authority
- Connect concepts to career opportunities and real projects
- Share "insider knowledge" and practical tips
- Discuss industry trends and future directions
- Provide actionable advice for skill development
- Balance encouragement with realistic expectations

**Response Structure:**
🎓 **Professional Insight:** [Industry perspective on the topic]
💼 **Career Relevance:** [How this knowledge advances their career]
🔥 **Pro Tip:** [Insider knowledge or best practice]
📈 **Next Steps:** [Specific actions to take their skills to the next level]
🌟 **Industry Perspective:** [Where this field is heading]
"""

class PremiumAIService:
    """
    Premium AI Service with advanced learning modes and multi-model integration
    """
    
    def __init__(self):
        self.model_manager = premium_model_manager
        self.learning_modes = PremiumLearningModes()
        
        # Learning analytics
        self.session_analytics = {}
        self.user_preferences = {}
    
    async def get_premium_response(
        self,
        user_message: str,
        session: ChatSession,
        context: Dict[str, Any] = None,
        learning_mode: str = "adaptive",
        stream: bool = False
    ) -> MentorResponse:
        """
        Get premium AI response with advanced learning modes
        
        Args:
            user_message: User's input message
            session: Current learning session
            context: Session context and history
            learning_mode: The learning mode to use (adaptive, socratic, debug, challenge, mentor)
            stream: Whether to stream the response
        
        Returns:
            Enhanced MentorResponse with premium features
        """
        try:
            # Determine optimal task type and learning mode
            task_type, optimized_mode = self._determine_optimal_approach(
                user_message, session, context, learning_mode
            )
            
            # Generate optimized prompt based on learning mode
            system_prompt = self._generate_mode_prompt(
                user_message, session, context, optimized_mode
            )
            
            # Get response from best available model
            response = await self.model_manager.get_optimized_response(
                prompt=user_message,
                task_type=task_type,
                system_prompt=system_prompt,
                context=context,
                stream=stream,
                user_preferences=self.user_preferences.get(session.user_id, {})
            )
            
            if stream:
                return response  # Return generator for streaming
            else:
                # Process response and add premium features
                content = response.choices[0].message.content
                return self._create_premium_response(
                    content, optimized_mode, task_type, session, context
                )
                
        except Exception as e:
            logger.error(f"Error in premium AI service: {str(e)}")
            return MentorResponse(
                response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                response_type="error",
                metadata={"error": str(e), "mode": learning_mode}
            )
    
    def _determine_optimal_approach(
        self, 
        user_message: str, 
        session: ChatSession, 
        context: Dict[str, Any],
        requested_mode: str
    ) -> tuple[TaskType, str]:
        """
        Intelligently determine the best learning approach based on context
        """
        # Analyze user message for intent
        message_lower = user_message.lower()
        
        # If user explicitly requests a mode, respect it
        if requested_mode in ["socratic", "debug", "challenge", "mentor"]:
            mode_task_map = {
                "socratic": TaskType.SOCRATIC,
                "debug": TaskType.DEBUG,
                "challenge": TaskType.CHALLENGE,
                "mentor": TaskType.MENTOR
            }
            return mode_task_map[requested_mode], requested_mode
        
        # Intelligent mode detection based on user message
        if any(word in message_lower for word in ["why", "how does", "what if", "explain why"]):
            return TaskType.SOCRATIC, "socratic"
        
        elif any(word in message_lower for word in ["confused", "don't understand", "mistake", "wrong", "error"]):
            return TaskType.DEBUG, "debug"
        
        elif any(word in message_lower for word in ["challenge", "harder", "difficult", "test me", "quiz"]):
            return TaskType.CHALLENGE, "challenge"
        
        elif any(word in message_lower for word in ["career", "professional", "industry", "job", "work"]):
            return TaskType.MENTOR, "mentor"
        
        elif any(word in message_lower for word in ["exercise", "practice", "problem"]):
            return TaskType.EXERCISE, "adaptive"
        
        else:
            # Default to explanation mode
            return TaskType.EXPLANATION, "adaptive"
    
    def _generate_mode_prompt(
        self, 
        user_message: str, 
        session: ChatSession, 
        context: Dict[str, Any],
        mode: str
    ) -> str:
        """Generate system prompt based on selected learning mode"""
        
        if mode == "socratic":
            return self.learning_modes.get_socratic_prompt(user_message, session, context)
        elif mode == "debug":
            return self.learning_modes.get_debug_prompt(user_message, session, context)
        elif mode == "challenge":
            return self.learning_modes.get_challenge_prompt(user_message, session, context)
        elif mode == "mentor":
            return self.learning_modes.get_mentor_prompt(user_message, session, context)
        else:
            # Adaptive/default mode with enhanced features
            return f"""
You are MasterX, a world-class AI Learning Mentor with premium capabilities. Provide an adaptive, personalized learning experience.

**Current Session:**
- Subject: {session.subject or 'General Learning'}
- Level: {session.difficulty_level}
- User Goals: {', '.join(session.learning_objectives) if session.learning_objectives else 'Exploratory Learning'}

**Enhanced Features:**
- Use intelligent examples and analogies
- Provide multiple explanation approaches (visual, logical, practical)
- Include real-world applications
- Offer progressive difficulty options
- Add professional insights when relevant

**Premium Response Structure:**
- Clear, engaging explanation
- Practical examples
- Visual or conceptual aids description
- Follow-up questions or exercises
- Next learning steps

Make this a premium learning experience that adapts to the user's needs and maximizes understanding.
"""
    
    def _create_premium_response(
        self,
        content: str,
        mode: str,
        task_type: TaskType,
        session: ChatSession,
        context: Dict[str, Any]
    ) -> MentorResponse:
        """Create enhanced MentorResponse with premium features"""
        
        # Enhanced metadata with learning analytics
        metadata = {
            "learning_mode": mode,
            "task_type": task_type.value,
            "model_used": "premium_multi_model",
            "session_id": session.id,
            "timestamp": datetime.utcnow().isoformat(),
            "premium_features": {
                "adaptive_difficulty": True,
                "personalized_content": True,
                "multi_modal_support": True,
                "analytics_enabled": True
            }
        }
        
        # Generate intelligent follow-up actions based on mode
        suggested_actions = self._generate_smart_actions(mode, content, context)
        
        # Extract concepts and learning objectives
        concepts_covered = self._extract_concepts(content)
        
        # Determine next steps based on learning mode
        next_steps = self._determine_next_steps(mode, session, context)
        
        return MentorResponse(
            response=content,
            response_type=f"premium_{mode}",
            suggested_actions=suggested_actions,
            concepts_covered=concepts_covered,
            next_steps=next_steps,
            metadata=metadata
        )
    
    def _generate_smart_actions(self, mode: str, content: str, context: Dict[str, Any]) -> List[str]:
        """Generate intelligent follow-up actions based on learning mode"""
        
        base_actions = {
            "socratic": [
                "Think about that question deeply",
                "Try to answer with your own reasoning",
                "Connect this to what you already know",
                "Ask a follow-up question"
            ],
            "debug": [
                "Test your understanding with an example",
                "Practice the corrected concept",
                "Ask about related potential confusions",
                "Request a verification exercise"
            ],
            "challenge": [
                "Attempt the challenge problem",
                "Ask for a hint if needed",
                "Try a harder version",
                "Explain your solution approach"
            ],
            "mentor": [
                "Research industry applications",
                "Connect with professionals in this field",
                "Build a project using this knowledge",
                "Plan your next skill development step"
            ],
            "adaptive": [
                "Practice with an exercise",
                "Explore a real-world example",
                "Ask for a different explanation approach",
                "Move to the next concept"
            ]
        }
        
        return base_actions.get(mode, base_actions["adaptive"])
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from the response content"""
        # Simple keyword extraction - can be enhanced with NLP
        concepts = []
        
        # Look for concepts in content structure
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['concept:', 'key idea:', 'principle:', 'important:']):
                concept = line.strip()
                for prefix in ['concept:', 'key idea:', 'principle:', 'important:', '*', '-', '•']:
                    concept = concept.replace(prefix, '').replace(prefix.upper(), '').strip()
                if concept and len(concept) > 5:
                    concepts.append(concept)
        
        return concepts[:5]  # Limit to 5 concepts
    
    def _determine_next_steps(self, mode: str, session: ChatSession, context: Dict[str, Any]) -> str:
        """Determine intelligent next steps based on learning mode and progress"""
        
        next_steps_map = {
            "socratic": "Continue exploring through guided questions to deepen your understanding",
            "debug": "Practice the corrected concepts and verify your understanding with examples",
            "challenge": "Take on progressively more difficult challenges to build mastery",
            "mentor": "Apply this knowledge in a real project or professional context",
            "adaptive": "Choose your next learning direction based on your interests and goals"
        }
        
        return next_steps_map.get(mode, next_steps_map["adaptive"])
    
    async def set_user_learning_mode(self, user_id: str, preferred_mode: str, preferences: Dict[str, Any]):
        """Set user's preferred learning mode and preferences"""
        self.user_preferences[user_id] = {
            "preferred_mode": preferred_mode,
            "cost_effective": preferences.get("cost_effective", False),
            "difficulty_preference": preferences.get("difficulty_preference", "adaptive"),
            "interaction_style": preferences.get("interaction_style", "collaborative"),
            **preferences
        }
    
    def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get learning analytics for user"""
        return {
            "user_preferences": self.user_preferences.get(user_id, {}),
            "model_usage": self.model_manager.get_usage_analytics(),
            "session_analytics": self.session_analytics.get(user_id, {})
        }

# Global premium AI service instance
premium_ai_service = PremiumAIService()