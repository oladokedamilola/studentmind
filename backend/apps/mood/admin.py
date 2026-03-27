from django.contrib import admin
from .models import MoodEntry

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'mood_score', 'recorded_at', 'note_preview']
    list_filter = ['mood_score', 'recorded_at']
    search_fields = ['student__matric_number', 'student__first_name', 'student__last_name']
    readonly_fields = ['recorded_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if obj.note and len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'