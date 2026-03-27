from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Student, Department, Faculty
import json

# ======================
# UNIVERSITY API VIEWS (Data endpoints)
# ======================

@require_http_methods(["GET"])
def verify_student(request, matric_number):
    """Verify if a student exists by matric number"""
    try:
        student = Student.objects.select_related('department__faculty').get(
            matric_number=matric_number
        )
        return JsonResponse({
            'exists': True,
            'student': {
                'id': student.id,
                'matric_number': student.matric_number,
                'full_name': student.get_full_name(),
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'email': student.email,
                'department': {
                    'id': student.department.id,
                    'name': student.department.name,
                    'code': student.department.code,
                },
                'faculty': {
                    'id': student.department.faculty.id,
                    'name': student.department.faculty.name,
                    'code': student.department.faculty.code,
                },
                'year_of_entry': student.year_of_entry,
                'status': student.status
            }
        })
    except Student.DoesNotExist:
        return JsonResponse({'exists': False, 'error': 'Student not found'}, status=404)


@require_http_methods(["GET"])
def get_student(request, matric_number):
    """Get student details by matric number"""
    try:
        student = Student.objects.select_related('department__faculty').get(
            matric_number=matric_number
        )
        return JsonResponse({
            'id': student.id,
            'matric_number': student.matric_number,
            'full_name': student.get_full_name(),
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'email': student.email,
            'department': {
                'id': student.department.id,
                'name': student.department.name,
                'code': student.department.code,
            },
            'faculty': {
                'id': student.department.faculty.id,
                'name': student.department.faculty.name,
                'code': student.department.faculty.code,
            },
            'year_of_entry': student.year_of_entry,
            'status': student.status
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)


@require_http_methods(["GET"])
def list_departments(request):
    """List all departments with their faculties"""
    departments = Department.objects.select_related('faculty').all()
    data = [{
        'id': dept.id,
        'name': dept.name,
        'code': dept.code,
        'faculty': {
            'id': dept.faculty.id,
            'name': dept.faculty.name,
            'code': dept.faculty.code
        }
    } for dept in departments]
    return JsonResponse({'departments': data})


@require_http_methods(["GET"])
def list_faculties(request):
    """List all faculties"""
    faculties = Faculty.objects.all()
    data = [{
        'id': fac.id,
        'name': fac.name,
        'code': fac.code
    } for fac in faculties]
    return JsonResponse({'faculties': data})


@require_http_methods(["GET"])
def list_students_by_department(request, department_id):
    """List all students in a department"""
    try:
        department = Department.objects.get(id=department_id)
        students = Student.objects.filter(department=department)
        data = [{
            'id': s.id,
            'matric_number': s.matric_number,
            'full_name': s.get_full_name(),
            'email': s.email,
            'year_of_entry': s.year_of_entry,
            'status': s.status
        } for s in students]
        return JsonResponse({
            'department': department.name,
            'students': data
        })
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


@require_http_methods(["GET"])
def list_students_by_year(request, year):
    """List all students who entered in a specific year"""
    students = Student.objects.filter(year_of_entry=year)
    data = [{
        'id': s.id,
        'matric_number': s.matric_number,
        'full_name': s.get_full_name(),
        'email': s.email,
        'department': s.department.name,
        'status': s.status
    } for s in students]
    return JsonResponse({
        'year': year,
        'count': students.count(),
        'students': data
    })


@require_http_methods(["GET"])
def student_stats(request):
    """Get statistics about students"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    by_faculty = {}
    
    faculties = Faculty.objects.all()
    for faculty in faculties:
        count = Student.objects.filter(department__faculty=faculty).count()
        by_faculty[faculty.name] = count
    
    return JsonResponse({
        'total_students': total_students,
        'active_students': active_students,
        'by_faculty': by_faculty,
        'by_year': {
            str(year): Student.objects.filter(year_of_entry=year).count()
            for year in Student.objects.values_list('year_of_entry', flat=True).distinct()
        }
    })