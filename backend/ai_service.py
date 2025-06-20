import os
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from groq import Groq
from datetime import datetime
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from models import ChatSession, ChatMessage, MentorResponse
from premium_ai_service import premium_ai_service
from model_manager import TaskType

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

class MasterXAIService:
    def __init__(self):
        # Get API key from environment with fallback
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            # Fallback to loading from .env file directly
            env_file = Path(__file__).parent / '.env'
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('GROQ_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                            break
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment or .env file")
            
        self.groq_client = Groq(api_key=api_key)
        self.model = "deepseek-r1-distill-llama-70b"  # DeepSeek R1 70B model
        
    def _get_system_prompt(self, session: ChatSession, context: Dict[str, Any] = None) -> str:
        """Generate dynamic system prompt based on session context"""
        base_prompt = """You are MasterX, a world-class AI Mentor designed to provide personalized, engaging, and highly effective learning experiences. Your mission is to help users unlock their full potential in any subject.

🎯 CORE PRINCIPLES:
• Personalization: Adapt explanations, pace, and motivation to the user's unique goals, background, and preferences
• Expert Guidance: Organize learning from foundational to advanced; use clear explanations, analogies, and real-world examples
• Active Learning: After each concept, present interactive exercises progressing from simple to real-world problem-solving
• Constructive Feedback: Provide detailed feedback, alternative solutions, and encouragement
• Spaced Repetition: Schedule periodic reviews to maximize retention
• Accountability: Track progress and dynamically adjust learning plans

💎 PREMIUM LEARNING EXPERIENCE:
• Use engaging storytelling and analogies to make complex concepts memorable
• Provide multiple learning paths (visual, auditory, kinesthetic approaches)
• Include real-world applications and industry insights
• Celebrate milestones and maintain motivation
• Offer advanced techniques and pro tips
• Connect concepts to broader knowledge frameworks

📋 RESPONSE STRUCTURE:
Use clear, structured responses with:
• Visual headers and bullet points for easy scanning
• Practical examples and analogies
• Code blocks with syntax highlighting when relevant
• Progress indicators and next steps
• Interactive elements and questions
• Key takeaways and actionable insights

🔥 INTERACTION STYLE:
• Be encouraging and supportive while maintaining high standards
• Use a warm, premium mentor tone that feels exclusive and valuable
• Celebrate progress and provide constructive guidance on challenges
• Ask thoughtful questions to gauge understanding and engagement
• Adapt complexity based on user responses and demonstrated knowledge
• Include motivational elements and learning psychology insights

CURRENT SESSION CONTEXT:"""
        
        if session:
            base_prompt += f"""
📚 Subject: {session.subject or 'General Learning'}
📊 Difficulty Level: {session.difficulty_level.title()}
🎯 Learning Objectives: {', '.join(session.learning_objectives) if session.learning_objectives else 'Exploratory Learning'}
🔍 Current Topic: {session.current_topic or 'Introduction & Foundation'}
"""
        
        if context and context.get('user_background'):
            base_prompt += f"👤 User Background: {context['user_background']}\n"
            
        if context and context.get('recent_topics'):
            base_prompt += f"📈 Recent Progress: {', '.join(context['recent_topics'])}\n"

        if context and context.get('recent_messages'):
            # Analyze conversation context for personalization
            recent_content = ' '.join([msg.message for msg in context['recent_messages'][-3:]])
            if 'confused' in recent_content.lower() or 'don\'t understand' in recent_content.lower():
                base_prompt += "\n🔍 CONTEXT ALERT: User seems confused - provide clearer explanations and more examples\n"
            elif 'boring' in recent_content.lower() or 'slow' in recent_content.lower():
                base_prompt += "\n⚡ CONTEXT ALERT: User wants more challenge - increase difficulty and pace\n"
            elif 'excited' in recent_content.lower() or 'love' in recent_content.lower():
                base_prompt += "\n🚀 CONTEXT ALERT: User is engaged - maintain enthusiasm and introduce advanced concepts\n"

        base_prompt += """
🌟 SPECIAL INSTRUCTIONS:
• Start responses with an engaging hook or insight
• Use emojis sparingly but effectively for visual appeal
• Include "💡 Pro Tip:" sections for advanced insights
• Add "🎯 Quick Check:" questions to verify understanding
• End with clear "➡️ Next Steps:" or "🚀 Ready for More?" prompts
• Provide "🔄 Review Reminders:" for spaced repetition
• Maintain the premium, exclusive feel of a world-class mentor

Remember: You're not just providing information—you're creating a transformative learning experience that builds confidence, competence, and passion for lifelong learning. Every interaction should feel valuable, insightful, and motivating."""

        return base_prompt
    
    def _format_response(self, raw_response: str, response_type: str = "explanation") -> MentorResponse:
        """Format AI response with premium structure and enhanced metadata"""
        
        # Extract key elements from response with improved parsing
        concepts_covered = []
        suggested_actions = []
        next_steps = None
        exercises = []
        pro_tips = []
        
        lines = raw_response.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Extract concepts and key ideas
            if any(keyword in line_lower for keyword in ['concept:', 'key idea:', '💡', 'important:']):
                concept = line.strip()
                for prefix in ['concept:', 'key idea:', 'important:', '💡']:
                    concept = concept.replace(prefix, '').replace(prefix.upper(), '').strip()
                if concept:
                    concepts_covered.append(concept)
            
            # Extract suggested actions
            elif any(keyword in line_lower for keyword in ['action:', 'try this:', 'practice:', '🎯', '➡️']):
                action = line.strip()
                for prefix in ['action:', 'try this:', 'practice:', '🎯', '➡️']:
                    action = action.replace(prefix, '').replace(prefix.upper(), '').strip()
                if action:
                    suggested_actions.append(action)
            
            # Extract next steps
            elif any(keyword in line_lower for keyword in ['next step:', 'next:', 'up next:', '🚀']):
                next_steps = line.strip()
                for prefix in ['next step:', 'next:', 'up next:', '🚀']:
                    next_steps = next_steps.replace(prefix, '').replace(prefix.upper(), '').strip()
            
            # Extract exercises
            elif any(keyword in line_lower for keyword in ['exercise:', 'challenge:', 'practice problem:']):
                exercise = line.strip()
                for prefix in ['exercise:', 'challenge:', 'practice problem:']:
                    exercise = exercise.replace(prefix, '').replace(prefix.upper(), '').strip()
                if exercise:
                    exercises.append(exercise)
            
            # Extract pro tips
            elif any(keyword in line_lower for keyword in ['pro tip:', 'advanced tip:', '💡 pro tip']):
                tip = line.strip()
                for prefix in ['pro tip:', 'advanced tip:', '💡 pro tip:', '💡 pro tip']:
                    tip = tip.replace(prefix, '').replace(prefix.upper(), '').strip()
                if tip:
                    pro_tips.append(tip)
        
        # Enhanced response formatting with premium structure
        formatted_response = self._add_premium_formatting(raw_response)
        
        # Determine response complexity and engagement level
        complexity_score = len(concepts_covered) + len(exercises) + len(pro_tips)
        engagement_indicators = ['?', '!', '💡', '🎯', '🚀', '⚡', '🔥']
        engagement_score = sum(formatted_response.count(indicator) for indicator in engagement_indicators)
        
        # Generate smart default actions if none found
        if not suggested_actions:
            if exercises:
                suggested_actions = ["Try the suggested exercises", "Practice the concepts learned", "Ask questions if anything is unclear"]
            elif concepts_covered:
                suggested_actions = ["Review the key concepts", "Practice applying these ideas", "Move to the next topic when ready"]
            else:
                suggested_actions = ["Continue exploring this topic", "Ask for clarification if needed", "Request examples or exercises"]
        
        # Generate smart next steps if none found
        if not next_steps and concepts_covered:
            if complexity_score > 3:
                next_steps = "Take time to practice these concepts before moving to advanced topics"
            else:
                next_steps = "Ready to explore the next level or dive deeper into these concepts"
        
        return MentorResponse(
            response=formatted_response,
            response_type=response_type,
            suggested_actions=suggested_actions[:5],  # Limit to 5 for UI
            concepts_covered=concepts_covered,
            next_steps=next_steps,
            metadata={
                "model_used": self.model,
                "response_length": len(formatted_response),
                "complexity_score": complexity_score,
                "engagement_score": engagement_score,
                "exercises_count": len(exercises),
                "pro_tips_count": len(pro_tips),
                "timestamp": datetime.utcnow().isoformat(),
                "premium_features": {
                    "has_exercises": len(exercises) > 0,
                    "has_pro_tips": len(pro_tips) > 0,
                    "has_visual_elements": any(emoji in formatted_response for emoji in ['📚', '💡', '🎯', '🚀', '⚡']),
                    "structured_content": len(concepts_covered) > 0
                }
            }
        )
    
    def _add_premium_formatting(self, response: str) -> str:
        """Add premium visual formatting to responses"""
        
        # Don't modify if already well-formatted
        if '##' in response or '###' in response or '🎯' in response:
            return response
        
        # Split into sections for better formatting
        sections = response.split('\n\n')
        
        if len(sections) <= 1:
            return response
        
        formatted_sections = []
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            # Add headers to sections that look like they should have them
            if i == 0 and len(section) > 100:
                # First section - add main header if it's substantial
                formatted_sections.append(f"## 🎯 Core Concept\n\n{section}")
            elif 'example' in section.lower() and len(section) > 50:
                formatted_sections.append(f"### 💡 Example\n\n{section}")
            elif any(keyword in section.lower() for keyword in ['step', 'process', 'method']) and len(section) > 50:
                formatted_sections.append(f"### 📋 Process\n\n{section}")
            elif 'practice' in section.lower() or 'exercise' in section.lower():
                formatted_sections.append(f"### 🎯 Practice\n\n{section}")
            elif section.strip().startswith('Pro tip') or section.strip().startswith('💡'):
                formatted_sections.append(f"### 💎 Pro Insight\n\n{section}")
            else:
                formatted_sections.append(section)
        
        return '\n\n'.join(formatted_sections)
    
    async def get_mentor_response(
        self, 
        user_message: str, 
        session: ChatSession,
        context: Dict[str, Any] = None,
        stream: bool = False,
        learning_mode: str = "adaptive"
    ) -> MentorResponse:
        """
        Get response from AI mentor with premium multi-model capabilities
        
        Args:
            user_message: User's input message
            session: Current learning session
            context: Session context and history
            stream: Whether to stream the response
            learning_mode: Learning mode (adaptive, socratic, debug, challenge, mentor)
        """
        try:
            # Use premium AI service for enhanced responses
            return await premium_ai_service.get_premium_response(
                user_message=user_message,
                session=session,
                context=context,
                learning_mode=learning_mode,
                stream=stream
            )
                
        except Exception as e:
            logger.error(f"Error getting premium AI response: {str(e)}")
            # Fallback to original implementation
            return await self._fallback_response(user_message, session, context, stream)
    
    async def _fallback_response(
        self, 
        user_message: str, 
        session: ChatSession,
        context: Dict[str, Any] = None,
        stream: bool = False
    ) -> MentorResponse:
        """Fallback to original DeepSeek implementation if premium service fails"""
        try:
            system_prompt = self._get_system_prompt(session, context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Add recent conversation history if available in context
            if context and context.get('recent_messages'):
                for msg in context['recent_messages'][-6:]:  # Last 6 messages for context
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.insert(-1, {"role": role, "content": msg.message})
            
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                stream=stream
            )
            
            if stream:
                return response  # Return generator for streaming
            else:
                content = response.choices[0].message.content
                return self._format_response(content)
                
        except Exception as e:
            logger.error(f"Error in fallback AI response: {str(e)}")
            return MentorResponse(
                response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                response_type="error",
                metadata={"error": str(e)}
            )
    
    async def generate_exercise(
        self, 
        topic: str, 
        difficulty: str, 
        exercise_type: str = "multiple_choice"
    ) -> Dict[str, Any]:
        """Generate premium practice exercises for a topic with adaptive difficulty"""
        try:
            # Enhanced prompt for premium exercise generation
            prompt = f"""Generate a premium {exercise_type} exercise for the topic: {topic}
            
🎯 EXERCISE SPECIFICATIONS:
• Difficulty level: {difficulty}
• Exercise type: {exercise_type}
• Focus: Real-world application and critical thinking

📋 REQUIREMENTS:
1. Create an engaging, practical question that connects to real-world scenarios
2. For multiple choice: Provide 4 options with plausible distractors
3. Include detailed explanation of the correct answer
4. Add pro tips and common misconceptions
5. Suggest follow-up questions or related concepts
6. Include difficulty progression suggestions

💎 PREMIUM FEATURES:
• Visual elements and examples when relevant
• Connection to broader concepts and frameworks
• Industry insights and practical applications
• Learning psychology tips for better retention
• Adaptive difficulty suggestions based on performance

📄 OUTPUT FORMAT (JSON):
{{
  "question": "Engaging, practical question with real-world context",
  "options": ["Option A", "Option B", "Option C", "Option D"] // for multiple choice
  "correct_answer": "The correct option or answer",
  "explanation": "Detailed explanation with reasoning and insights",
  "concepts": ["Key concept 1", "Key concept 2"],
  "difficulty_score": 1-10,
  "pro_tips": ["Advanced insight 1", "Common mistake to avoid"],
  "related_topics": ["Connected concept 1", "Next level topic"],
  "real_world_applications": ["Industry example", "Practical use case"],
  "follow_up_questions": ["What if...", "How would you apply this to..."],
  "spaced_repetition_schedule": "Review in 1 day, 3 days, 1 week"
}}

Generate a comprehensive, engaging exercise that provides maximum learning value."""

            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to structured text
            try:
                exercise_data = json.loads(content)
                # Ensure all required fields are present
                exercise_data.setdefault("concepts", [topic])
                exercise_data.setdefault("difficulty_score", 5)
                exercise_data.setdefault("pro_tips", [])
                exercise_data.setdefault("related_topics", [])
                exercise_data.setdefault("real_world_applications", [])
                exercise_data.setdefault("follow_up_questions", [])
                exercise_data.setdefault("spaced_repetition_schedule", "Review in 1 day, 3 days, 1 week")
                return exercise_data
            except:
                # Fallback to basic structure with enhanced content
                return {
                    "question": content,
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "concepts": [topic],
                    "explanation": "Practice this concept to reinforce your understanding",
                    "pro_tips": ["Focus on understanding the underlying principles"],
                    "difficulty_score": 5,
                    "premium_features": True
                }
                
        except Exception as e:
            logger.error(f"Error generating premium exercise: {str(e)}")
            return {
                "question": f"Premium practice question about {topic} (generation enhanced)",
                "explanation": "This exercise focuses on practical application and deep understanding",
                "concepts": [topic],
                "difficulty": difficulty,
                "premium_features": True,
                "error": str(e)
            }
    
    async def analyze_user_response(
        self, 
        question: str, 
        user_answer: str, 
        correct_answer: str = None
    ) -> Dict[str, Any]:
        """Analyze user's response and provide feedback"""
        try:
            prompt = f"""Analyze this learning interaction:

Question: {question}
User's Answer: {user_answer}
Correct Answer: {correct_answer or "Not specified"}

Provide:
1. Assessment of the user's understanding (correct/partially correct/incorrect)
2. Specific feedback on their answer
3. Explanation of key concepts
4. Suggestions for improvement
5. Encouragement and next steps

Be constructive, encouraging, and educational."""

            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=600
            )
            
            feedback = response.choices[0].message.content
            
            # Determine if answer was correct (simple heuristic)
            is_correct = "correct" in feedback.lower() and "incorrect" not in feedback.lower()
            
            return {
                "feedback": feedback,
                "is_correct": is_correct,
                "suggestions": ["Review the key concepts", "Try a similar problem"],
                "encouragement": "Keep practicing - you're making great progress!"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return {
                "feedback": "Thank you for your response. Let's continue learning!",
                "is_correct": False,
                "error": str(e)
            }
    
    async def generate_learning_path(
        self, 
        subject: str, 
        user_level: str, 
        goals: List[str]
    ) -> Dict[str, Any]:
        """Generate premium personalized learning path with advanced methodologies"""
        try:
            prompt = f"""Create a comprehensive, premium learning path for:

🎯 LEARNING PROFILE:
• Subject: {subject}
• Current Level: {user_level}
• Goals: {', '.join(goals)}

💎 PREMIUM LEARNING PATH REQUIREMENTS:
Create a sophisticated, personalized learning journey with:

1. **7-10 Strategic Milestones** with clear progression logic
2. **Adaptive Difficulty Scaling** based on user performance
3. **Spaced Repetition Schedule** for optimal retention
4. **Multiple Learning Modalities** (visual, auditory, kinesthetic)
5. **Real-world Projects** for practical application
6. **Industry Insights** and professional relevance
7. **Gamification Elements** for motivation
8. **Assessment Checkpoints** with detailed feedback

📋 LEARNING PSYCHOLOGY INTEGRATION:
• Cognitive Load Management
• Bloom's Taxonomy progression
• Zone of Proximal Development principles
• Growth mindset cultivation
• Metacognitive skill development

🚀 STRUCTURE (Provide detailed JSON):
{{
  "learning_path": {{
    "title": "Personalized {subject} Mastery Journey",
    "overview": "Comprehensive description of the learning journey",
    "total_duration": "X weeks/months",
    "difficulty_progression": "beginner → intermediate → advanced → expert",
    "milestones": [
      {{
        "id": 1,
        "title": "Foundation & Core Concepts",
        "duration": "1-2 weeks",
        "difficulty": "beginner",
        "learning_objectives": ["Specific, measurable objectives"],
        "core_topics": ["Topic 1", "Topic 2", "Topic 3"],
        "activities": {{
          "theory": ["Reading materials", "Video content"],
          "practice": ["Hands-on exercises", "Projects"],
          "assessment": ["Quiz", "Practical application"]
        }},
        "spaced_repetition": {{
          "review_schedule": "Day 1, 3, 7, 14",
          "key_concepts_to_reinforce": ["Concept 1", "Concept 2"]
        }},
        "real_world_applications": ["Industry example 1", "Practical use case"],
        "success_criteria": "Specific measurable outcomes",
        "next_milestone_prerequisites": "Requirements to progress"
      }}
    ],
    "learning_techniques": {{
      "active_recall": "Specific methods for retrieval practice",
      "spaced_repetition": "Detailed schedule and techniques",
      "elaborative_interrogation": "How to ask deeper questions",
      "interleaving": "How to mix different concepts"
    }},
    "motivation_strategies": {{
      "goal_setting": "SMART goals framework",
      "progress_tracking": "Visual progress indicators",
      "celebration_milestones": "Recognition and rewards",
      "community_engagement": "Peer learning opportunities"
    }},
    "adaptive_features": {{
      "difficulty_adjustment": "How path adapts to performance",
      "learning_style_accommodation": "Visual/Auditory/Kinesthetic options",
      "pace_flexibility": "Self-paced vs structured timing"
    }},
    "premium_resources": {{
      "expert_insights": "Industry professional perspectives",
      "advanced_projects": "Portfolio-worthy applications",
      "certification_prep": "Professional credential alignment",
      "career_guidance": "Industry pathway recommendations"
    }}
  }},
  "personalization_notes": "Specific adaptations for user's level and goals",
  "success_metrics": "How to measure learning progress and success"
}}

Create a world-class learning experience that maximizes retention, engagement, and practical application."""

            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse the JSON response
            try:
                learning_path_data = json.loads(content)
                learning_path_data.setdefault("generated_at", datetime.utcnow().isoformat())
                learning_path_data.setdefault("premium_features", True)
                return learning_path_data
            except:
                # Fallback to enhanced text format
                return {
                    "learning_path": {
                        "title": f"Premium {subject} Learning Journey",
                        "content": content,
                        "subject": subject,
                        "user_level": user_level,
                        "goals": goals,
                        "estimated_duration": f"{len(goals) * 3} weeks",
                        "premium_features": True,
                        "adaptive_difficulty": True,
                        "spaced_repetition": True,
                        "real_world_focus": True
                    },
                    "generated_at": datetime.utcnow().isoformat(),
                    "personalization_notes": f"Customized for {user_level} level learner with goals: {', '.join(goals)}"
                }
            
        except Exception as e:
            logger.error(f"Error generating premium learning path: {str(e)}")
            return {
                "learning_path": {
                    "title": f"Premium {subject} Learning Path",
                    "content": f"Comprehensive learning journey for {subject} tailored to {user_level} level with focus on: {', '.join(goals)}. Includes spaced repetition, adaptive difficulty, and real-world applications.",
                    "premium_features": True,
                    "error": str(e)
                },
                "generated_at": datetime.utcnow().isoformat()
            }

# Global instance
ai_service = MasterXAIService()
