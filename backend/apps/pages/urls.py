from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Public pages
    path('', views.landing, name='landing'),
    path('verify/', views.matric_verification, name='matric_verification'),
    path('confirm/', views.student_confirmation, name='student_confirmation'),
    path('create-password/', views.create_password, name='create_password'),
    path('login/', views.login_page, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # Protected pages
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints for form submissions
    path('api/verify-matric/', views.api_verify_matric, name='api_verify_matric'),
]