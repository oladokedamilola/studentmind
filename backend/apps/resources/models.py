from django.db import models
from apps.accounts.models import AnonymousUserSession

class ResourceCategory(models.Model):
    """
    Categories for coping resources
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # Icon class name
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Resource categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class ResourceTag(models.Model):
    """
    Tags for filtering resources
    """
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ResourceItem(models.Model):
    """
    Coping resources, articles, and tips
    """
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('exercise', 'Exercise'),
        ('tip', 'Quick Tip'),
        ('guided', 'Guided Practice'),
        ('external', 'External Link'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(max_length=300, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='article')
    
    # Categorization
    categories = models.ManyToManyField(ResourceCategory, related_name='resources')
    tags = models.ManyToManyField(ResourceTag, related_name='resources', blank=True)
    
    # Metadata
    author = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo embed URL")
    
    # Media
    featured_image = models.ImageField(upload_to='resources/', blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)  # For exercises/videos
    
    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement metrics
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    avg_rating = models.FloatField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['resource_type', 'is_published']),
            models.Index(fields=['-published_at']),
            models.Index(fields=['-view_count']),
        ]
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title

class MoodEntry(models.Model):
    """
    Tracks user mood over time
    """
    MOOD_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Neutral'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    session = models.ForeignKey(
        AnonymousUserSession,
        on_delete=models.CASCADE,
        related_name='mood_entries'
    )
    mood_score = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)  # Optional note about the mood
    
    # Context
    recorded_at = models.DateTimeField(auto_now_add=True)
    day_of_week = models.IntegerField()  # 0-6, Monday=0
    time_of_day = models.TimeField(auto_now_add=True)
    
    # Optional: link to conversation if mood was recorded during chat
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mood_entries'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['session', '-recorded_at']),
            models.Index(fields=['mood_score']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']
    
    def save(self, *args, **kwargs):
        # Auto-set day of week
        from django.utils import timezone
        self.day_of_week = timezone.now().weekday()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Mood {self.mood_score} at {self.recorded_at}"

class ResourceInteraction(models.Model):
    """
    Tracks user interactions with resources for recommendations
    """
    INTERACTION_TYPES = [
        ('view', 'Viewed'),
        ('helpful', 'Marked Helpful'),
        ('not_helpful', 'Marked Not Helpful'),
        ('share', 'Shared'),
        ('save', 'Saved'),
    ]
    
    session = models.ForeignKey(
        AnonymousUserSession,
        on_delete=models.CASCADE,
        related_name='resource_interactions'
    )
    resource = models.ForeignKey(
        ResourceItem,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Context
    mood_at_time = models.IntegerField(choices=MoodEntry.MOOD_CHOICES, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['session', 'interaction_type']),
            models.Index(fields=['resource', '-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.session.session_id} - {self.interaction_type} - {self.resource.title}"