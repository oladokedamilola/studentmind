from django.db import models
from apps.university.models import Student
from django.utils import timezone

class MoodEntry(models.Model):
    """
    Tracks mood entries for students
    """
    MOOD_CHOICES = [
        (1, '😔 Very Low'),
        (2, '😟 Low'),
        (3, '😐 Okay'),
        (4, '🙂 Good'),
        (5, '😊 Excellent'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='mood_entries'
    )
    mood_score = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['student', '-recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.get_mood_score_display()} on {self.recorded_at.date()}"