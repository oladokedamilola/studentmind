from django.db import models
from apps.university.models import Student
from django.utils import timezone

class Assessment(models.Model):
    """Mental health assessment (e.g., PHQ-9, GAD-7)"""
    ASSESSMENT_TYPES = [
        ('phq9', 'PHQ-9 (Depression)'),
        ('gad7', 'GAD-7 (Anxiety)'),
        ('pss', 'Perceived Stress Scale'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, choices=ASSESSMENT_TYPES)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    scoring_guide = models.TextField(blank=True)
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=27)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_severity(self, score):
        """Get severity level based on score"""
        if self.code == 'phq9':
            if score <= 4:
                return {'level': 'Minimal', 'color': '#4A6B4A', 'description': 'Minimal depression'}
            elif score <= 9:
                return {'level': 'Mild', 'color': '#9CAF88', 'description': 'Mild depression'}
            elif score <= 14:
                return {'level': 'Moderate', 'color': '#E5B25D', 'description': 'Moderate depression'}
            elif score <= 19:
                return {'level': 'Moderately Severe', 'color': '#C47E7E', 'description': 'Moderately severe depression'}
            else:
                return {'level': 'Severe', 'color': '#C47E7E', 'description': 'Severe depression'}
        elif self.code == 'gad7':
            if score <= 4:
                return {'level': 'Minimal', 'color': '#4A6B4A', 'description': 'Minimal anxiety'}
            elif score <= 9:
                return {'level': 'Mild', 'color': '#9CAF88', 'description': 'Mild anxiety'}
            elif score <= 14:
                return {'level': 'Moderate', 'color': '#E5B25D', 'description': 'Moderate anxiety'}
            else:
                return {'level': 'Severe', 'color': '#C47E7E', 'description': 'Severe anxiety'}
        return {'level': 'Normal', 'color': '#4A6B4A', 'description': 'Normal range'}


class Question(models.Model):
    """Questions for an assessment"""
    QUESTION_TYPES = [
        ('likert', 'Likert Scale (0-3)'),
        ('scale', 'Scale (0-10)'),
        ('text', 'Text Response'),
        ('yes_no', 'Yes/No'),
    ]
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='likert')
    order = models.IntegerField(default=0)
    
    # For Likert questions (0-3 scale)
    option_labels = models.JSONField(default=list, blank=True, help_text="Labels for each option")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.assessment.code} - Q{self.order}: {self.text[:50]}"


class AssessmentResult(models.Model):
    """User's assessment results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    total_score = models.IntegerField()
    severity = models.CharField(max_length=50)
    responses = models.JSONField(default=dict)  # Store question responses
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['student', '-completed_at']),
            models.Index(fields=['assessment']),
        ]
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.assessment.name}: {self.total_score} ({self.completed_at.date()})"