from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import json
import logging
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse

# Import from correct locations
from apps.university.models import Student
from .models import StudentAuth
from .forms import (
    MatricVerificationForm, PasswordCreationForm, LoginForm,
    ForgotPasswordForm, ResetPasswordForm, ResendVerificationForm
)
from .utils import (
    send_verification_email, send_password_reset_email,
    verify_token, email_verification_token, password_reset_token, send_registration_email
)

logger = logging.getLogger(__name__)

# ======================
# API VIEWS (JSON Responses)
# ======================

def api_verify_matric(request):
    """API endpoint for matric verification - Step 1: Verify student exists"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    form = MatricVerificationForm(data)
    
    if form.is_valid():
        student = form.cleaned_data['student']
        
        # Check if student already has a verified account
        if hasattr(student, 'auth') and student.auth.is_email_verified:
            return JsonResponse({
                'success': False,
                'already_registered': True,
                'error': 'An account already exists with this matric number. Please login instead.'
            }, status=400)
        
        # Store in session for confirmation page
        request.session['verifying_matric'] = student.matric_number
        request.session['verifying_student_id'] = str(student.id)
        request.session['student_name'] = student.get_full_name()
        request.session['student_dept'] = student.department.name
        request.session['student_faculty'] = student.department.faculty.name
        request.session['student_year'] = student.year_of_entry
        request.session['student_email'] = student.email
        
        return JsonResponse({
            'success': True,
            'student': {
                'id': student.id,
                'matric_number': student.matric_number,
                'full_name': student.get_full_name(),
                'email': student.email,
                'department': student.department.name,
                'faculty': student.department.faculty.name,
                'year_of_entry': student.year_of_entry,
                'status': student.status,
                'profile_image': getattr(student, 'profile_image', '')
            }
        })
    else:
        return JsonResponse({'errors': form.errors}, status=400)
    
def api_send_registration_email(request):
    """API endpoint to send registration email after confirmation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if we have verified student from confirmation page
    student_id = request.session.get('verifying_student_id')
    if not student_id:
        return JsonResponse({'error': 'No student verified. Please restart registration.'}, status=400)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    # Check if already registered
    if hasattr(student, 'auth') and student.auth.is_email_verified:
        return JsonResponse({
            'success': False,
            'error': 'An account already exists with this matric number. Please login instead.'
        }, status=400)
    
    # Create or get StudentAuth (without password yet)
    student_auth, created = StudentAuth.objects.get_or_create(
        student=student,
        defaults={
            'email': student.email,
            'is_verified': False,
            'is_email_verified': False
        }
    )
    
    # If already exists but not completed registration, update email
    if not created and not student_auth.is_email_verified:
        student_auth.email = student.email
        student_auth.save()
    
    # Generate registration token
    token = student_auth.set_registration_token()
    
    # Send registration email
    email_sent = send_registration_email(student_auth, token, request)
    
    if not email_sent:
        return JsonResponse({
            'success': False,
            'error': 'Failed to send registration email. Please try again.'
        }, status=500)
    
    # Clear session after email sent
    request.session.pop('verifying_matric', None)
    request.session.pop('verifying_student_id', None)
    
    return JsonResponse({
        'success': True,
        'message': 'Registration link sent to your university email. Please check your inbox.',
        'email': student.email
    })
    

