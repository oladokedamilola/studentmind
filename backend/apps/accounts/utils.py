from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
import six
import logging

# Import StudentAuth model
from .models import StudentAuth

logger = logging.getLogger(__name__)

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for email verification and password reset"""
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.is_email_verified)
        )

# Create token generator instances
email_verification_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()

def send_registration_email(student_auth, token, request):
    """Send registration link to student's email"""
    try:
        # Build registration URL
        registration_url = request.build_absolute_uri(
                reverse('pages:register_confirm', kwargs={
                    'matric_number': student_auth.student.matric_number,
                    'token': token
                })
            )
        
        # Email subject and message
        subject = 'Complete Your Registration - MindHaven'
        
        student_name = student_auth.student.get_full_name()
        
        # HTML email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Nunito', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 16px; }}
                .header {{ background: #9CAF88; padding: 30px; text-align: center; border-radius: 16px 16px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ padding: 40px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #9CAF88; color: white; 
                          text-decoration: none; border-radius: 25px; margin: 20px 0; }}
                .footer {{ background: #E6E6FA; padding: 20px; text-align: center; font-size: 14px; }}
                .warning {{ background: #FFF3CD; border-left: 4px solid #FFA500; padding: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏡 MindHaven</h1>
                </div>
                <div class="content">
                    <h2>Complete Your Registration, {student_name}!</h2>
                    <p>You're almost there! Click the button below to set up your password and complete your MindHaven registration.</p>
                    <div style="text-align: center;">
                        <a href="{registration_url}" class="button">Create Your Account</a>
                    </div>
                    <div class="warning">
                        <p><strong>⚠️ This link expires in 24 hours.</strong></p>
                        <p>If you didn't request this, please ignore this email. No account will be created.</p>
                    </div>
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all;">{registration_url}</p>
                </div>
                <div class="footer">
                    <p>© 2025 MindHaven. Your campus sanctuary.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_message = f"""
        Hello {student_name},
        
        Complete your MindHaven registration by clicking the link below:
        {registration_url}
        
        This link expires in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        MindHaven Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student_auth.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Registration email sent to {student_auth.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send registration email: {e}")
        return False
    

def send_verification_email(student_auth, request):
    """Send email verification link to student"""
    try:
        # Generate token
        token = email_verification_token.make_token(student_auth)
        uid = urlsafe_base64_encode(force_bytes(student_auth.pk))
        
        # Build verification URL
        verification_url = request.build_absolute_uri(
            f'/verify-email/{uid}/{token}/'
        )
        
        # Email subject and message
        subject = 'Verify your email - MindHaven'
        
        # HTML email content
        html_message = render_to_string('accounts/emails/verification_email.html', {
            'student': student_auth.student,
            'verification_url': verification_url,
            'site_name': 'MindHaven',
            'support_email': settings.SUPPORT_EMAIL or 'support@mindhaven.com'
        })
        
        # Plain text fallback
        text_message = f"""
        Hello {student_auth.student.get_full_name()},
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        MindHaven Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@mindhaven.com',
            recipient_list=[student_auth.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {student_auth.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


def send_password_reset_email(student_auth, request):
    """Send password reset link to student"""
    try:
        # Generate token
        token = password_reset_token.make_token(student_auth)
        uid = urlsafe_base64_encode(force_bytes(student_auth.pk))
        
        # Build reset URL
        reset_url = request.build_absolute_uri(
            f'/reset-password/{uid}/{token}/'
        )
        
        # Email subject and message
        subject = 'Reset your password - MindHaven'
        
        # HTML email content
        html_message = render_to_string('accounts/emails/password_reset_email.html', {
            'student': student_auth.student,
            'reset_url': reset_url,
            'site_name': 'MindHaven',
            'expiry_hours': 24
        })
        
        # Plain text fallback
        text_message = f"""
        Hello {student_auth.student.get_full_name()},
        
        You requested to reset your password. Click the link below:
        {reset_url}
        
        This link expires in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        MindHaven Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@mindhaven.com',
            recipient_list=[student_auth.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {student_auth.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False


def verify_token(uidb64, token, token_generator):
    """Verify token and return user if valid"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        student_auth = StudentAuth.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, StudentAuth.DoesNotExist):
        return None, False
    
    if token_generator.check_token(student_auth, token):
        return student_auth, True
    return student_auth, False