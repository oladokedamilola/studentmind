from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import re

# Import Student from university app, NOT from accounts.models
from apps.university.models import Student
from .models import StudentAuth

class MatricVerificationForm(forms.Form):
    """Form for step 1: Matric number verification"""
    matric_number = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d{9,10}$',
                message='Matric number must be 9-10 digits'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 202012345',
            'autocomplete': 'off'
        })
    )
    
    def clean_matric_number(self):
        matric = self.cleaned_data['matric_number']
        
        # Check if student exists in university database
        try:
            student = Student.objects.get(matric_number=matric)
        except Student.DoesNotExist:
            raise forms.ValidationError('Student not found in university database')
        
        # Check if already registered
        if hasattr(student, 'auth') and student.auth.is_verified:
            raise forms.ValidationError('This student is already registered. Please login.')
        
        # Store student in cleaned_data for use in views
        self.cleaned_data['student'] = student
        return matric


class PasswordCreationForm(forms.Form):
    """Form for step 3: Create password (email already known from database)"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Password strength validation
        errors = []
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number')
            
        if errors:
            raise forms.ValidationError(errors)
            
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm and password != confirm:
            raise forms.ValidationError({'confirm_password': 'Passwords do not match'})
            
        return cleaned_data


class LoginForm(forms.Form):
    """Form for login"""
    matric_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matric Number',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        matric = cleaned_data.get('matric_number')
        password = cleaned_data.get('password')
        
        if matric and password:
            try:
                student = Student.objects.get(matric_number=matric)
                
                # Check if student has auth record
                if not hasattr(student, 'auth'):
                    raise forms.ValidationError('Account not registered. Please create password first.')
                
                # Check if account is locked
                if student.auth.is_locked():
                    raise forms.ValidationError(
                        f'Account locked. Try again in {student.auth.locked_until.minute} minutes.'
                    )
                
                # Verify password
                if not student.auth.check_password(password):
                    student.auth.increment_login_attempts()
                    remaining = 5 - student.auth.login_attempts
                    
                    if remaining > 0:
                        raise forms.ValidationError(f'Invalid password. {remaining} attempt(s) remaining.')
                    else:
                        raise forms.ValidationError('Account locked due to too many failed attempts.')
                
                # Check if email verified
                if not student.auth.is_email_verified:
                    raise forms.ValidationError(
                        'Please verify your email first. Check your inbox for the verification link.'
                    )
                
                # Success - reset attempts and store student
                student.auth.reset_login_attempts()
                cleaned_data['student'] = student
                
            except Student.DoesNotExist:
                raise forms.ValidationError('Invalid matric number or password')
                
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """Form for password reset request"""
    matric_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your matric number'
        })
    )
    
    def clean_matric_number(self):
        matric = self.cleaned_data['matric_number']
        
        try:
            student = Student.objects.get(matric_number=matric)
        except Student.DoesNotExist:
            raise forms.ValidationError('Student not found')
        
        if not hasattr(student, 'auth'):
            raise forms.ValidationError('No account found with this matric number')
        
        if not student.auth.is_email_verified:
            raise forms.ValidationError('Email not verified. Please contact support.')
        
        self.cleaned_data['student'] = student
        return matric


class ResetPasswordForm(forms.Form):
    """Form for resetting password (from email link)"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Same password strength validation
        errors = []
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number')
            
        if errors:
            raise forms.ValidationError(errors)
            
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm and password != confirm:
            raise forms.ValidationError({'confirm_password': 'Passwords do not match'})
            
        return cleaned_data


class ResendVerificationForm(forms.Form):
    """Form to resend verification email"""
    matric_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your matric number'
        })
    )
    
    def clean_matric_number(self):
        matric = self.cleaned_data['matric_number']
        
        try:
            student = Student.objects.get(matric_number=matric)
        except Student.DoesNotExist:
            raise forms.ValidationError('Student not found')
        
        if not hasattr(student, 'auth'):
            raise forms.ValidationError('No account found')
        
        if student.auth.is_email_verified:
            raise forms.ValidationError('Email already verified. Please login.')
        
        self.cleaned_data['student'] = student
        return matric