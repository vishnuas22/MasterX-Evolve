"""
Premium Multi-Model AI Manager for MasterX Learning Platform
Intelligently selects the best available model for each learning task
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Supported AI model providers"""
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class TaskType(Enum):
    """Different types of learning tasks that require specific model capabilities"""
    EXPLANATION = "explanation"  # General concept explanation
    SOCRATIC = "socratic"  # Questioning-based learning
    DEBUG = "debug"  # Finding knowledge gaps
    CHALLENGE = "challenge"  # Progressive difficulty problems
    MENTOR = "mentor"  # Professional guidance
    CREATIVE = "creative"  # Creative learning and analogies
    ANALYSIS = "analysis"  # Code/text analysis
    EXERCISE = "exercise"  # Exercise generation
    ASSESSMENT = "assessment"  # Performance evaluation
    VOICE = "voice"  # Voice interaction optimized
    MULTIMODAL = "multimodal"  # Image/text combined

@dataclass
class ModelConfig:
    """Configuration for each AI model"""
    provider: ModelProvider
    model_name: str
    max_tokens: int
    temperature: float
    strength_score: int  # 1-10 rating for different tasks
    task_specialties: List[TaskType]
    cost_per_token: float
    api_key_env: str
    available: bool = False

class ModelRegistry:
    """Registry of all supported models with intelligent selection"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self._check_availability()
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize all supported models with their capabilities"""
        return {
            # DeepSeek R1 70B (Currently Available)
            "deepseek-r1": ModelConfig(
                provider=ModelProvider.GROQ,
                model_name="deepseek-r1-distill-llama-70b",
                max_tokens=2000,
                temperature=0.7,
                strength_score=9,  # Excellent for reasoning and learning
                task_specialties=[
                    TaskType.EXPLANATION, TaskType.SOCRATIC, TaskType.DEBUG,
                    TaskType.CHALLENGE, TaskType.MENTOR, TaskType.EXERCISE
                ],
                cost_per_token=0.00001,  # Very cost effective
                api_key_env="GROQ_API_KEY"
            ),
            
            # Claude 3.5 Sonnet (To be added)
            "claude-sonnet": ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.6,
                strength_score=10,  # Best for complex reasoning and mentoring
                task_specialties=[
                    TaskType.MENTOR, TaskType.SOCRATIC, TaskType.ANALYSIS,
                    TaskType.CREATIVE, TaskType.DEBUG, TaskType.ASSESSMENT
                ],
                cost_per_token=0.00003,
                api_key_env="ANTHROPIC_API_KEY"
            ),
            
            # GPT-4o (To be added)
            "gpt-4o": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                max_tokens=4000,
                temperature=0.7,
                strength_score=9,  # Excellent for creative and comprehensive explanations
                task_specialties=[
                    TaskType.CREATIVE, TaskType.EXPLANATION, TaskType.EXERCISE,
                    TaskType.MULTIMODAL, TaskType.VOICE
                ],
                cost_per_token=0.00005,
                api_key_env="OPENAI_API_KEY"
            ),
            
            # Gemini Pro (To be added)
            "gemini-pro": ModelConfig(
                provider=ModelProvider.GOOGLE,
                model_name="gemini-1.5-pro",
                max_tokens=3000,
                temperature=0.8,
                strength_score=8,  # Good for multimodal and creative tasks
                task_specialties=[
                    TaskType.MULTIMODAL, TaskType.CREATIVE, TaskType.EXPLANATION,
                    TaskType.VOICE
                ],
                cost_per_token=0.00002,
                api_key_env="GOOGLE_API_KEY"
            )
        }
    
    def _check_availability(self):
        """Check which models are available based on API keys"""
        for model_id, config in self.models.items():
            api_key = os.environ.get(config.api_key_env)
            config.available = bool(api_key and api_key.strip())
            if config.available:
                logger.info(f"Model {model_id} is available")
            else:
                logger.info(f"Model {model_id} is not available (missing API key: {config.api_key_env})")
    
    def get_best_model(self, task_type: TaskType, prefer_cost_effective: bool = False) -> Optional[ModelConfig]:
        """
        Select the best available model for a specific task
        
        Args:
            task_type: The type of learning task
            prefer_cost_effective: If True, prefer lower cost models when quality is similar
        
        Returns:
            Best available model config or None if no models available
        """
        available_models = [model for model in self.models.values() if model.available]
        
        if not available_models:
            logger.error("No AI models available!")
            return None
        
        # Filter models that specialize in this task type
        specialized_models = [
            model for model in available_models 
            if task_type in model.task_specialties
        ]
        
        # If no specialized models, use all available models
        candidate_models = specialized_models if specialized_models else available_models
        
        # Sort by strength score (and cost if preferred)
        if prefer_cost_effective:
            # Balance quality and cost
            candidate_models.sort(
                key=lambda m: (m.strength_score * 10 - m.cost_per_token * 1000000), 
                reverse=True
            )
        else:
            # Prefer highest quality
            candidate_models.sort(key=lambda m: m.strength_score, reverse=True)
        
        selected_model = candidate_models[0]
        logger.info(f"Selected model {selected_model.model_name} for task {task_type.value}")
        return selected_model
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return [
            model_id for model_id, config in self.models.items() 
            if config.available
        ]
    
    def add_model_key(self, provider: str, api_key: str) -> bool:
        """
        Add a new API key and check for newly available models
        
        Args:
            provider: The provider name (groq, openai, anthropic, google)
            api_key: The API key to add
        
        Returns:
            True if new models became available
        """
        provider_env_map = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY"
        }
        
        env_key = provider_env_map.get(provider.lower())
        if not env_key:
            return False
        
        # Set environment variable
        os.environ[env_key] = api_key
        
        # Recheck availability
        old_available = self.get_available_models()
        self._check_availability()
        new_available = self.get_available_models()
        
        newly_available = set(new_available) - set(old_available)
        if newly_available:
            logger.info(f"New models available: {newly_available}")
            return True
        
        return False

