# apps/chat/models.py
from django.db import models
from apps.accounts.models import AnonymousUserSession
from apps.university.models import Student
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os
import json
import logging

logger = logging.getLogger(__name__)

# Cache for cipher to avoid recreating it for every message
_cipher_cache = None

def get_encryption_key():
    """
    Get the encryption key from settings.
    Must be consistent across server restarts.
    """
    # Check if there's a key in settings (already bytes)
    if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
        return settings.ENCRYPTION_KEY
    
    # For development without a key, generate a temporary one
    # WARNING: This will cause decryption errors if used across server restarts!
    logger.warning("No ENCRYPTION_KEY found in settings. Using temporary key. Messages may not be decryptable after server restart.")
    return Fernet.generate_key()

def get_cipher():
    """
    Get or create a cached Fernet cipher instance.
    This ensures the same cipher is reused for all encryption/decryption.
    """
    global _cipher_cache
    if _cipher_cache is None:
        key = get_encryption_key()
        _cipher_cache = Fernet(key)
    return _cipher_cache

class Conversation(models.Model):
    """
    Represents a chat conversation between a student and the AI assistant
    Now linked to either anonymous session OR authenticated student
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
        ('escalated', 'Escalated'),
    ]
    
    # Can be linked to either anonymous session OR authenticated student
    session = models.ForeignKey(
        AnonymousUserSession,
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    topic = models.CharField(max_length=100, blank=True, null=True)
    
    # For analytics
    message_count = models.IntegerField(default=0)
    user_message_count = models.IntegerField(default=0)
    ai_message_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['student', '-last_activity']),
            models.Index(fields=['session', '-last_activity']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-last_activity']
    
    def get_participant(self):
        """Return the participant (student or anonymous)"""
        if self.student:
            return self.student
        return self.session
    
    def get_participant_type(self):
        """Return whether conversation is with student or anonymous"""
        if self.student:
            return 'student'
        return 'anonymous'
    
    def close(self):
        """Close the conversation"""
        self.status = 'closed'
        self.save()
    
    def update_counts(self):
        """Update message counts"""
        self.user_message_count = self.messages.filter(sender='user').count()
        self.ai_message_count = self.messages.filter(sender='ai').count()
        self.message_count = self.user_message_count + self.ai_message_count
        self.save()
    
    def __str__(self):
        if self.student:
            return f"Conversation {self.id} - Student: {self.student.matric_number}"
        return f"Conversation {self.id} - Session: {self.session.session_id}"

class Message(models.Model):
    """
    Individual messages within a conversation
    Content is encrypted for privacy
    """
    SENDER_TYPES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
        ('system', 'System'),
        ('counselor', 'Human Counselor'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.CharField(max_length=20, choices=SENDER_TYPES)
    encrypted_content = models.TextField()  # Encrypted message content
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # For analysis and prioritization
    sentiment_score = models.FloatField(null=True, blank=True)  # -1 to 1
    priority = models.IntegerField(default=0)  # 0=normal, 1=urgent, 2=crisis
    detected_keywords = models.TextField(blank=True, null=True)  # JSON array of keywords
    
    # Metadata
    token_count = models.IntegerField(null=True, blank=True)  # For OpenAI billing
    response_time_ms = models.IntegerField(null=True, blank=True)  # For AI response time
    
    class Meta:
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['priority']),
            models.Index(fields=['sender']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['timestamp']
    
    def encrypt_content(self, content):
        """
        Encrypt message content using consistent cipher.
        Falls back to plain text if encryption fails (with marker).
        """
        try:
            cipher = get_cipher()
            encrypted = cipher.encrypt(content.encode())
            self.encrypted_content = base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error for message: {e}")
            # Store as plain text with marker as fallback (prevents data loss)
            self.encrypted_content = f"PLAIN:{content}"
    
    def decrypt_content(self):
        """
        Decrypt message content using consistent cipher.
        Handles plain text fallback and decryption errors gracefully.
        """
        try:
            # Handle plain text fallback (for messages that couldn't be encrypted)
            if self.encrypted_content.startswith('PLAIN:'):
                return self.encrypted_content[6:]
            
            cipher = get_cipher()
            encrypted = base64.b64decode(self.encrypted_content.encode())
            return cipher.decrypt(encrypted).decode()
        except Exception as e:
            logger.error(f"Decryption error for message {self.id}: {e}")
            return "[Message temporarily unavailable]"
    
    def get_content(self):
        """Alias for decrypt_content for template use"""
        return self.decrypt_content()
    
    def set_keywords(self, keywords_list):
        """Store detected keywords as JSON"""
        self.detected_keywords = json.dumps(keywords_list)
    
    def get_keywords(self):
        """Retrieve detected keywords"""
        if self.detected_keywords:
            try:
                return json.loads(self.detected_keywords)
            except json.JSONDecodeError:
                return []
        return []
    
    def save(self, *args, **kwargs):
        # Update conversation's last_activity
        self.conversation.last_activity = timezone.now()
        self.conversation.save()
        
        # Update conversation counts if this is a new message
        if not self.pk:  # Only on creation
            if self.sender == 'user':
                self.conversation.user_message_count += 1
            elif self.sender == 'ai':
                self.conversation.ai_message_count += 1
            self.conversation.message_count += 1
            self.conversation.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation_id} - {self.sender}"