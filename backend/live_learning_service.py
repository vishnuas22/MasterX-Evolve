"""
Live Learning Sessions Service for MasterX AI Mentor System

This service provides live learning session capabilities including:
- Voice Interaction
- Screen Sharing
- Live Coding
- Interactive Whiteboards
"""

import logging
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import io
from groq import AsyncGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class SessionType(Enum):
    """Types of live learning sessions"""
    VOICE_INTERACTION = "voice_interaction"
    SCREEN_SHARING = "screen_sharing"
    LIVE_CODING = "live_coding"
    INTERACTIVE_WHITEBOARD = "interactive_whiteboard"
    MIXED_REALITY = "mixed_reality"

class VoiceMode(Enum):
    """Voice interaction modes"""
    CONVERSATION = "conversation"
    DICTATION = "dictation"
    QUESTIONS_ANSWERS = "questions_answers"
    PRONUNCIATION = "pronunciation"

class CodingLanguage(Enum):
    """Supported coding languages for live coding"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    HTML_CSS = "html_css"
    REACT = "react"
    NODE = "node"

@dataclass
class LiveSession:
    """Live learning session data structure"""
    session_id: str
    user_id: str
    session_type: SessionType
    title: str
    description: str
    start_time: datetime
    duration_minutes: int
    status: str
    participants: List[str]
    features_enabled: Dict[str, bool]
    session_data: Dict[str, Any]
    ai_mentor_active: bool
    real_time_feedback: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'session_type': self.session_type.value,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'participants': self.participants,
            'features_enabled': self.features_enabled,
            'session_data': self.session_data,
            'ai_mentor_active': self.ai_mentor_active,
            'real_time_feedback': self.real_time_feedback
        }

class LiveLearningService:
    """Live learning sessions service"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "deepseek-r1-distill-llama-70b"
        
        # Active sessions storage
        self.active_sessions: Dict[str, LiveSession] = {}
        self.session_connections: Dict[str, List[Any]] = {}  # WebSocket connections
        
        # Voice interaction storage
        self.voice_conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Screen sharing data
        self.screen_data: Dict[str, Dict[str, Any]] = {}
        
        # Live coding environments
        self.coding_environments: Dict[str, Dict[str, Any]] = {}
        
        # Interactive whiteboards
        self.whiteboards: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Live Learning Service initialized")

    async def create_live_session(self, 
                                user_id: str, 
                                session_type: SessionType, 
                                title: str, 
                                duration_minutes: int = 60,
                                features: Dict[str, bool] = None) -> LiveSession:
        """Create a new live learning session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Default features
            default_features = {
                'ai_mentor': True,
                'real_time_feedback': True,
                'screen_sharing': False,
                'voice_interaction': False,
                'collaborative_editing': False,
                'whiteboard': False,
                'code_execution': False
            }
            
            if features:
                default_features.update(features)
            
            # Session-specific configurations
            session_data = {}
            if session_type == SessionType.VOICE_INTERACTION:
                session_data = {
                    'voice_mode': VoiceMode.CONVERSATION.value,
                    'language': 'en-US',
                    'speech_rate': 1.0,
                    'voice_settings': {
                        'pitch': 0,
                        'speed': 1.0,
                        'volume': 0.8
                    }
                }
                default_features['voice_interaction'] = True
                
            elif session_type == SessionType.LIVE_CODING:
                session_data = {
                    'coding_language': CodingLanguage.PYTHON.value,
                    'environment': 'interactive',
                    'auto_save': True,
                    'syntax_highlighting': True,
                    'real_time_compilation': True
                }
                default_features['code_execution'] = True
                default_features['collaborative_editing'] = True
                
            elif session_type == SessionType.INTERACTIVE_WHITEBOARD:
                session_data = {
                    'canvas_size': {'width': 1920, 'height': 1080},
                    'tools_enabled': ['pen', 'eraser', 'shapes', 'text', 'images'],
                    'collaboration_mode': 'real_time',
                    'auto_save_interval': 30
                }
                default_features['whiteboard'] = True
                
            elif session_type == SessionType.SCREEN_SHARING:
                session_data = {
                    'sharing_mode': 'full_screen',
                    'annotation_enabled': True,
                    'recording_enabled': False,
                    'quality': 'high'
                }
                default_features['screen_sharing'] = True
            
            # Create session
            live_session = LiveSession(
                session_id=session_id,
                user_id=user_id,
                session_type=session_type,
                title=title,
                description=f"Live {session_type.value.replace('_', ' ').title()} Session",
                start_time=datetime.now(),
                duration_minutes=duration_minutes,
                status='active',
                participants=[user_id],
                features_enabled=default_features,
                session_data=session_data,
                ai_mentor_active=True,
                real_time_feedback=True
            )
            
            self.active_sessions[session_id] = live_session
            self.session_connections[session_id] = []
            
            # Initialize session-specific data
            if session_type == SessionType.VOICE_INTERACTION:
                self.voice_conversations[session_id] = []
            elif session_type == SessionType.LIVE_CODING:
                self.coding_environments[session_id] = {
                    'code': '',
                    'output': '',
                    'errors': [],
                    'history': []
                }
            elif session_type == SessionType.INTERACTIVE_WHITEBOARD:
                self.whiteboards[session_id] = {
                    'elements': [],
                    'history': [],
                    'collaborators': {}
                }
            elif session_type == SessionType.SCREEN_SHARING:
                self.screen_data[session_id] = {
                    'current_frame': None,
                    'annotations': [],
                    'analysis': {}
                }
            
            logger.info(f"Created live session {session_id} of type {session_type.value}")
            return live_session
            
        except Exception as e:
            logger.error(f"Error creating live session: {str(e)}")
            raise

    async def handle_voice_interaction(self, session_id: str, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """Handle voice interaction in live session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.session_type != SessionType.VOICE_INTERACTION:
                raise ValueError("Invalid voice interaction session")
            
            # Simulate speech-to-text (in production, use actual STT service)
            # For now, we'll simulate with a text message
            transcribed_text = "User said something about learning programming"  # Placeholder
            
            # Add to conversation history
            if session_id not in self.voice_conversations:
                self.voice_conversations[session_id] = []
            
            self.voice_conversations[session_id].append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'type': 'speech',
                'content': transcribed_text,
                'audio_duration': len(audio_data) / 16000  # Approximate duration
            })
            
            # Generate AI mentor response
            mentor_response = await self._generate_voice_response(session_id, transcribed_text)
            
            # Add mentor response to conversation
            self.voice_conversations[session_id].append({
                'timestamp': datetime.now().isoformat(),
                'user_id': 'ai_mentor',
                'type': 'response',
                'content': mentor_response['text'],
                'audio_generated': True
            })
            
            return {
                'transcribed_text': transcribed_text,
                'mentor_response': mentor_response,
                'conversation_context': self.voice_conversations[session_id][-5:],
                'session_insights': await self._analyze_voice_session(session_id)
            }
            
        except Exception as e:
            logger.error(f"Error handling voice interaction: {str(e)}")
            return {'error': str(e)}

    async def handle_screen_sharing(self, session_id: str, screen_data: bytes, user_id: str) -> Dict[str, Any]:
        """Handle screen sharing and analysis"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.session_type != SessionType.SCREEN_SHARING:
                raise ValueError("Invalid screen sharing session")
            
            # Store current frame
            if session_id not in self.screen_data:
                self.screen_data[session_id] = {
                    'current_frame': None,
                    'annotations': [],
                    'analysis': {}
                }
            
            # Convert screen data to base64 for storage
            screen_base64 = base64.b64encode(screen_data).decode('utf-8')
            self.screen_data[session_id]['current_frame'] = screen_base64
            
            # Analyze screen content (AI-powered)
            analysis = await self._analyze_screen_content(session_id, screen_data)
            
            # Generate real-time feedback
            feedback = await self._generate_screen_feedback(session_id, analysis)
            
            return {
                'analysis': analysis,
                'feedback': feedback,
                'annotations': self.screen_data[session_id]['annotations'],
                'suggestions': await self._generate_screen_suggestions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Error handling screen sharing: {str(e)}")
            return {'error': str(e)}

    async def handle_live_coding(self, session_id: str, code_update: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle live coding session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.session_type != SessionType.LIVE_CODING:
                raise ValueError("Invalid live coding session")
            
            if session_id not in self.coding_environments:
                self.coding_environments[session_id] = {
                    'code': '',
                    'output': '',
                    'errors': [],
                    'history': []
                }
            
            env = self.coding_environments[session_id]
            
            # Update code
            new_code = code_update.get('code', '')
            language = code_update.get('language', session.session_data.get('coding_language', 'python'))
            
            # Store in history
            env['history'].append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'code': new_code,
                'change_type': code_update.get('change_type', 'edit')
            })
            
            env['code'] = new_code
            
            # Analyze code in real-time
            code_analysis = await self._analyze_code(new_code, language)
            
            # Execute code if requested
            execution_result = None
            if code_update.get('execute', False):
                execution_result = await self._execute_code(new_code, language)
                env['output'] = execution_result.get('output', '')
                env['errors'] = execution_result.get('errors', [])
            
            # Generate AI mentor feedback
            mentor_feedback = await self._generate_coding_feedback(session_id, code_analysis, execution_result)
            
            return {
                'code_analysis': code_analysis,
                'execution_result': execution_result,
                'mentor_feedback': mentor_feedback,
                'environment_state': env,
                'suggestions': await self._generate_coding_suggestions(new_code, language)
            }
            
        except Exception as e:
            logger.error(f"Error handling live coding: {str(e)}")
            return {'error': str(e)}

    async def handle_interactive_whiteboard(self, session_id: str, whiteboard_update: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle interactive whiteboard session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.session_type != SessionType.INTERACTIVE_WHITEBOARD:
                raise ValueError("Invalid whiteboard session")
            
            if session_id not in self.whiteboards:
                self.whiteboards[session_id] = {
                    'elements': [],
                    'history': [],
                    'collaborators': {}
                }
            
            whiteboard = self.whiteboards[session_id]
            
            # Process whiteboard update
            update_type = whiteboard_update.get('type', 'draw')
            
            if update_type == 'draw':
                element = {
                    'id': str(uuid.uuid4()),
                    'type': 'path',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'data': whiteboard_update.get('data', {}),
                    'style': whiteboard_update.get('style', {})
                }
                whiteboard['elements'].append(element)
                
            elif update_type == 'text':
                element = {
                    'id': str(uuid.uuid4()),
                    'type': 'text',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'content': whiteboard_update.get('content', ''),
                    'position': whiteboard_update.get('position', {'x': 0, 'y': 0}),
                    'style': whiteboard_update.get('style', {})
                }
                whiteboard['elements'].append(element)
                
            elif update_type == 'shape':
                element = {
                    'id': str(uuid.uuid4()),
                    'type': 'shape',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'shape_type': whiteboard_update.get('shape_type', 'rectangle'),
                    'bounds': whiteboard_update.get('bounds', {}),
                    'style': whiteboard_update.get('style', {})
                }
                whiteboard['elements'].append(element)
            
            # Add to history
            whiteboard['history'].append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'action': update_type,
                'element_id': element['id'] if 'element' in locals() else None
            })
            
            # Analyze whiteboard content
            content_analysis = await self._analyze_whiteboard_content(session_id)
            
            # Generate AI suggestions
            ai_suggestions = await self._generate_whiteboard_suggestions(session_id, content_analysis)
            
            return {
                'whiteboard_state': whiteboard,
                'content_analysis': content_analysis,
                'ai_suggestions': ai_suggestions,
                'collaboration_insights': self._get_collaboration_insights(session_id)
            }
            
        except Exception as e:
            logger.error(f"Error handling whiteboard: {str(e)}")
            return {'error': str(e)}

    async def _generate_voice_response(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate AI mentor voice response"""
        try:
            conversation_history = self.voice_conversations.get(session_id, [])
            context = "\n".join([f"{msg['user_id']}: {msg['content']}" for msg in conversation_history[-5:]])
            
            prompt = f"""
            You are an AI mentor in a live voice interaction session. Respond to the user's spoken input naturally and conversationally.
            
            Conversation Context:
            {context}
            
            User Input: "{user_input}"
            
            Provide a helpful, encouraging, and conversational response that:
            1. Addresses their question or comment directly
            2. Uses natural speech patterns suitable for voice
            3. Includes appropriate pauses and emphasis
            4. Provides actionable learning guidance
            5. Maintains an encouraging tone
            
            Keep responses concise but informative (30-60 seconds when spoken).
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            text_response = response.choices[0].message.content
            
            return {
                'text': text_response,
                'audio_duration_estimate': len(text_response.split()) / 2.5,  # Approximate speaking time
                'emphasis_points': self._identify_emphasis_points(text_response),
                'suggested_pace': 'moderate'
            }
            
        except Exception as e:
            logger.error(f"Error generating voice response: {str(e)}")
            return {'text': "I'm having trouble responding right now. Could you please repeat that?"}

    async def _analyze_screen_content(self, session_id: str, screen_data: bytes) -> Dict[str, Any]:
        """Analyze screen content using AI"""
        try:
            # In production, this would use computer vision APIs
            # For now, we'll simulate analysis
            analysis = {
                'content_type': 'code_editor',
                'detected_elements': ['text_editor', 'terminal', 'browser'],
                'programming_language': 'python',
                'complexity_level': 'intermediate',
                'potential_issues': [],
                'learning_opportunities': [
                    'Code structure optimization',
                    'Best practices implementation',
                    'Debugging techniques'
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing screen content: {str(e)}")
            return {}

    async def _generate_screen_feedback(self, session_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real-time feedback for screen sharing"""
        try:
            feedback_prompt = f"""
            Analyze the user's screen content and provide real-time learning feedback.
            
            Screen Analysis: {json.dumps(analysis)}
            
            Provide constructive feedback that includes:
            1. What the user is doing well
            2. Areas for improvement
            3. Specific suggestions
            4. Next steps
            
            Keep feedback encouraging and actionable.
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": feedback_prompt}],
                temperature=0.6,
                max_tokens=300
            )
            
            return {
                'feedback_text': response.choices[0].message.content,
                'priority': 'medium',
                'action_required': False,
                'suggested_improvements': analysis.get('learning_opportunities', [])
            }
            
        except Exception as e:
            logger.error(f"Error generating screen feedback: {str(e)}")
            return {'feedback_text': 'Continue with your current work. You\'re doing great!'}

    async def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code in real-time"""
        try:
            analysis_prompt = f"""
            Analyze this {language} code for learning purposes:
            
            ```{language}
            {code}
            ```
            
            Provide analysis including:
            - Code quality assessment
            - Potential improvements
            - Best practices recommendations
            - Learning insights
            
            Return as JSON with structure:
            {{
                "quality_score": 0.8,
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"],
                "concepts": ["concept1", "concept2"],
                "difficulty_level": "intermediate"
            }}
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except:
                return {
                    "quality_score": 0.7,
                    "strengths": ["Code is readable"],
                    "improvements": ["Consider adding comments"],
                    "concepts": ["Basic programming"],
                    "difficulty_level": "beginner"
                }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {}

    async def _execute_code(self, code: str, language: str) -> Dict[str, Any]:
        """Execute code safely (simulated)"""
        try:
            # In production, this would use secure code execution environment
            # For now, we'll simulate execution results
            
            if language == 'python':
                if 'print(' in code:
                    output = "Hello, World!"  # Simulated output
                    errors = []
                elif 'import' in code:
                    output = "Modules imported successfully"
                    errors = []
                else:
                    output = "Code executed successfully"
                    errors = []
            else:
                output = f"Code executed in {language}"
                errors = []
            
            return {
                'output': output,
                'errors': errors,
                'execution_time': 0.05,
                'memory_usage': '2.1 MB'
            }
            
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return {
                'output': '',
                'errors': [str(e)],
                'execution_time': 0,
                'memory_usage': '0 MB'
            }

    async def _generate_coding_feedback(self, session_id: str, analysis: Dict[str, Any], execution: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI mentor feedback for coding"""
        try:
            feedback_prompt = f"""
            Provide mentoring feedback for a live coding session.
            
            Code Analysis: {json.dumps(analysis)}
            Execution Result: {json.dumps(execution) if execution else 'No execution'}
            
            Provide encouraging and educational feedback that:
            1. Celebrates what's working well
            2. Guides improvement gently
            3. Suggests next learning steps
            4. Maintains motivation
            
            Keep it conversational and supportive.
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": feedback_prompt}],
                temperature=0.7,
                max_tokens=250
            )
            
            return {
                'feedback': response.choices[0].message.content,
                'encouragement_level': 'high',
                'learning_focus': analysis.get('concepts', []),
                'next_steps': ['Continue practicing', 'Try adding complexity']
            }
            
        except Exception as e:
            logger.error(f"Error generating coding feedback: {str(e)}")
            return {'feedback': 'Great work! Keep coding and learning!'}

    async def _analyze_whiteboard_content(self, session_id: str) -> Dict[str, Any]:
        """Analyze whiteboard content"""
        try:
            whiteboard = self.whiteboards.get(session_id, {})
            elements = whiteboard.get('elements', [])
            
            # Analyze content patterns
            text_elements = [e for e in elements if e['type'] == 'text']
            shape_elements = [e for e in elements if e['type'] == 'shape']
            drawing_elements = [e for e in elements if e['type'] == 'path']
            
            analysis = {
                'total_elements': len(elements),
                'text_count': len(text_elements),
                'shape_count': len(shape_elements),
                'drawing_count': len(drawing_elements),
                'collaboration_level': len(set(e['user_id'] for e in elements)),
                'content_categories': self._categorize_whiteboard_content(elements),
                'complexity_score': min(1.0, len(elements) / 20.0)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing whiteboard content: {str(e)}")
            return {}

    def _categorize_whiteboard_content(self, elements: List[Dict[str, Any]]) -> List[str]:
        """Categorize whiteboard content"""
        categories = []
        
        text_contents = [e.get('content', '') for e in elements if e['type'] == 'text']
        all_text = ' '.join(text_contents).lower()
        
        if any(word in all_text for word in ['function', 'variable', 'code', 'algorithm']):
            categories.append('programming')
        if any(word in all_text for word in ['math', 'equation', 'formula', 'calculate']):
            categories.append('mathematics')
        if any(word in all_text for word in ['diagram', 'flow', 'process', 'step']):
            categories.append('process_mapping')
        if len([e for e in elements if e['type'] == 'shape']) > 3:
            categories.append('visual_design')
        
        return categories or ['general']

    async def _generate_whiteboard_suggestions(self, session_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI suggestions for whiteboard"""
        try:
            suggestions_prompt = f"""
            Analyze whiteboard usage and provide helpful suggestions.
            
            Whiteboard Analysis: {json.dumps(analysis)}
            
            Suggest improvements for:
            1. Organization and structure
            2. Visual clarity
            3. Learning effectiveness
            4. Collaboration enhancement
            
            Provide actionable suggestions.
            """
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": suggestions_prompt}],
                temperature=0.6,
                max_tokens=200
            )
            
            return {
                'suggestions': response.choices[0].message.content,
                'priority_actions': ['Organize content', 'Add labels'],
                'collaboration_tips': ['Use different colors for different contributors']
            }
            
        except Exception as e:
            logger.error(f"Error generating whiteboard suggestions: {str(e)}")
            return {'suggestions': 'Keep up the great visual thinking!'}

    def _identify_emphasis_points(self, text: str) -> List[Dict[str, Any]]:
        """Identify points that need emphasis in speech"""
        emphasis_points = []
        
        # Look for important words/phrases
        important_words = ['important', 'key', 'remember', 'crucial', 'essential']
        
        for word in important_words:
            if word in text.lower():
                emphasis_points.append({
                    'word': word,
                    'type': 'emphasis',
                    'strength': 'strong'
                })
        
        return emphasis_points

    async def _analyze_voice_session(self, session_id: str) -> Dict[str, Any]:
        """Analyze voice session patterns"""
        try:
            conversation = self.voice_conversations.get(session_id, [])
            
            user_messages = [msg for msg in conversation if msg['user_id'] != 'ai_mentor']
            ai_messages = [msg for msg in conversation if msg['user_id'] == 'ai_mentor']
            
            insights = {
                'total_exchanges': len(conversation) // 2,
                'user_engagement': len(user_messages),
                'avg_response_length': sum(len(msg['content']) for msg in ai_messages) / max(len(ai_messages), 1),
                'session_duration': self._calculate_session_duration(conversation),
                'learning_momentum': 'high' if len(conversation) > 10 else 'moderate'
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing voice session: {str(e)}")
            return {}

    def _calculate_session_duration(self, conversation: List[Dict[str, Any]]) -> float:
        """Calculate session duration in minutes"""
        if len(conversation) < 2:
            return 0.0
        
        start_time = datetime.fromisoformat(conversation[0]['timestamp'])
        end_time = datetime.fromisoformat(conversation[-1]['timestamp'])
        
        duration = (end_time - start_time).total_seconds() / 60.0
        return round(duration, 2)

    async def _generate_screen_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on screen analysis"""
        suggestions = []
        
        if analysis.get('content_type') == 'code_editor':
            suggestions.extend([
                'Consider adding more comments to your code',
                'Try breaking down complex functions into smaller ones',
                'Use meaningful variable names for better readability'
            ])
        
        if 'terminal' in analysis.get('detected_elements', []):
            suggestions.extend([
                'Practice using keyboard shortcuts for efficiency',
                'Try using command history for repeated commands'
            ])
        
        return suggestions

    async def _generate_coding_suggestions(self, code: str, language: str) -> List[str]:
        """Generate coding suggestions"""
        suggestions = []
        
        if language == 'python':
            if 'def ' not in code and len(code) > 50:
                suggestions.append('Consider organizing code into functions')
            if '#' not in code:
                suggestions.append('Add comments to explain your logic')
            if 'import' not in code and 'print' in code:
                suggestions.append('Explore using Python libraries for enhanced functionality')
        
        return suggestions

    def _get_collaboration_insights(self, session_id: str) -> Dict[str, Any]:
        """Get collaboration insights for whiteboard"""
        whiteboard = self.whiteboards.get(session_id, {})
        elements = whiteboard.get('elements', [])
        
        user_contributions = {}
        for element in elements:
            user_id = element['user_id']
            if user_id not in user_contributions:
                user_contributions[user_id] = 0
            user_contributions[user_id] += 1
        
        return {
            'active_collaborators': len(user_contributions),
            'contribution_distribution': user_contributions,
            'collaboration_balance': 'balanced' if len(set(user_contributions.values())) <= 2 else 'unbalanced'
        }

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return session.to_dict()

    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a live session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {'error': 'Session not found'}
            
            session.status = 'completed'
            
            # Generate session summary
            summary = await self._generate_session_summary(session_id)
            
            # Clean up session data
            if session_id in self.session_connections:
                del self.session_connections[session_id]
            
            return {
                'session_summary': summary,
                'status': 'completed',
                'message': 'Session ended successfully'
            }
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {'error': str(e)}

    async def _generate_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {}
            
            summary = {
                'session_type': session.session_type.value,
                'duration': (datetime.now() - session.start_time).total_seconds() / 60.0,
                'participants': len(session.participants),
                'features_used': [k for k, v in session.features_enabled.items() if v],
                'key_achievements': [],
                'learning_insights': {},
                'recommendations': []
            }
            
            # Type-specific summaries
            if session.session_type == SessionType.VOICE_INTERACTION:
                conversation = self.voice_conversations.get(session_id, [])
                summary['total_exchanges'] = len(conversation) // 2
                summary['key_achievements'].append(f"Completed {len(conversation)} voice interactions")
                
            elif session.session_type == SessionType.LIVE_CODING:
                env = self.coding_environments.get(session_id, {})
                summary['lines_of_code'] = len(env.get('code', '').split('\n'))
                summary['key_achievements'].append("Practiced live coding with AI mentor")
                
            elif session.session_type == SessionType.INTERACTIVE_WHITEBOARD:
                whiteboard = self.whiteboards.get(session_id, {})
                summary['elements_created'] = len(whiteboard.get('elements', []))
                summary['key_achievements'].append("Created visual learning content")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating session summary: {str(e)}")
            return {}

# Create global instance
live_learning_service = LiveLearningService()