def api_create_password(request):
    """API endpoint for password creation (Step 3)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if we have student from registration
    student_id = request.session.get('registering_student_id')
    if not student_id:
        return JsonResponse({'error': 'No registration in progress. Please request a new registration link.'}, status=400)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    form = PasswordCreationForm(data)
    
    if form.is_valid():
        password = form.cleaned_data['password']
        
        # Check if student already has auth
        if hasattr(student, 'auth') and student.auth.is_email_verified:
            return JsonResponse({'error': 'Student already registered'}, status=400)
        
        # Get or create StudentAuth with student's email
        student_auth, created = StudentAuth.objects.get_or_create(
            student=student,
            defaults={
                'email': student.email,
                'is_verified': False,
                'is_email_verified': False
            }
        )
        
        # If existed but not verified, update email
        if not created and not student_auth.is_email_verified:
            student_auth.email = student.email
        
        # Set password and verify email
        student_auth.set_password(password)
        student_auth.is_email_verified = True
        student_auth.is_verified = True
        student_auth.save()
        
        # LOG THE USER IN DIRECTLY
        request.session['student_id'] = str(student.id)
        request.session['matric_number'] = student.matric_number
        request.session['full_name'] = student.get_full_name()
        request.session['department'] = student.department.name
        request.session['faculty'] = student.department.faculty.name
        request.session.set_expiry(60 * 60 * 24 * 7)  # 1 week session
        
        # Clear registration session
        request.session.pop('registering_student_id', None)
        request.session.pop('registering_matric', None)
        
        return JsonResponse({
            'success': True,
            'message': 'Account created successfully! Welcome to MindHaven!',
            'redirect': '/dashboard'
        })
    else:
        print(f"PasswordCreationForm errors: {form.errors}")
        return JsonResponse({'errors': form.errors}, status=400)


def api_login(request):
    """API endpoint for login"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    form = LoginForm(data)
    
    if form.is_valid():
        student = form.cleaned_data['student']
        remember_me = form.cleaned_data.get('remember_me', False)
        
        # Update last login
        student.auth.last_login = timezone.now()
        student.auth.save()
        
        # Set session
        request.session['student_id'] = student.id
        request.session['matric_number'] = student.matric_number
        request.session['full_name'] = student.get_full_name()
        
        # Session expiry
        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 7)  # 1 week
        else:
            request.session.set_expiry(60 * 60 * 8)  # 8 hours
        
        # Get the next URL from the request body (if provided)
        next_url = data.get('next_url', '')
        
        # Validate next URL for security (only allow relative paths)
        if next_url:
            # Only allow relative URLs starting with /
            if next_url.startswith('/') and not next_url.startswith('//'):
                # Optional: Whitelist allowed paths
                allowed_paths = ['/dashboard', '/chat', '/resources', '/mood', '/assessments', '/settings']
                is_allowed = False
                for path in allowed_paths:
                    if next_url.startswith(path):
                        is_allowed = True
                        break
                if not is_allowed:
                    next_url = '/dashboard'
            else:
                next_url = '/dashboard'
        else:
            next_url = '/dashboard'
        
        return JsonResponse({
            'success': True,
            'redirect_url': next_url,
            'student': {
                'matric_number': student.matric_number,
                'name': student.get_full_name(),
                'email': student.auth.email,
                'department': student.department.name,
                'faculty': student.department.faculty.name
            }
        })
    else:
        return JsonResponse({'errors': form.errors}, status=400)
    
    
def api_logout(request):
    """API endpoint for logout"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    request.session.flush()
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})

def logout_page(request):
    """Logout and redirect to landing page"""
    request.session.flush()
    messages.success(request, 'You have been successfully logged out.')
    return redirect('pages:login')


def api_forgot_password(request):
    """API endpoint for password reset request"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    form = ForgotPasswordForm(data)
    
    if form.is_valid():
        student = form.cleaned_data['student']
        
        # Send password reset email
        email_sent = send_password_reset_email(student.auth, request)
        
        return JsonResponse({
            'success': True,
            'email_sent': email_sent,
            'message': 'If an account exists with this matric number, you will receive a password reset email.'
        })
    else:
        return JsonResponse({
            'success': True,
            'message': 'If an account exists with this matric number, you will receive a password reset email.'
        })


