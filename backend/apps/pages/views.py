from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from functools import wraps

import logging

logger = logging.getLogger(__name__)

# ======================
# HELPER DECORATOR
# ======================

def login_required_view(view_func):
    """Decorator to check if user is logged in"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):
            return redirect('pages:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ======================
# PUBLIC PAGES (No Login Required)
# ======================

def landing(request):
    """Landing page"""
    return render(request, 'pages/landing.html')

@ensure_csrf_cookie
def matric_verification(request):
    """Step 1: Matric number input"""
    if request.session.get('student_id'):
        return redirect('pages:dashboard')
    return render(request, 'pages/matric_verification.html')

@ensure_csrf_cookie
def student_confirmation(request):
    """Step 2: Confirm student details"""
    if not request.session.get('verifying_matric'):
        return redirect('pages:matric_verification')
    
    # Get student data from session (set by API)
    context = {
        'student_name': request.session.get('student_name', ''),
        'matric_number': request.session.get('verifying_matric', ''),
        'department': request.session.get('student_dept', ''),
        'faculty': request.session.get('student_faculty', '')
    }
    return render(request, 'pages/student_confirmation.html', context)

@ensure_csrf_cookie
def create_password(request):
    """Step 3: Create password"""
    if not request.session.get('verified_student_id'):
        return redirect('pages:matric_verification')
    return render(request, 'pages/create_password.html')

@ensure_csrf_cookie
def login_page(request):
    """Login page"""
    if request.session.get('student_id'):
        # If already logged in, redirect to the next URL or dashboard
        next_url = request.GET.get('next', '')
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('pages:dashboard')
    
    # Pass next URL to template for reference (optional)
    context = {
        'next_url': request.GET.get('next', '')
    }
    return render(request, 'pages/login.html', context)

def forgot_password(request):
    """Forgot password page"""
    return render(request, 'pages/forgot_password.html')

def reset_password_confirm_page(request):
    """Page shown after clicking reset link"""
    return render(request, 'pages/reset_password_confirm.html')

def email_verification_sent(request):
    """Page shown after registration - check email"""
    email = request.session.get('verification_email', 'your email address')
    return render(request, 'pages/email_verification_sent.html', {
        'email': email
    })

def resend_verification_page(request):
    """Page to resend verification email"""
    return render(request, 'pages/resend_verification.html')

def about(request):
    """About page"""
    return render(request, 'pages/about.html')

def privacy(request):
    """Privacy policy page"""
    return render(request, 'pages/privacy.html')

def terms(request):
    """Terms of service page"""
    return render(request, 'pages/terms.html')

def contact(request):
    """Contact page"""
    return render(request, 'pages/contact.html')


# ======================
# PROTECTED PAGES (Login Required)
# ======================

@login_required_view
def dashboard(request):
    """Main dashboard after login"""
    return render(request, 'pages/dashboard.html')


# ======================
# CHAT PAGES
# ======================

@login_required_view
def chat_list(request):
    """List all conversations"""
    return render(request, 'pages/chat/chat_list.html')

@login_required_view
def chat_detail(request, conversation_id):
    """Individual chat thread"""
    return render(request, 'pages/chat/chat_detail.html', {
        'conversation_id': conversation_id
    })

@login_required_view
def chat_new(request):
    """Start new conversation"""
    return render(request, 'pages/chat/chat_new.html')

@login_required_view
def chat_search(request):
    """Search conversations"""
    return render(request, 'pages/chat/chat_search.html')


# ======================
# MOOD TRACKING PAGES
# ======================

@login_required_view
def mood_log(request):
    """Log daily mood"""
    return render(request, 'pages/mood/mood_log.html')

@login_required_view
def mood_history(request):
    """View mood history with charts"""
    return render(request, 'pages/mood/mood_history.html')

@login_required_view
def mood_calendar(request):
    """Calendar view of moods"""
    return render(request, 'pages/mood/mood_calendar.html')


# ======================
# RESOURCES PAGES
# ======================

@login_required_view
def resources_list(request):
    """Browse all resources"""
    # Fetch resources from database
    from apps.resources.models import ResourceItem, ResourceCategory
    
    resources = ResourceItem.objects.filter(is_published=True)
    categories = ResourceCategory.objects.all()
    
    # Get featured resources (first 2 by view count or random)
    featured_resources = resources.order_by('-view_count')[:2]
    if featured_resources.count() < 2:
        featured_resources = resources[:2]
    
    context = {
        'resources': resources,
        'categories': categories,
        'featured_resources': featured_resources,
        'all_resources': resources
    }
    return render(request, 'pages/resources/resources_list.html', context)


@login_required_view
def resource_detail(request, resource_id):
    """View single resource"""
    from apps.resources.models import ResourceItem
    
    try:
        # Get the resource from database
        resource = ResourceItem.objects.get(id=resource_id, is_published=True)
        
        # Increment view count
        resource.view_count += 1
        resource.save()
        
        # Get related resources (same categories)
        related_resources = ResourceItem.objects.filter(
            categories__in=resource.categories.all(),
            is_published=True
        ).exclude(id=resource.id).distinct()[:3]
        
        context = {
            'resource': resource,
            'related_resources': related_resources,
            'resource_id': resource_id  # Keep for JavaScript if needed
        }
        return render(request, 'pages/resources/resource_detail.html', context)
        
    except ResourceItem.DoesNotExist:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Resource not found')
        return redirect('pages:resources_list')


@login_required_view
def resources_saved(request):
    """View saved resources"""
    return render(request, 'pages/resources/resources_saved.html')


@login_required_view
def resources_search(request):
    """Search resources"""
    return render(request, 'pages/resources/resources_search.html')

# ======================
# ASSESSMENTS PAGES
# ======================

@login_required_view
def assessments_list(request):
    """List all available assessments"""
    from apps.assessment.models import Assessment
    
    assessments = Assessment.objects.filter(is_active=True)
    
    context = {
        'assessments': assessments
    }
    return render(request, 'pages/assessments/assessments_list.html', context)


@login_required_view
def assessment_take(request, assessment_id):
    """Take an assessment"""
    from apps.assessment.models import Assessment
    
    try:
        assessment = Assessment.objects.get(id=assessment_id, is_active=True)
    except Assessment.DoesNotExist:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Assessment not found')
        return redirect('pages:assessments_list')
    
    context = {
        'assessment': assessment,
        'questions': assessment.questions.all().order_by('order')
    }
    return render(request, 'pages/assessments/assessment_take.html', context)


@login_required_view
def assessment_results(request, result_id):
    """View assessment results"""
    from apps.assessment.models import AssessmentResult
    from django.contrib import messages
    from django.shortcuts import redirect
    
    try:
        student_id = request.session.get('student_id')
        result = AssessmentResult.objects.get(id=result_id, student_id=student_id)
        
        # Create a dictionary of questions
        questions_dict = {str(q.id): q.text for q in result.assessment.questions.all()}
        
        # Prepare responses with question text
        responses_with_text = []
        for question_id, score in result.responses.items():
            question_text = questions_dict.get(str(question_id), 'Unknown question')
            responses_with_text.append({
                'text': question_text,
                'score': score,
                'score_label': get_score_label(score)
            })
        
        # Calculate score percentage for progress bar
        score_percentage = (result.total_score / result.assessment.max_score) * 100
        
        # Severity levels for the assessment
        severity_levels = get_severity_levels(result.assessment.code)
        
        # Interpretation based on score
        interpretation = get_interpretation(result.assessment.code, result.total_score)
        
        # Recommendations based on severity
        recommendations = get_recommendations(result.assessment.code, result.severity)
        
        context = {
            'result': result,
            'responses_with_text': responses_with_text,
            'score_percentage': score_percentage,
            'severity_levels': severity_levels,
            'interpretation': interpretation,
            'recommendations': recommendations
        }
        return render(request, 'pages/assessments/assessment_results.html', context)
        
    except AssessmentResult.DoesNotExist:
        messages.error(request, 'Assessment result not found')
        return redirect('pages:assessments_list')
    except Exception as e:
        logger.error(f"Error loading assessment result: {e}")
        messages.error(request, 'Error loading assessment results')
        return redirect('pages:assessments_list')


def get_score_label(score):
    """Convert score to label for display"""
    score_int = int(score) if score else 0
    if score_int == 0:
        return "0 - Not at all"
    elif score_int == 1:
        return "1 - Several days"
    elif score_int == 2:
        return "2 - More than half the days"
    elif score_int == 3:
        return "3 - Nearly every day"
    else:
        return f"{score_int} - Selected"


def get_severity_levels(assessment_code):
    """Get severity level labels for the assessment"""
    if assessment_code == 'phq9':
        return ['Minimal', 'Mild', 'Moderate', 'Mod-Severe', 'Severe']
    elif assessment_code == 'gad7':
        return ['Minimal', 'Mild', 'Moderate', 'Severe']
    else:
        return ['Low', 'Moderate', 'High']


def get_interpretation(assessment_code, score):
    """Get interpretation text for assessment results"""
    if assessment_code == 'phq9':
        if score <= 4:
            return "Your score suggests minimal depression. Continue with self-care practices and monitor your mood."
        elif score <= 9:
            return "Your score suggests mild depression. Consider talking to a counselor and using our coping resources. Small lifestyle changes can make a difference."
        elif score <= 14:
            return "Your score suggests moderate depression. We recommend speaking with a mental health professional. Our resources can provide additional support."
        elif score <= 19:
            return "Your score suggests moderately severe depression. Please reach out to a mental health professional. You don't have to navigate this alone."
        else:
            return "Your score suggests severe depression. Please seek professional help immediately. Contact your university counseling center or a crisis hotline."
    elif assessment_code == 'gad7':
        if score <= 4:
            return "Your score suggests minimal anxiety. Continue with self-care practices and mindfulness exercises."
        elif score <= 9:
            return "Your score suggests mild anxiety. Consider practicing relaxation techniques and talking with a counselor."
        elif score <= 14:
            return "Your score suggests moderate anxiety. We recommend speaking with a mental health professional about coping strategies."
        else:
            return "Your score suggests severe anxiety. Please reach out to a mental health professional for support."
    return "Thank you for completing this assessment. Your results help track your mental health journey."


def get_recommendations(assessment_code, severity):
    """Get recommendations based on assessment severity"""
    recommendations = []
    
    # Base recommendations for all users
    recommendations.append({
        'icon': 'fas fa-comment',
        'title': 'Consider speaking with a counselor',
        'description': 'Talking to a professional can help you develop coping strategies'
    })
    
    recommendations.append({
        'icon': 'fas fa-smile',
        'title': 'Try our mood tracking feature',
        'description': 'Track your daily mood to identify patterns and triggers'
    })
    
    recommendations.append({
        'icon': 'fas fa-book-open',
        'title': 'Explore coping resources',
        'description': 'Check our library of articles and exercises for managing stress and anxiety'
    })
    
    # Additional recommendations based on severity
    if severity in ['Moderate', 'Mod-Severe', 'Severe']:
        recommendations.insert(0, {
            'icon': 'fas fa-phone-alt',
            'title': 'Schedule an appointment with a counselor',
            'description': 'Your score indicates you may benefit from professional support'
        })
    
    if severity in ['Severe']:
        recommendations.insert(0, {
            'icon': 'fas fa-exclamation-triangle',
            'title': 'Crisis support available 24/7',
            'description': 'If you\'re in crisis, please reach out to emergency services or a crisis hotline immediately'
        })
    
    return recommendations


@login_required_view
def assessment_history(request):
    """View past assessment results"""
    from apps.assessment.models import AssessmentResult
    
    student_id = request.session.get('student_id')
    results = AssessmentResult.objects.filter(
        student_id=student_id
    ).order_by('-completed_at')
    
    context = {
        'results': results
    }
    return render(request, 'pages/assessments/assessment_history.html', context)


@login_required_view
def assessment_compare(request):
    """Compare results over time"""
    from apps.assessment.models import AssessmentResult
    
    student_id = request.session.get('student_id')
    assessment_code = request.GET.get('assessment', 'phq9')
    
    results = AssessmentResult.objects.filter(
        student_id=student_id,
        assessment__code=assessment_code
    ).order_by('completed_at')
    
    context = {
        'results': results,
        'assessment_code': assessment_code
    }
    return render(request, 'pages/assessments/assessment_compare.html', context)

# ======================
# ACCOUNT MANAGEMENT PAGES
# ======================

@login_required_view
def settings(request):
    """Account settings"""
    return render(request, 'pages/account/settings.html')

@login_required_view
def change_password(request):
    """Change password page"""
    return render(request, 'pages/account/change_password.html')

@login_required_view
def notification_preferences(request):
    """Notification preferences"""
    return render(request, 'pages/account/notification_preferences.html')

@login_required_view
def delete_account(request):
    """Account deletion confirmation"""
    return render(request, 'pages/account/delete_account.html')


# ======================
# SUPPORT PAGES (Login Required)
# ======================

@login_required_view
def crisis_support(request):
    """Crisis support page with emergency resources"""
    return render(request, 'pages/support/crisis_support.html')


@login_required_view
def find_counselor(request):
    """Find a counselor page"""
    return render(request, 'pages/support/find_counselor.html')


@login_required_view
def support_groups(request):
    """Support groups page"""
    return render(request, 'pages/support/support_groups.html')


@login_required_view
def help_faqs(request):
    """Help and FAQs page"""
    return render(request, 'pages/help_faqs.html')


# ======================
# ERROR PAGES
# ======================

def custom_404(request, exception):
    """404 error page"""
    return render(request, 'pages/errors/404.html', status=404)

def custom_500(request):
    """500 error page"""
    return render(request, 'pages/errors/500.html', status=500)