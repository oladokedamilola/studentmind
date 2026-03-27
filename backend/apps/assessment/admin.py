from django.contrib import admin
from .models import Assessment, Question, AssessmentResult

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5
    fields = ['text', 'question_type', 'order', 'option_labels']

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'code']
    search_fields = ['name', 'description']
    inlines = [QuestionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'instructions')
        }),
        ('Scoring', {
            'fields': ('scoring_guide', 'min_score', 'max_score')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'assessment', 'text', 'question_type', 'order']
    list_filter = ['assessment', 'question_type']
    search_fields = ['text']

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'total_score', 'severity', 'completed_at']
    list_filter = ['assessment', 'severity', 'completed_at']
    search_fields = ['student__matric_number']
    readonly_fields = ['responses', 'completed_at']