def api_resend_verification(request):
    """API endpoint to resend verification email"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    form = ResendVerificationForm(data)
    
    if form.is_valid():
        student = form.cleaned_data['student']
        
        # Resend verification email
        email_sent = send_verification_email(student.auth, request)
        
        return JsonResponse({
            'success': True,
            'email_sent': email_sent,
            'message': 'Verification email resent. Please check your inbox.'
        })
    else:
        return JsonResponse({'errors': form.errors}, status=400)


def api_check_session(request):
    """Check if current session is valid"""
    student_id = request.session.get('student_id')
    
    # Convert to integer if it's a string
    if student_id and isinstance(student_id, str):
        try:
            student_id = int(student_id)
        except ValueError:
            return JsonResponse({'authenticated': False})
    
    if not student_id:
        return JsonResponse({'authenticated': False})
    
    try:
        student = Student.objects.get(id=student_id)
        return JsonResponse({
            'authenticated': True,
            'student': {
                'matric_number': student.matric_number,
                'name': student.get_full_name(),
                'email': student.auth.email if hasattr(student, 'auth') else None
            }
        })
    except Student.DoesNotExist:
        request.session.flush()
        return JsonResponse({'authenticated': False})


def get_current_student(request):
    """Get the currently logged-in student's information"""
    import traceback
    
    print("=" * 50)
    print("get_current_student called")
    print(f"Request session keys: {list(request.session.keys())}")
    
    student_id = request.session.get('student_id')
    print(f"Student ID from session: {student_id}")
    print(f"Student ID type: {type(student_id)}")
    
    if not student_id:
        print("No student_id found in session")
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        print(f"Attempting to get student with id: {student_id}")
        student = Student.objects.select_related('department__faculty').get(id=student_id)
        print(f"Found student: {student}")
        print(f"Student department: {student.department}")
        print(f"Student faculty: {student.department.faculty}")
        
        # Check if student has auth record
        email = None
        if hasattr(student, 'auth'):
            email = student.auth.email
            print(f"Student auth email: {email}")
        else:
            print("No auth record found for student")
        
        response_data = {
            'id': student.id,
            'matric_number': student.matric_number,
            'full_name': student.get_full_name(),
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': email or student.email,
            'department': student.department.name,
            'faculty': student.department.faculty.name,
            'year_of_entry': student.year_of_entry,
            'status': student.status
        }
        
        print(f"Returning user data: {response_data}")
        print("=" * 50)
        return JsonResponse(response_data)
        
    except Student.DoesNotExist:
        print(f"ERROR: Student with id {student_id} not found")
        # Clear invalid session
        request.session.flush()
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return JsonResponse({'error': 'Failed to get user info'}, status=500)


def test_email(request):
    """Simple view to test email sending"""
    try:
        send_mail(
            subject='Test Email from MindHaven',
            message='This is a test email to verify SMTP configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        return HttpResponse('Email sent successfully! Check your inbox.')
    except Exception as e:
        return HttpResponse(f'Error sending email: {str(e)}')


# ======================
# EMAIL VERIFICATION VIEWS
# ======================
def register_confirm(request, matric_number, token):
    """Confirm registration from email link"""
    from apps.university.models import Student
    from .models import StudentAuth
    
    try:
        student = Student.objects.get(matric_number=matric_number)
        student_auth = StudentAuth.objects.get(student=student)
    except (Student.DoesNotExist, StudentAuth.DoesNotExist):
        messages.error(request, 'Invalid registration link.')
        return redirect('pages:landing')
    
    # Check if already registered
    if student_auth.is_email_verified:
        messages.info(request, 'Account already verified. Please login.')
        return redirect('pages:login')
    
    # Check token validity
    if student_auth.registration_token != token:
        messages.error(request, 'Invalid registration link.')
        return redirect('pages:landing')
    
    if not student_auth.is_registration_token_valid():
        messages.error(request, 'Registration link has expired. Please request a new one.')
        return redirect('pages:matric_verification')
    
    # Store in session for password creation
    request.session['registering_student_id'] = str(student.id)
    request.session['registering_matric'] = student.matric_number
    request.session['registering_email'] = student_auth.email
    
    # Clear token (will be used once)
    student_auth.clear_registration_token()
    
    return render(request, 'pages/create_password.html', {
        'matric_number': student.matric_number,
        'student_name': student.get_full_name(),
        'email': student_auth.email
    })
    
    
def verify_email(request, uidb64, token):
    """Verify email from link"""
    student_auth, valid = verify_token(uidb64, token, email_verification_token)
    
    if valid and student_auth:
        if student_auth.is_email_verified:
            messages.info(request, 'Email already verified. Please login.')
        else:
            student_auth.verify_email()
            messages.success(request, 'Email verified successfully! You can now login.')
        return redirect('pages:login')
    else:
        messages.error(request, 'Verification link is invalid or expired.')
        return redirect('pages:login')


def reset_password_confirm(request, uidb64, token):
    """Confirm password reset from link"""
    student_auth, valid = verify_token(uidb64, token, password_reset_token)
    
    if not valid or not student_auth:
        messages.error(request, 'Password reset link is invalid or expired.')
        return redirect('pages:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            student_auth.set_password(form.cleaned_data['password'])
            messages.success(request, 'Password reset successfully. Please login.')
            return redirect('pages:login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'pages/reset_password_confirm.html', {
        'form': form,
        'valid_link': True,
        'student_name': student_auth.student.get_full_name()
    })