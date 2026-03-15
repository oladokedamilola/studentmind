from django.db import models
import uuid
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import base64

class AnonymousUserSession(models.Model):
    """
    Model to track anonymous user sessions
    No personal information is stored - only session identifiers
    """
    session_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Anonymized metadata (no personal identifiers)
    hashed_ip = models.CharField(max_length=64, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Encrypted session data (for temporary storage)
    encrypted_data = models.TextField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def save(self, *args, **kwargs):
        # Set expiry to 30 days from creation if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if session is still valid (not expired)"""
        return timezone.now() < self.expires_at
    
    def hash_ip(self, ip_address):
        """Anonymize IP address by hashing it"""
        if ip_address:
            salt = settings.SECRET_KEY.encode()
            hashed = hashlib.pbkdf2_hmac('sha256', ip_address.encode(), salt, 100000)
            self.hashed_ip = base64.b64encode(hashed).decode()
    
    def __str__(self):
        return f"Session {self.session_id} - Created: {self.created_at}"