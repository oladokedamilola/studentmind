from django.urls import path
from . import views

app_name = 'university'

urlpatterns = [
    # Student data endpoints
    path('students/verify/<str:matric_number>/', views.verify_student, name='verify_student'),
    path('students/<str:matric_number>/', views.get_student, name='get_student'),
    path('students/by-department/<int:department_id>/', views.list_students_by_department, name='students_by_department'),
    path('students/by-year/<int:year>/', views.list_students_by_year, name='students_by_year'),
    path('students/stats/', views.student_stats, name='student_stats'),
    
    # Lookup endpoints
    path('departments/', views.list_departments, name='list_departments'),
    path('faculties/', views.list_faculties, name='list_faculties'),
]