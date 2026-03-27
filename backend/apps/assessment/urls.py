from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('api/<int:assessment_id>/', views.get_assessment, name='get_assessment'),
    path('api/<int:assessment_id>/submit/', views.submit_assessment, name='submit_assessment'),
]