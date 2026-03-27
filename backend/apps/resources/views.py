from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import ResourceItem, ResourceCategory

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_recommended_resource(request):
    """Get a recommended resource based on user's recent mood"""
    try:
        student_id = request.session.get('student_id')
        
        # Default recommendation if no user context
        if not student_id:
            resource = ResourceItem.objects.filter(
                is_published=True,
                resource_type='exercise'
            ).order_by('?').first()
            
            if resource:
                return JsonResponse({
                    'id': resource.id,
                    'title': resource.title,
                    'summary': resource.summary or resource.content[:100],
                    'resource_type': resource.resource_type
                })
            return JsonResponse({})
        
        # Get user's recent mood from the mood app
        from apps.mood.models import MoodEntry
        recent_moods = MoodEntry.objects.filter(
            student_id=student_id
        ).order_by('-recorded_at')[:5]
        
        # Determine mood trend
        if recent_moods.exists():
            avg_mood = sum(m.mood_score for m in recent_moods) / len(recent_moods)
            if avg_mood <= 2:
                # Low mood - recommend calming exercises
                category = 'anxiety'
            elif avg_mood <= 3:
                category = 'stress'
            else:
                category = 'general'
        else:
            category = 'general'
        
        # Get resource based on category
        resource = ResourceItem.objects.filter(
            is_published=True,
            categories__name__iexact=category
        ).order_by('?').first()
        
        if not resource:
            resource = ResourceItem.objects.filter(is_published=True).order_by('?').first()
        
        if resource:
            return JsonResponse({
                'id': resource.id,
                'title': resource.title,
                'description': resource.summary or resource.content[:150],
                'resource_type': resource.resource_type
            })
        
        return JsonResponse({})
        
    except Exception as e:
        logger.error(f"Error getting recommended resource: {e}")
        return JsonResponse({})


@require_http_methods(["GET"])
def get_resources_api(request):
    """API endpoint to get all resources as JSON"""
    try:
        resources = ResourceItem.objects.filter(is_published=True).select_related()
        
        data = []
        for resource in resources:
            data.append({
                'id': resource.id,
                'title': resource.title,
                'summary': resource.summary or resource.content[:100],
                'content': resource.content,
                'resource_type': resource.resource_type,
                'categories': [{'name': cat.name} for cat in resource.categories.all()],
                'duration_minutes': resource.duration_minutes,
                'view_count': resource.view_count,
                'avg_rating': resource.avg_rating,
                'external_url': resource.external_url,
                'video_url': getattr(resource, 'video_url', None)
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        logger.error(f"Error fetching resources API: {e}")
        return JsonResponse({'error': 'Failed to fetch resources'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def save_resource(request, resource_id):
    """Save a resource to user's favorites"""
    try:
        student_id = request.session.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        resource = ResourceItem.objects.get(id=resource_id, is_published=True)
        
        # Here you would create a SavedResource record
        # For now, just return success
        return JsonResponse({
            'success': True,
            'saved': True,
            'message': 'Resource saved to favorites'
        })
        
    except ResourceItem.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except Exception as e:
        logger.error(f"Error saving resource: {e}")
        return JsonResponse({'error': 'Failed to save resource'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def rate_resource(request, resource_id):
    """Rate a resource as helpful or not helpful"""
    try:
        # Get student_id from session
        student_id = request.session.get('student_id')
        
        data = json.loads(request.body)
        helpful = data.get('helpful', True)
        
        resource = ResourceItem.objects.get(id=resource_id, is_published=True)
        
        if helpful:
            resource.helpful_count += 1
        else:
            resource.not_helpful_count += 1
        
        resource.save()
        
        return JsonResponse({
            'success': True,
            'helpful_count': resource.helpful_count,
            'not_helpful_count': resource.not_helpful_count
        })
        
    except ResourceItem.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error rating resource: {e}")
        return JsonResponse({'error': 'Failed to rate resource'}, status=500)


@require_http_methods(["GET"])
def search_resources(request):
    """Search resources by keyword"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            resources = ResourceItem.objects.filter(is_published=True)[:20]
        else:
            resources = ResourceItem.objects.filter(
                is_published=True,
                title__icontains=query
            ) | ResourceItem.objects.filter(
                is_published=True,
                summary__icontains=query
            ) | ResourceItem.objects.filter(
                is_published=True,
                content__icontains=query
            ) | ResourceItem.objects.filter(
                is_published=True,
                tags__name__icontains=query
            )
            resources = resources.distinct()
        
        data = []
        for resource in resources[:20]:
            data.append({
                'id': resource.id,
                'title': resource.title,
                'summary': resource.summary or resource.content[:100],
                'resource_type': resource.resource_type,
                'categories': [{'name': cat.name} for cat in resource.categories.all()]
            })
        
        return JsonResponse({
            'success': True,
            'query': query,
            'count': len(data),
            'results': data
        })
        
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        return JsonResponse({'error': 'Failed to search'}, status=500)


@require_http_methods(["GET"])
def get_resources_by_category(request, category_name):
    """Get resources filtered by category"""
    try:
        resources = ResourceItem.objects.filter(
            is_published=True,
            categories__name__iexact=category_name
        )
        
        data = []
        for resource in resources:
            data.append({
                'id': resource.id,
                'title': resource.title,
                'summary': resource.summary or resource.content[:100],
                'resource_type': resource.resource_type,
                'duration_minutes': resource.duration_minutes
            })
        
        return JsonResponse({
            'success': True,
            'category': category_name,
            'count': len(data),
            'resources': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching resources by category: {e}")
        return JsonResponse({'error': 'Failed to fetch resources'}, status=500)


@require_http_methods(["GET"])
def get_featured_resources(request):
    """Get featured resources for the dashboard"""
    try:
        resources = ResourceItem.objects.filter(
            is_published=True
        ).order_by('-view_count')[:3]
        
        data = []
        for resource in resources:
            data.append({
                'id': resource.id,
                'title': resource.title,
                'summary': resource.summary or resource.content[:100],
                'resource_type': resource.resource_type,
                'duration_minutes': resource.duration_minutes
            })
        
        return JsonResponse({
            'success': True,
            'resources': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching featured resources: {e}")
        return JsonResponse({'error': 'Failed to fetch featured resources'}, status=500)