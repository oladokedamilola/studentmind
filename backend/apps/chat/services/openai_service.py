"""
OpenAI API integration service using GitHub Models (Microsoft Foundry Inference SDK)
"""
import os
import time
import logging
from django.conf import settings
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from apps.openai_integration.models import APICallLog, PromptTemplate

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with GitHub Models (Microsoft Foundry Inference)"""
    
    def __init__(self):
        self.endpoint = settings.AZURE_INFERENCE_ENDPOINT
        self.model = settings.AZURE_MODEL_NAME
        self.token = settings.GITHUB_TOKEN
        
        # Initialize the client
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.token),
        )
        
        logger.info(f"Initialized GitHub Models client with endpoint: {self.endpoint}, model: {self.model}")
    
    def get_system_prompt(self, context=None):
        """
        Get the appropriate system prompt based on context
        """
        base_prompt = """You are a compassionate mental health support assistant for university students. 
        Your role is to provide empathetic, non-judgmental support while maintaining appropriate boundaries.

        GUIDELINES:
        1. Always be warm, empathetic, and validating
        2. NEVER provide medical diagnosis or prescribe treatments
        3. If user mentions self-harm or suicide, acknowledge their pain and provide crisis resources
        4. Suggest evidence-based coping strategies (breathing exercises, grounding techniques, etc.)
        5. Keep responses concise and supportive (under 200 words)
        6. Ask open-ended questions to encourage reflection
        7. Remind users that you're an AI and encourage professional help when needed
        8. Maintain confidentiality boundaries - do not ask for personal identifying information

        Remember: You're here to support, not to replace professional mental health care.
        """
        
        # Try to get a more specific prompt from database
        try:
            if context and context.get('category'):
                template = PromptTemplate.objects.filter(
                    category=context['category'],
                    is_active=True
                ).order_by('-version').first()
                
                if template:
                    return template.render(**context)
        except Exception as e:
            logger.error(f"Error fetching prompt template: {e}")
        
        return base_prompt
    
    def generate_response(self, message, conversation_history=None, student_context=None):
        """
        Generate AI response using GitHub Models
        """
        start_time = time.time()
        
        try:
            # Prepare messages for API
            messages = []
            
            # Add system message
            messages.append(SystemMessage(self.get_system_prompt(student_context)))
            
            # Add conversation history (last 10 messages for context)
            if conversation_history:
                for msg in conversation_history[-10:]:
                    if msg.sender == 'ai':
                        messages.append(AssistantMessage(msg.decrypt_content()))
                    elif msg.sender == 'user':
                        messages.append(UserMessage(msg.decrypt_content()))
            
            # Add current message
            messages.append(UserMessage(message))
            
            logger.debug(f"Sending request to GitHub Models with {len(messages)} messages")
            
            # Call GitHub Models API
            response = self.client.complete(
                messages=messages,
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Extract response content
            ai_message = response.choices[0].message.content
            
            # Extract usage information if available
            prompt_tokens = getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0
            completion_tokens = getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0
            total_tokens = getattr(response.usage, 'total_tokens', 0) if hasattr(response, 'usage') else 0
            
            # Log API call
            APICallLog.objects.create(
                model_used=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time,
                status='success'
            )
            
            logger.info(f"GitHub Models response successful. Tokens: {total_tokens}, Time: {response_time}ms")
            
            return {
                'success': True,
                'message': ai_message,
                'token_usage': {
                    'prompt': prompt_tokens,
                    'completion': completion_tokens,
                    'total': total_tokens
                },
                'response_time': response_time
            }
            
        except HttpResponseError as e:
            logger.error(f"GitHub Models HTTP error: {e.status_code} - {e.message}")
            
            # Handle rate limiting (GitHub Models free tier has limits)
            if e.status_code == 429:
                return {
                    'success': False,
                    'error': 'rate_limit',
                    'message': "I've reached my usage limit right now. Please try again later or contact support if this persists."
                }
            elif e.status_code == 401:
                return {
                    'success': False,
                    'error': 'auth_error',
                    'message': "Authentication error. Please check your GitHub token."
                }
            else:
                return {
                    'success': False,
                    'error': 'api_error',
                    'message': "I'm having trouble connecting right now. Please try again."
                }
                
        except ServiceRequestError as e:
            logger.error(f"GitHub Models connection error: {e}")
            return {
                'success': False,
                'error': 'connection_error',
                'message': "Unable to reach the AI service. Please check your internet connection."
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in GitHub Models service: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'unknown',
                'message': "Something went wrong. Please try again."
            }
    
    def test_connection(self):
        """
        Test the connection to GitHub Models
        """
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage("You are a test assistant."),
                    UserMessage("Say 'Connection successful' if you can hear me.")
                ],
                model=self.model,
                max_tokens=20
            )
            return True, response.choices[0].message.content
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, str(e)