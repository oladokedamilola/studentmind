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
    # Check authentication (either student or anonymous session)
    student_id = request.session.get('student_id')
    session_id = request.session.session_key
    
    if not student_id and not session_id:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = MessageCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    content = serializer.validated_data['content']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    # Get or create conversation
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            # Verify ownership
            if student_id:
                if not conversation.student or conversation.student.id != student_id:
                    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            else:
                if not conversation.session or conversation.session.session_id != session_id:
                    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Create new conversation
        if student_id:
            student = Student.objects.get(id=student_id)
            conversation = Conversation.objects.create(student=student)
        else:
            session, _ = AnonymousUserSession.objects.get_or_create(
                session_id=session_id
            )
            conversation = Conversation.objects.create(session=session)
    
    # Calculate priority and detect crisis
    priority = calculate_priority(content)
    
    # Create user message
    user_message = Message(
        conversation=conversation,
        sender='user',
        priority=priority
    )
    user_message.encrypt_content(content)
    user_message.save()
    
    # If crisis detected, create crisis flag
    if priority >= 2:
        crisis_keywords = []  # This would come from detection function
        crisis_flag = CrisisFlag.objects.create(
            message=user_message,
            conversation=conversation,
            session=conversation.session if not student_id else None,
            student=conversation.student if student_id else None,
            severity=priority,
            detection_method='automated',
            matched_keywords=','.join(crisis_keywords) if crisis_keywords else None
        )
        crisis_flag.save()
    
    # Get conversation history for context
    history = conversation.messages.all().order_by('-timestamp')[:20]
    
    # Get AI response
    student_context = None
    if student_id:
        student = Student.objects.get(id=student_id)
        student_context = {
            'department': student.department.name,
            'faculty': student.department.faculty.name,
            'year': student.year_of_entry
        }
    
    ai_response = openai_service.generate_response(
        message=content,
        conversation_history=history,
        student_context=student_context
    )
    
    if ai_response['success']:
        # Create AI message
        ai_message = Message(
            conversation=conversation,
            sender='ai',
            token_count=ai_response['token_usage']['total'],
            response_time_ms=ai_response['response_time']
        )
        ai_message.encrypt_content(ai_response['message'])
        ai_message.save()
        
        # Check if we need to include emergency resources
        response_data = {
            'message': ai_message.decrypt_content(),
            'conversation_id': conversation.id,
            'message_id': ai_message.id,
            'timestamp': ai_message.timestamp
        }
        
        # Add emergency resources if high priority
        if priority >= 2:
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
        
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # Return fallback response
        return Response({
            'message': ai_response['message'],
            'conversation_id': conversation.id,
            'error': ai_response.get('error')
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