class PremiumModelManager:
    """
    Premium AI Model Manager with intelligent task routing and advanced features
    """
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.clients = {}
        self._initialize_clients()
        
        # Performance tracking
        self.model_performance = {}
        self.usage_stats = {}
    
    def _initialize_clients(self):
        """Initialize API clients for available models"""
        for model_id, config in self.registry.models.items():
            if config.available:
                try:
                    if config.provider == ModelProvider.GROQ:
                        from groq import Groq
                        self.clients[model_id] = Groq(
                            api_key=os.environ.get(config.api_key_env)
                        )
                    elif config.provider == ModelProvider.OPENAI:
                        # Will be initialized when OpenAI key is added
                        pass
                    elif config.provider == ModelProvider.ANTHROPIC:
                        # Will be initialized when Anthropic key is added
                        pass
                    elif config.provider == ModelProvider.GOOGLE:
                        # Will be initialized when Google key is added
                        pass
                        
                    logger.info(f"Initialized client for {model_id}")
                except Exception as e:
                    logger.error(f"Failed to initialize client for {model_id}: {e}")
    
    async def get_optimized_response(
        self, 
        prompt: str, 
        task_type: TaskType,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Get AI response using the best available model for the task
        
        Args:
            prompt: User input prompt
            task_type: Type of learning task
            system_prompt: System prompt (will be optimized for selected model)
            context: Additional context for the conversation
            stream: Whether to stream the response
            user_preferences: User preferences for model selection
        
        Returns:
            AI response optimized for the task type
        """
        # Select best model for this task
        prefer_cost_effective = user_preferences and user_preferences.get('cost_effective', False)
        model_config = self.registry.get_best_model(task_type, prefer_cost_effective)
        
        if not model_config:
            raise Exception("No AI models available")
        
        # Get optimized system prompt for the task type and model
        optimized_system_prompt = self._get_optimized_system_prompt(
            task_type, model_config, system_prompt, context
        )
        
        # Track usage
        self._track_usage(model_config.model_name, task_type)
        
        try:
            # Route to appropriate model
            if model_config.provider == ModelProvider.GROQ:
                return await self._call_groq_model(
                    model_config, optimized_system_prompt, prompt, stream, context
                )
            elif model_config.provider == ModelProvider.OPENAI:
                return await self._call_openai_model(
                    model_config, optimized_system_prompt, prompt, stream, context
                )
            elif model_config.provider == ModelProvider.ANTHROPIC:
                return await self._call_anthropic_model(
                    model_config, optimized_system_prompt, prompt, stream, context
                )
            elif model_config.provider == ModelProvider.GOOGLE:
                return await self._call_google_model(
                    model_config, optimized_system_prompt, prompt, stream, context
                )
            else:
                raise Exception(f"Unsupported provider: {model_config.provider}")
                
        except Exception as e:
            logger.error(f"Error calling model {model_config.model_name}: {e}")
            # Try fallback to any available model
            return await self._fallback_response(prompt, system_prompt, stream)
    
    def _get_optimized_system_prompt(
        self, 
        task_type: TaskType, 
        model_config: ModelConfig,
        base_system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate optimized system prompt based on task type and model capabilities"""
        
        task_prompts = {
            TaskType.SOCRATIC: """You are a Socratic tutor who guides learning through thoughtful questions. Instead of giving direct answers, ask probing questions that help the user discover the solution themselves. Build on their responses with deeper questions that reveal underlying principles.""",
            
            TaskType.DEBUG: """You are a debugging mentor who helps identify knowledge gaps and misconceptions. Analyze the user's understanding, identify specific areas of confusion, and provide targeted clarification. Focus on fixing fundamental misunderstandings.""",
            
            TaskType.CHALLENGE: """You are a challenge designer who provides progressively difficult problems. Start with the user's current level and gradually increase complexity. Provide hints when needed but maintain appropriate difficulty to promote growth.""",
            
            TaskType.MENTOR: """You are a senior professional mentor providing industry-level guidance. Share practical insights, real-world applications, and professional best practices. Connect learning to career advancement and practical value.""",
            
            TaskType.CREATIVE: """You are a creative learning facilitator who uses innovative analogies, storytelling, and imaginative examples. Make complex concepts memorable through creative connections and engaging narratives.""",
            
            TaskType.ANALYSIS: """You are an analytical expert who breaks down complex problems systematically. Provide structured analysis, identify patterns, and guide through logical reasoning processes step by step.""",
            
            TaskType.EXERCISE: """You are an exercise designer who creates engaging, practical problems that reinforce learning. Design exercises that are challenging but achievable, with clear learning objectives and real-world relevance.""",
            
            TaskType.ASSESSMENT: """You are an assessment specialist who evaluates understanding and provides constructive feedback. Identify strengths and areas for improvement with specific, actionable guidance for progress."""
        }
        
        # Get task-specific prompt
        task_prompt = task_prompts.get(task_type, "")
        
        # Combine with base system prompt
        if base_system_prompt:
            combined_prompt = f"{base_system_prompt}\n\n{task_prompt}"
        else:
            combined_prompt = task_prompt
        
        # Add model-specific optimizations
        if model_config.provider == ModelProvider.GROQ:
            # DeepSeek R1 responds well to structured thinking prompts
            combined_prompt += "\n\nUse step-by-step reasoning and provide structured, educational responses with clear learning objectives."
        elif model_config.provider == ModelProvider.ANTHROPIC:
            # Claude excels with detailed reasoning
            combined_prompt += "\n\nProvide detailed reasoning and comprehensive analysis. Consider multiple perspectives and edge cases."
        elif model_config.provider == ModelProvider.OPENAI:
            # GPT-4 is great for creative and engaging responses
            combined_prompt += "\n\nMake responses engaging and creative while maintaining educational value. Use examples and analogies."
        
        return combined_prompt
    
    async def _call_groq_model(
        self, 
        model_config: ModelConfig, 
        system_prompt: str, 
        user_prompt: str, 
        stream: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call Groq model (DeepSeek R1)"""
        client = self.clients.get("deepseek-r1")
        if not client:
            raise Exception("Groq client not initialized")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Add context messages if available
        if context and context.get('recent_messages'):
            for msg in context['recent_messages'][-6:]:  # Last 6 messages
                role = "user" if msg.sender == "user" else "assistant"
                messages.insert(-1, {"role": role, "content": msg.message})
        
        response = client.chat.completions.create(
            model=model_config.model_name,
            messages=messages,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            stream=stream
        )
        
        return response
    
    async def _call_openai_model(self, model_config: ModelConfig, system_prompt: str, user_prompt: str, stream: bool, context: Optional[Dict[str, Any]] = None):
        """Call OpenAI model (GPT-4o) - Will be implemented when API key is added"""
        # TODO: Implement when OpenAI API key is provided
        raise Exception("OpenAI integration will be implemented when API key is provided")
    
    async def _call_anthropic_model(self, model_config: ModelConfig, system_prompt: str, user_prompt: str, stream: bool, context: Optional[Dict[str, Any]] = None):
        """Call Anthropic model (Claude) - Will be implemented when API key is added"""
        # TODO: Implement when Anthropic API key is provided
        raise Exception("Anthropic integration will be implemented when API key is provided")
    
    async def _call_google_model(self, model_config: ModelConfig, system_prompt: str, user_prompt: str, stream: bool, context: Optional[Dict[str, Any]] = None):
        """Call Google model (Gemini) - Will be implemented when API key is added"""
        # TODO: Implement when Google API key is provided
        raise Exception("Google integration will be implemented when API key is provided")
    
    async def _fallback_response(self, prompt: str, system_prompt: Optional[str], stream: bool) -> Any:
        """Fallback to any available model when primary selection fails"""
        available_models = self.registry.get_available_models()
        if not available_models:
            raise Exception("No fallback models available")
        
        # Use the first available model as fallback
        fallback_config = next(
            config for config in self.registry.models.values() 
            if config.available
        )
        
        logger.warning(f"Using fallback model: {fallback_config.model_name}")
        return await self._call_groq_model(fallback_config, system_prompt or "", prompt, stream)
    
    def _track_usage(self, model_name: str, task_type: TaskType):
        """Track model usage for analytics"""
        if model_name not in self.usage_stats:
            self.usage_stats[model_name] = {}
        
        task_key = task_type.value
        if task_key not in self.usage_stats[model_name]:
            self.usage_stats[model_name][task_key] = 0
        
        self.usage_stats[model_name][task_key] += 1
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics for premium dashboard"""
        return {
            "available_models": self.registry.get_available_models(),
            "usage_stats": self.usage_stats,
            "model_performance": self.model_performance,
            "total_calls": sum(
                sum(tasks.values()) for tasks in self.usage_stats.values()
            )
        }
    
    def add_new_model(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Add new model API key and return status"""
        success = self.registry.add_model_key(provider, api_key)
        
        if success:
            # Reinitialize clients for newly available models
            self._initialize_clients()
        
        return {
            "success": success,
            "available_models": self.registry.get_available_models(),
            "message": f"Successfully added {provider} models" if success else f"Failed to add {provider} models"
        }

# Global instance
premium_model_manager = PremiumModelManager()