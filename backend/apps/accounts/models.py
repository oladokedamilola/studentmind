from django.db import models
import uuid
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import base64
from django.contrib.auth.hashers import make_password, check_password  # Add this import

# Import Student from university app - use string reference to avoid circular imports
# from apps.university.models import Student  # Don't import directly

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


class StudentAuth(models.Model):
    """Authentication information for students who register"""
    student = models.OneToOneField('university.Student', on_delete=models.CASCADE, related_name='auth')
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Registration token (for email verification during signup)
    registration_token = models.CharField(max_length=100, blank=True, null=True)
    registration_token_created_at = models.DateTimeField(null=True, blank=True)
    
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Security fields
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def set_password(self, raw_password):
        """Hash and set password"""
        from django.contrib.auth.hashers import make_password
        self.password_hash = make_password(raw_password)
        self.save()
    
    def check_password(self, raw_password):
        """Verify password"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password_hash)
    
    def set_registration_token(self):
        """Generate and set registration token"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.registration_token = token
        self.registration_token_created_at = timezone.now()
        self.save()
        return token
    
    def is_registration_token_valid(self):
        """Check if registration token is still valid (24 hours)"""
        if not self.registration_token_created_at:
            return False
        expiry = self.registration_token_created_at + timezone.timedelta(hours=24)
        return timezone.now() < expiry
    
    def clear_registration_token(self):
        """Clear registration token after use"""
        self.registration_token = None
        self.registration_token_created_at = None
        self.save()
    
    def increment_login_attempts(self):
        """Track failed login attempts"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def reset_login_attempts(self):
        """Reset after successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.save()
    
    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_email_verified = True
        self.email_verified_at = timezone.now()
        self.is_verified = True  # Auto-verify student
        self.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['email']),  
        ]
    
    def __str__(self):
        return f"Auth for {self.student.matric_number}"