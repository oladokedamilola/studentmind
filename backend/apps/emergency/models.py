from django.db import models
from apps.chat.models import Message, Conversation
from apps.accounts.models import AnonymousUserSession

class CrisisFlag(models.Model):
    """
    Flags messages that contain crisis indicators
    """
    SEVERITY_CHOICES = [
        (1, 'Low - Concerning keywords'),
        (2, 'Medium - Strong indicators'),
        (3, 'High - Immediate attention'),
        (4, 'Critical - Immediate intervention required'),
    ]
    
    STATUS_CHOICES = [
        ('detected', 'Detected - Not escalated'),
        ('escalated', 'Escalated to human'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='crisis_flag'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='crisis_flags'
    )
    session = models.ForeignKey(
        AnonymousUserSession,
        on_delete=models.CASCADE,
        related_name='crisis_flags'
    )
    
    detected_at = models.DateTimeField(auto_now_add=True)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected')
    
    # Detection method
    detection_method = models.CharField(max_length=50, default='keyword')  # keyword, sentiment, manual
    matched_keywords = models.TextField(blank=True, null=True)  # Comma-separated keywords matched
    
    # Escalation tracking
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalated_to = models.CharField(max_length=100, blank=True, null=True)  # Counselor/Admin
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['session']),
        ]
        ordering = ['-severity', 'detected_at']
    
    def escalate(self, escalated_by=None):
        """Mark this crisis flag as escalated"""
        self.status = 'escalated'
        self.escalated_at = models.DateTimeField(auto_now=True)
        self.escalated_to = escalated_by
        self.save()
        
        # Also mark the conversation as escalated
        self.conversation.status = 'escalated'
        self.conversation.save()
    
    def resolve(self, notes=""):
        """Resolve this crisis flag"""
        self.status = 'resolved'
        self.resolution_notes = notes
        self.resolved_at = models.DateTimeField(auto_now=True)
        self.save()
    
    def __str__(self):
        return f"Crisis Flag {self.id} - Severity {self.severity} - {self.status}"

class EmergencyResource(models.Model):
    """
    Emergency contact resources for different regions
    """
    REGION_CHOICES = [
        ('global', 'Global'),
        ('us', 'United States'),
        ('uk', 'United Kingdom'),
        ('ca', 'Canada'),
        ('au', 'Australia'),
        ('ng', 'Nigeria'),  # Add your specific region
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    text_line = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='global')
    languages = models.CharField(max_length=200, default='English')  # Comma-separated
    
    # Availability
    hours_available = models.CharField(max_length=100, default='24/7')
    is_available = models.BooleanField(default=True)
    
    # Priority (for display order)
    priority = models.IntegerField(default=0)  # Lower = higher priority
    
    class Meta:
        indexes = [
            models.Index(fields=['region', 'priority']),
            models.Index(fields=['is_available']),
        ]
        ordering = ['region', 'priority', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.region}"

class CrisisKeyword(models.Model):
    """
    Keywords that trigger crisis detection
    """
    word = models.CharField(max_length=100, unique=True)
    severity_level = models.IntegerField(choices=CrisisFlag.SEVERITY_CHOICES, default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['severity_level', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.word} (Severity: {self.severity_level})"