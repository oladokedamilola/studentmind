from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from django.conf import settings

# Public pages (no login required)
def landing(request):
    """Landing page"""
    return render(request, 'pages/landing.html')

@ensure_csrf_cookie
def matric_verification(request):
    """Step 1: Matric number input"""
    # If already logged in, redirect to dashboard
    if request.session.get('student_id'):
        return redirect('dashboard')
    return render(request, 'pages/matric_verification.html')

@ensure_csrf_cookie
def student_confirmation(request):
    """Step 2: Confirm student details"""
    # Check if we have matric in session from step 1
    if not request.session.get('verifying_matric'):
        return redirect('matric_verification')
    return render(request, 'pages/student_confirmation.html')

@ensure_csrf_cookie
def create_password(request):
    """Step 3: Create password"""
    # Check if we have verified student in session from step 2
    if not request.session.get('verified_student_id'):
        return redirect('matric_verification')
    return render(request, 'pages/create_password.html')

@ensure_csrf_cookie
def login_page(request):
    """Login page"""
    if request.session.get('student_id'):
        return redirect('dashboard')
    return render(request, 'pages/login.html')

def forgot_password(request):
    """Forgot password page"""
    return render(request, 'pages/forgot_password.html')

# Protected pages (login required)
def dashboard(request):
    """Main dashboard after login"""
    if not request.session.get('student_id'):
        return redirect('login')
    return render(request, 'pages/dashboard.html')

# API integration views (handle form submissions)
def api_verify_matric(request):
    """Handle matric verification form submission"""
    if request.method == 'POST':
        # This will call your backend API
        # We'll implement this next
        pass
    return JsonResponse({'error': 'Method not allowed'}, status=405)