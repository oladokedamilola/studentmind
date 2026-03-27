from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Assessment, AssessmentResult

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_assessment(request, assessment_id):
    """Get assessment details and questions"""
    try:
        assessment = Assessment.objects.get(id=assessment_id, is_active=True)
        questions = assessment.questions.all().order_by('order')
        
        data = {
            'id': assessment.id,
            'name': assessment.name,
            'code': assessment.code,
            'description': assessment.description,
            'instructions': assessment.instructions,
            'questions': []
        }
        
        for q in questions:
            data['questions'].append({
                'id': q.id,  # Make sure ID is included
                'text': q.text,
                'type': q.question_type,
                'order': q.order,
                'options': q.option_labels or ['Not at all', 'Several days', 'More than half the days', 'Nearly every day']
            })
        
        return JsonResponse(data)
        
    except Assessment.DoesNotExist:
        return JsonResponse({'error': 'Assessment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching assessment: {e}")
        return JsonResponse({'error': 'Failed to fetch assessment'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def submit_assessment(request, assessment_id):
    """Submit assessment responses and get results"""
    try:
        student_id = request.session.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        assessment = Assessment.objects.get(id=assessment_id, is_active=True)
        data = json.loads(request.body)
        responses = data.get('responses', {})
        
        # Calculate total score (sum of all responses)
        total_score = sum(responses.values())
        
        # Get severity based on score
        severity_info = assessment.get_severity(total_score)
        
        # Save result
        from apps.university.models import Student
        student = Student.objects.get(id=student_id)
        
        result = AssessmentResult.objects.create(
            student=student,
            assessment=assessment,
            total_score=total_score,
            severity=severity_info['level'],
            responses=responses
        )
        
        return JsonResponse({
            'success': True,
            'result_id': result.id,
            'total_score': total_score,
            'severity': severity_info['level'],
            'severity_color': severity_info['color'],
            'severity_description': severity_info['description'],
            'interpretation': get_interpretation(assessment.code, total_score)
        })
        
    except Assessment.DoesNotExist:
        return JsonResponse({'error': 'Assessment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        return JsonResponse({'error': 'Failed to submit assessment'}, status=500)


def get_interpretation(assessment_code, score):
    """Get interpretation text for assessment results"""
    if assessment_code == 'phq9':
        if score <= 4:
            return "Your score suggests minimal depression. Continue with self-care practices."
        elif score <= 9:
            return "Your score suggests mild depression. Consider talking to a counselor and using our coping resources."
        elif score <= 14:
            return "Your score suggests moderate depression. We recommend speaking with a mental health professional."
        elif score <= 19:
            return "Your score suggests moderately severe depression. Please reach out to a mental health professional."
        else:
            return "Your score suggests severe depression. Please seek professional help immediately."
    elif assessment_code == 'gad7':
        if score <= 4:
            return "Your score suggests minimal anxiety. Continue with self-care practices."
        elif score <= 9:
            return "Your score suggests mild anxiety. Consider talking to a counselor and using our coping resources."
        elif score <= 14:
            return "Your score suggests moderate anxiety. We recommend speaking with a mental health professional."
        else:
            return "Your score suggests severe anxiety. Please reach out to a mental health professional."
    return "Thank you for completing this assessment."