from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
from .models import MoodEntry
from apps.university.models import Student

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def save_mood(request):
    """Save a mood entry for the current user"""
    try:
        student_id = request.session.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        student = Student.objects.get(id=student_id)
        data = json.loads(request.body)
        
        mood_score = data.get('mood_score')
        if not mood_score or mood_score not in [1, 2, 3, 4, 5]:
            return JsonResponse({'error': 'Invalid mood score. Must be 1-5'}, status=400)
        
        note = data.get('note', '')
        
        # Check if mood already logged today
        today = timezone.now().date()
        existing = MoodEntry.objects.filter(
            student=student,
            recorded_at__date=today
        ).first()
        
        if existing:
            # Update existing entry
            existing.mood_score = mood_score
            existing.note = note
            existing.save()
            return JsonResponse({
                'success': True,
                'message': 'Mood updated for today',
                'id': existing.id,
                'updated': True
            })
        else:
            # Create new entry
            mood_entry = MoodEntry.objects.create(
                student=student,
                mood_score=mood_score,
                note=note
            )
            return JsonResponse({
                'success': True,
                'message': 'Mood saved for today',
                'id': mood_entry.id,
                'created': True
            })
            
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error saving mood: {e}")
        return JsonResponse({'error': 'Failed to save mood'}, status=500)


@require_http_methods(["GET"])
def get_today_mood(request):
    """Get today's mood entry for the current user"""
    try:
        student_id = request.session.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        student = Student.objects.get(id=student_id)
        today = timezone.now().date()
        
        mood_entry = MoodEntry.objects.filter(
            student=student,
            recorded_at__date=today
        ).first()
        
        if mood_entry:
            return JsonResponse({
                'mood': mood_entry.mood_score,
                'note': mood_entry.note,
                'recorded_at': mood_entry.recorded_at,
                'has_entry': True
            })
        else:
            return JsonResponse({'has_entry': False})
            
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching today's mood: {e}")
        return JsonResponse({'error': 'Failed to fetch mood'}, status=500)


@require_http_methods(["GET"])
def get_mood_history(request):
    """Get mood history for the current user"""
    try:
        student_id = request.session.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        student = Student.objects.get(id=student_id)
        
        # Get last 30 days of mood entries
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        moods = MoodEntry.objects.filter(
            student=student,
            recorded_at__gte=thirty_days_ago
        ).order_by('-recorded_at')
        
        data = [{
            'id': m.id,
            'mood_score': m.mood_score,
            'note': m.note,
            'recorded_at': m.recorded_at.isoformat(),
            'date': m.recorded_at.strftime('%Y-%m-%d'),
            'day_of_week': m.recorded_at.strftime('%A'),
            'mood_name': dict(MoodEntry.MOOD_CHOICES).get(m.mood_score, 'Unknown')
        } for m in moods]
        
        return JsonResponse({
            'success': True,
            'moods': data,
            'count': len(data)
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching mood history: {e}")
        return JsonResponse({'error': 'Failed to fetch mood history'}, status=500)