from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.utils import timezone
from .models import Student, StudentAuth
from .serializers import (
    MatricNumberSerializer, 
    StudentVerificationSerializer,
    PasswordCreateSerializer,
    LoginSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_matric_number(request):
    """
    Step 1: Student enters matric number
    Returns student details if found in university database
    """
    serializer = MatricNumberSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    matric_number = serializer.validated_data['matric_number']
    
    try:
        student = Student.objects.get(matric_number=matric_number)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found in university database'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already registered
    if hasattr(student, 'auth'):
        return Response(
            {'error': 'Student already registered. Please login.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Return student info for verification
    response_serializer = StudentVerificationSerializer(student)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_password(request):
    """
    Step 2: Create password for verified student
    """
    serializer = PasswordCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    matric_number = serializer.validated_data['matric_number']
    password = serializer.validated_data['password']
    
    try:
        student = Student.objects.get(matric_number=matric_number)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Double-check not already registered
    if hasattr(student, 'auth'):
        return Response(
            {'error': 'Student already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create authentication record
    auth = StudentAuth.objects.create(student=student)
    auth.set_password(password)
    
    return Response(
        {'message': 'Password created successfully. You can now login.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_student(request):
    """
    Step 3: Login with matric number and password
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    student = serializer.validated_data['student']
    
    # Update last login
    student.auth.last_login = timezone.now()
    student.auth.save()
    
    # Create session (Django's built-in session)
    request.session['student_id'] = str(student.id)
    request.session['matric_number'] = student.matric_number
    request.session.set_expiry(60 * 60 * 24 * 7)  # 1 week
    
    # For API clients, you might want to use tokens
    # token, created = Token.objects.get_or_create(user=student)  # Would need to adapt
    
    return Response({
        'message': 'Login successful',
        'student': {
            'matric_number': student.matric_number,
            'name': student.get_full_name(),
            'email': student.email,
            'department': student.department.name,
        },
        'session_id': request.session.session_key
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_student(request):
    """
    Logout student
    """
    request.session.flush()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_current_student(request):
    """
    Get currently logged in student info
    """
    student_id = request.session.get('student_id')
    
    if not student_id:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'matric_number': student.matric_number,
        'name': student.get_full_name(),
        'email': student.email,
        'department': student.department.name,
        'faculty': student.department.faculty.name,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password(request):
    """
    Change password for authenticated student
    """
    student_id = request.session.get('student_id')
    
    if not student_id:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    # Verify old password
    if not student.auth.check_password(old_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password
    if new_password != confirm_password:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update password
    student.auth.set_password(new_password)
    
    return Response(
        {'message': 'Password changed successfully'},
        status=status.HTTP_200_OK
    )