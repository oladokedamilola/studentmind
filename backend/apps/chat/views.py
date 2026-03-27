from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
import logging

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationDetailSerializer,
    MessageSerializer, MessageCreateSerializer
)
from apps.university.models import Student
from apps.accounts.models import AnonymousUserSession
from .utils.crisis_detection import calculate_priority, get_emergency_response
from .services.openai_service import OpenAIService
from apps.emergency.models import CrisisFlag, EmergencyResource

logger = logging.getLogger(__name__)
openai_service = OpenAIService()

@api_view(['POST'])
def send_message(request):
    """
    Send a message and get AI response
    """
    # Debug: Log incoming request
    logger.info("=" * 50)
    logger.info("send_message called")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request data: {request.data}")
    
    # Check authentication (either student or anonymous session)
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    # FIX: Convert student_id to integer if it's a string
    if student_id and isinstance(student_id, str):
        try:
            student_id = int(student_id)
            logger.info(f"✅ Converted student_id from string to int: {student_id}")
        except ValueError:
            logger.error(f"❌ Could not convert student_id to int: {student_id}")
            return Response(
                {'error': 'Invalid session data'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    logger.info(f"Student ID from session (type: {type(student_id)}): {student_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Session keys: {list(request.session.keys())}")
    
    if not student_id and not session_id:
        logger.warning("No authentication found - returning 401")
        return Response(
            {'error': 'Not authenticated', 'details': 'Please login to continue'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = MessageCreateSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    content = serializer.validated_data['content']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    logger.info(f"Content: {content[:100]}...")
    logger.info(f"Conversation ID: {conversation_id}")
    
    # Get or create conversation
    try:
        if conversation_id:
            logger.info(f"Fetching existing conversation: {conversation_id}")
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                logger.info(f"Conversation found: student_id={conversation.student_id}, student={conversation.student}")
                
                # Verify ownership with type-safe comparison
                if student_id:
                    # If conversation has no student, assign it
                    if conversation.student is None:
                        logger.info(f"⚠️ Conversation {conversation_id} has no student, assigning to student {student_id}")
                        conversation.student_id = student_id
                        conversation.save()
                    # Check if conversation belongs to this student
                    elif conversation.student.id != student_id:
                        logger.warning(f"Conversation {conversation_id} does not belong to student {student_id} (belongs to {conversation.student.id})")
                        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
                    logger.info(f"✅ Conversation belongs to student {student_id}")
                else:
                    if not conversation.session or conversation.session.session_id != session_id:
                        logger.warning(f"Conversation {conversation_id} does not belong to session {session_id}")
                        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
                    logger.info(f"Conversation belongs to session {session_id}")
            except Conversation.DoesNotExist:
                logger.error(f"Conversation {conversation_id} not found")
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new conversation
            logger.info("Creating new conversation")
            if student_id:
                try:
                    student = Student.objects.get(id=student_id)
                    conversation = Conversation.objects.create(student=student)
                    logger.info(f"✅ Created new conversation for student {student_id}: ID {conversation.id}")
                except Student.DoesNotExist:
                    logger.error(f"Student {student_id} not found")
                    return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                session, created = AnonymousUserSession.objects.get_or_create(
                    session_id=session_id
                )
                conversation = Conversation.objects.create(session=session)
                logger.info(f"✅ Created new conversation for session {session_id}: ID {conversation.id}")
    except Exception as e:
        logger.error(f"Error creating/fetching conversation: {str(e)}")
        return Response({'error': 'Failed to create conversation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Calculate priority and detect crisis
    try:
        priority = calculate_priority(content)
        logger.info(f"Message priority: {priority}")
    except Exception as e:
        logger.error(f"Error calculating priority: {str(e)}")
        priority = 0
    
    # Create user message
    try:
        user_message = Message(
            conversation=conversation,
            sender='user',
            priority=priority
        )
        user_message.encrypt_content(content)
        user_message.save()
        logger.info(f"User message created: ID {user_message.id}")
    except Exception as e:
        logger.error(f"Error creating user message: {str(e)}")
        return Response({'error': 'Failed to save message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # If crisis detected, create crisis flag
    if priority >= 2:
        try:
            crisis_flag = CrisisFlag.objects.create(
                message=user_message,
                conversation=conversation,
                session=conversation.session if not student_id else None,
                student=conversation.student if student_id else None,
                severity=priority,
                detection_method='automated',
                matched_keywords=None
            )
            logger.info(f"Crisis flag created: ID {crisis_flag.id}")
        except Exception as e:
            logger.error(f"Error creating crisis flag: {str(e)}")
            # Continue even if crisis flag fails
    
    # Get conversation history for context
    try:
        # Convert QuerySet to list to avoid slicing issues
        history_qs = conversation.messages.all().order_by('-timestamp')[:20]
        history = list(history_qs)  # Convert to list for safe slicing
        logger.info(f"Retrieved {len(history)} messages for context")
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        history = []
    
    # Get AI response
    student_context = None
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            student_context = {
                'department': student.department.name,
                'faculty': student.department.faculty.name,
                'year': student.year_of_entry
            }
            logger.info(f"Student context: {student_context}")
        except Student.DoesNotExist:
            logger.error(f"Student {student_id} not found for context")
    
    try:
        ai_response = openai_service.generate_response(
            message=content,
            conversation_history=history,
            student_context=student_context
        )
        logger.info(f"AI response received: success={ai_response.get('success')}")
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        ai_response = {
            'success': False,
            'message': "I'm having trouble connecting right now. Please try again.",
            'error': 'ai_service_error'
        }
    
    if ai_response.get('success'):
        try:
            # Create AI message
            ai_message = Message(
                conversation=conversation,
                sender='ai',
                token_count=ai_response.get('token_usage', {}).get('total', 0),
                response_time_ms=ai_response.get('response_time', 0)
            )
            ai_message.encrypt_content(ai_response['message'])
            ai_message.save()
            logger.info(f"AI message created: ID {ai_message.id}")
        except Exception as e:
            logger.error(f"Error creating AI message: {str(e)}")
            return Response({
                'message': "Message received but couldn't save response. Please try again.",
                'conversation_id': conversation.id,
                'error': 'save_error'
            }, status=status.HTTP_200_OK)
        
        # Check if we need to include emergency resources
        response_data = {
            'message': ai_message.decrypt_content(),
            'conversation_id': conversation.id,
            'message_id': ai_message.id,
            'timestamp': ai_message.timestamp
        }
        
        # Add emergency resources if high priority
        if priority >= 2:
            try:
                emergency_resources = EmergencyResource.objects.filter(
                    is_available=True
                ).order_by('priority')[:3]
                
                response_data['emergency_resources'] = [
                    {
                        'name': r.name,
                        'phone': r.phone_number,
                        'website': r.website
                    }
                    for r in emergency_resources
                ]
                response_data['crisis_message'] = get_emergency_response(priority)
                logger.info(f"Added emergency resources for priority {priority}")
            except Exception as e:
                logger.error(f"Error adding emergency resources: {str(e)}")
        
        logger.info("Request completed successfully")
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # Return fallback response
        logger.warning(f"AI response failed: {ai_response.get('error')}")
        return Response({
            'message': ai_response.get('message', "I'm having trouble responding right now. Please try again."),
            'conversation_id': conversation.id,
            'error': ai_response.get('error', 'unknown')
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_conversations(request):
    """
    Get all conversations for the current user
    """
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    if student_id:
        conversations = Conversation.objects.filter(
            student_id=student_id
        ).prefetch_related('messages')
    elif session_id:
        conversations = Conversation.objects.filter(
            session__session_id=session_id
        ).prefetch_related('messages')
    else:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_conversation_detail(request, conversation_id):
    """
    Get detailed conversation with all messages
    """
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    try:
        if student_id:
            conversation = Conversation.objects.prefetch_related('messages').get(
                id=conversation_id,
                student_id=student_id
            )
        elif session_id:
            conversation = Conversation.objects.prefetch_related('messages').get(
                id=conversation_id,
                session__session_id=session_id
            )
        else:
            return Response(
                {'error': 'Not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ConversationDetailSerializer(conversation)
    return Response(serializer.data)


@api_view(['POST'])
def close_conversation(request, conversation_id):
    """
    Close a conversation
    """
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    try:
        if student_id:
            conversation = Conversation.objects.get(
                id=conversation_id,
                student_id=student_id
            )
        elif session_id:
            conversation = Conversation.objects.get(
                id=conversation_id,
                session__session_id=session_id
            )
        else:
            return Response(
                {'error': 'Not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    conversation.close()
    return Response({'message': 'Conversation closed'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def mark_read(request, conversation_id):
    """
    Mark all messages in a conversation as read
    """
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    try:
        if student_id:
            conversation = Conversation.objects.get(
                id=conversation_id,
                student_id=student_id
            )
        elif session_id:
            conversation = Conversation.objects.get(
                id=conversation_id,
                session__session_id=session_id
            )
        else:
            return Response(
                {'error': 'Not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    conversation.messages.filter(is_read=False).update(is_read=True)
    return Response({'message': 'Messages marked as read'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def regenerate_response(request):
    """
    Regenerate AI response for a user message
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        
        # Get the original user message
        user_message = Message.objects.get(id=message_id, sender='user')
        
        # Get the conversation
        conversation = user_message.conversation
        
        # Verify ownership
        if not conversation.student or conversation.student.id != student_id:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Delete the existing AI response (if any) after this user message
        later_messages = conversation.messages.filter(timestamp__gt=user_message.timestamp)
        later_messages.delete()
        
        # Get conversation history for context
        history = conversation.messages.all().order_by('timestamp')
        
        # Get AI response
        student = Student.objects.get(id=student_id)
        student_context = {
            'department': student.department.name,
            'faculty': student.department.faculty.name,
            'year': student.year_of_entry
        }
        
        ai_response = openai_service.generate_response(
            message=user_message.decrypt_content(),
            conversation_history=history,
            student_context=student_context
        )
        
        if ai_response.get('success'):
            # Create new AI message
            ai_message = Message(
                conversation=conversation,
                sender='ai',
                token_count=ai_response.get('token_usage', {}).get('total', 0),
                response_time_ms=ai_response.get('response_time', 0)
            )
            ai_message.encrypt_content(ai_response['message'])
            ai_message.save()
            
            return Response({
                'success': True,
                'message_id': ai_message.id,
                'content': ai_message.decrypt_content(),
                'timestamp': ai_message.timestamp
            })
        else:
            return Response({
                'success': False,
                'error': ai_response.get('error', 'Failed to generate response')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error regenerating response: {e}")
        return Response({'error': 'Failed to regenerate response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def edit_and_resend(request):
    """
    Edit a user message and get new AI response
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the original message
        original_message = Message.objects.get(id=message_id, sender='user')
        conversation = original_message.conversation
        
        # Verify ownership
        if not conversation.student or conversation.student.id != student_id:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Delete all messages after this point (including the original)
        later_messages = conversation.messages.filter(timestamp__gte=original_message.timestamp)
        later_messages.delete()
        
        # Create new user message with edited content
        user_message = Message(
            conversation=conversation,
            sender='user',
            priority=calculate_priority(new_content)
        )
        user_message.encrypt_content(new_content)
        user_message.save()
        
        # Get conversation history for context
        history = conversation.messages.all().order_by('timestamp')
        
        # Get AI response
        student = Student.objects.get(id=student_id)
        student_context = {
            'department': student.department.name,
            'faculty': student.department.faculty.name,
            'year': student.year_of_entry
        }
        
        ai_response = openai_service.generate_response(
            message=new_content,
            conversation_history=history,
            student_context=student_context
        )
        
        if ai_response.get('success'):
            ai_message = Message(
                conversation=conversation,
                sender='ai',
                token_count=ai_response.get('token_usage', {}).get('total', 0),
                response_time_ms=ai_response.get('response_time', 0)
            )
            ai_message.encrypt_content(ai_response['message'])
            ai_message.save()
            
            return Response({
                'success': True,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.decrypt_content(),
                    'timestamp': user_message.timestamp
                },
                'ai_message': {
                    'id': ai_message.id,
                    'content': ai_message.decrypt_content(),
                    'timestamp': ai_message.timestamp
                }
            })
        else:
            return Response({
                'success': False,
                'error': ai_response.get('error', 'Failed to generate response')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error editing and resending: {e}")
        return Response({'error': 'Failed to edit message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def stop_generation(request):
    """
    Stop the current AI response generation
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Verify ownership
        if not conversation.student or conversation.student.id != student_id:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Find and delete the last incomplete AI message (if any)
        last_messages = conversation.messages.filter(sender='ai').order_by('-timestamp')
        if last_messages.exists():
            last_ai = last_messages.first()
            # If the AI message was just created and empty or incomplete, delete it
            last_ai.delete()
        
        return Response({'success': True, 'message': 'Generation stopped'})
        
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error stopping generation: {e}")
        return Response({'error': 'Failed to stop generation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)