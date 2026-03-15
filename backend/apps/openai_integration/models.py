from django.db import models
from apps.chat.models import Conversation, Message
from django.utils import timezone

class APICallLog(models.Model):
    """
    Logs all GitHub Models API calls for monitoring and billing
    """
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('rate_limited', 'Rate Limited'),
        ('timeout', 'Timeout'),
        ('auth_error', 'Authentication Error'),
    ]
    
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.SET_NULL,
        null=True,
        related_name='api_calls'
    )
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.SET_NULL,
        null=True,
        related_name='api_log'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    model_used = models.CharField(max_length=50)
    provider = models.CharField(max_length=20, default='github-models')  # Track provider
    
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    
    response_time_ms = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # For debugging (anonymized)
    prompt_preview = models.TextField(blank=True, null=True)  # First 100 chars
    error_message = models.TextField(blank=True, null=True)
    
    # Cost tracking (GitHub Models free tier has limits, then pay-as-you-go)
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['conversation']),
            models.Index(fields=['provider']),
        ]
        ordering = ['-timestamp']
    
    def calculate_cost(self):
        """Calculate estimated cost based on token usage"""
        # GitHub Models pricing (example - adjust based on actual model)
        # GPT-4o pricing example: $0.005 per 1K input tokens, $0.015 per 1K output tokens
        input_rate = 0.005  # per 1K tokens
        output_rate = 0.015  # per 1K tokens
        
        input_cost = (self.prompt_tokens / 1000) * input_rate
        output_cost = (self.completion_tokens / 1000) * output_rate
        self.estimated_cost_usd = input_cost + output_cost
        return self.estimated_cost_usd
    
    def save(self, *args, **kwargs):
        if not self.estimated_cost_usd and self.total_tokens:
            self.calculate_cost()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"GitHub Models API Call {self.id} - {self.status} - {self.total_tokens} tokens"

class PromptTemplate(models.Model):
    """
    Stores different prompt templates for various mental health scenarios
    """
    CATEGORY_CHOICES = [
        ('general', 'General Support'),
        ('anxiety', 'Anxiety Management'),
        ('stress', 'Academic Stress'),
        ('depression', 'Depression Support'),
        ('crisis', 'Crisis Intervention'),
        ('greeting', 'Greeting/Introduction'),
        ('followup', 'Follow-up Questions'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    
    # The actual prompt template with placeholders
    template_content = models.TextField()
    
    # Versioning
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)  # Admin user
    
    # Usage statistics
    times_used = models.IntegerField(default=0)
    avg_rating = models.FloatField(null=True, blank=True)  # 1-5 scale from testing
    
    class Meta:
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['name']),
        ]
        ordering = ['category', 'name']
    
    def render(self, **kwargs):
        """
        Render the template with provided variables
        Example: template.render(user_message="I'm feeling anxious")
        """
        try:
            return self.template_content.format(**kwargs)
        except KeyError as e:
            # Fallback to template without formatting if variables missing
            return self.template_content
    
    def __str__(self):
        return f"{self.name} v{self.version} - {self.category}"