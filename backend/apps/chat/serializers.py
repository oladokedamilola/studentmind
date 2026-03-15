from rest_framework import serializers
from .models import Conversation, Message
from apps.university.models import Student
import json

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages"""
    content = serializers.SerializerMethodField()
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_display', 'content', 'timestamp', 'is_read', 'priority']
        read_only_fields = ['id', 'timestamp', 'priority']
    
    def get_content(self, obj):
        """Decrypt content for API response"""
        return obj.decrypt_content()

class MessageCreateSerializer(serializers.Serializer):
    """Serializer for creating a new message"""
    content = serializers.CharField(max_length=5000)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Message too long (max 5000 characters)")
        return value.strip()

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participant_info = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'started_at', 'last_activity', 'status', 'topic', 
                  'message_count', 'participant_info', 'last_message']
        read_only_fields = ['id', 'started_at', 'last_activity', 'message_count']
    
    def get_participant_info(self, obj):
        """Get info about the participant (student or anonymous)"""
        if obj.student:
            return {
                'type': 'student',
                'matric_number': obj.student.matric_number,
                'name': obj.student.get_full_name(),
                'department': obj.student.department.name
            }
        return {
            'type': 'anonymous',
            'session_id': str(obj.session.session_id) if obj.session else None
        }
    
    def get_last_message(self, obj):
        """Get the most recent message"""
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return {
                'content': last_msg.decrypt_content()[:100] + '...' if len(last_msg.decrypt_content()) > 100 else last_msg.decrypt_content(),
                'sender': last_msg.sender,
                'timestamp': last_msg.timestamp
            }
        return None

class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer with all messages"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']