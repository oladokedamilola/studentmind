from django.urls import path
from . import views

app_name = 'university'

urlpatterns = [
    # Registration flow
    path('verify-matric/', views.verify_matric_number, name='verify-matric'),
    path('create-password/', views.create_password, name='create-password'),
    
    # Authentication
    path('login/', views.login_student, name='login'),
    path('logout/', views.logout_student, name='logout'),
    path('me/', views.get_current_student, name='me'),
    path('change-password/', views.change_password, name='change-password'),
]