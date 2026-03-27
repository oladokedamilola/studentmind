from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # API endpoints
    path('api/verify-matric/', views.api_verify_matric, name='api_verify_matric'),
    path('api/send-registration-email/', views.api_send_registration_email, name='api_send_registration_email'),
    path('api/create-password/', views.api_create_password, name='api_create_password'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('logout-page/', views.logout_page, name='logout_page'),
    path('api/forgot-password/', views.api_forgot_password, name='api_forgot_password'),
    path('api/resend-verification/', views.api_resend_verification, name='api_resend_verification'),
    path('api/check-session/', views.api_check_session, name='api_check_session'),
    path('api/test-email/', views.test_email, name='test_email'),
    path('me/', views.get_current_student, name='get_current_student'),
    # Email verification URLs
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_confirm, name='reset_password_confirm'),
    
    # Registration confirmation from email - ADD THIS
    path('register/<str:matric_number>/<str:token>/', views.register_confirm, name='register_confirm'),
]