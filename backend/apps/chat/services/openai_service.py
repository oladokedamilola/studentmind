"""
OpenAI API integration service using GitHub Models (Microsoft Foundry Inference SDK)
"""
import os
import time
import logging
import random
from functools import wraps
from django.conf import settings
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from apps.openai_integration.models import APICallLog, PromptTemplate

logger = logging.getLogger(__name__)

def retry_on_connection_error(max_retries=3, base_delay=1):
    """Decorator to retry on connection errors with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (HttpResponseError, ServiceRequestError) as e:
                    last_error = e
                    # Check if it's a connection error
                    error_str = str(e)
                    is_connection_error = (
                        "ConnectionResetError" in error_str or 
                        "10054" in error_str or 
                        "connection" in error_str.lower() or
                        "timeout" in error_str.lower() or
                        "reset" in error_str.lower()
                    )
                    
                    if is_connection_error and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}. Retrying in {delay:.2f}s... Error: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        raise
                except Exception as e:
                    # For non-retryable errors, just raise
                    raise
            raise last_error if last_error else Exception("Max retries exceeded")
        return wrapper
    return decorator


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
    
    @retry_on_connection_error(max_retries=3, base_delay=1)
    def generate_response(self, message, conversation_history=None, student_context=None):
        """
        Generate AI response using GitHub Models with automatic retry on connection errors
        """
        start_time = time.time()
        
        try:
            # Prepare messages for API
            messages = []
            
            # Add system message
            messages.append(SystemMessage(self.get_system_prompt(student_context)))
            
            # Add conversation history (last 10 messages for context)
            # FIX: Handle empty or small conversation_history properly
            if conversation_history is not None:
                # Check if it's a QuerySet or list
                if hasattr(conversation_history, 'exists') and conversation_history.exists():
                    # It's a QuerySet with data
                    history_list = list(conversation_history)
                    # Get last 10 messages (or all if less than 10)
                    if len(history_list) > 10:
                        history_list = history_list[-10:]
                    
                    for msg in history_list:
                        try:
                            if msg.sender == 'ai':
                                messages.append(AssistantMessage(msg.decrypt_content()))
                            elif msg.sender == 'user':
                                messages.append(UserMessage(msg.decrypt_content()))
                        except Exception as e:
                            logger.error(f"Error processing history message: {e}")
                            continue
                elif isinstance(conversation_history, list) and len(conversation_history) > 0:
                    # It's a list
                    history_list = conversation_history
                    if len(history_list) > 10:
                        history_list = history_list[-10:]
                    
                    for msg in history_list:
                        try:
                            if msg.sender == 'ai':
                                messages.append(AssistantMessage(msg.decrypt_content()))
                            elif msg.sender == 'user':
                                messages.append(UserMessage(msg.decrypt_content()))
                        except Exception as e:
                            logger.error(f"Error processing history message: {e}")
                            continue
            
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
            # The retry decorator will handle retries, so this is just a fallback
            return {
                'success': False,
                'error': 'connection_error',
                'message': "Network issue. Please check your internet connection and try again."
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