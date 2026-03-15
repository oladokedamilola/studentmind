from rest_framework import serializers
from .models import Student, StudentAuth, Faculty, Department
import re

class MatricNumberSerializer(serializers.Serializer):
    """Serializer for matric number verification"""
    matric_number = serializers.CharField(max_length=20)
    
    def validate_matric_number(self, value):
        # Basic format validation (adjust regex as needed)
        if not re.match(r'^\d{9,10}$', value):  # Example: 9-10 digits
            raise serializers.ValidationError("Invalid matric number format")
        return value

class StudentVerificationSerializer(serializers.ModelSerializer):
    """Serializer for student verification response"""
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name')
    faculty_name = serializers.CharField(source='department.faculty.name')
    
    class Meta:
        model = Student
        fields = ['matric_number', 'full_name', 'email', 'department_name', 'faculty_name', 'year_of_entry']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class PasswordCreateSerializer(serializers.Serializer):
    """Serializer for password creation"""
    matric_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Password strength validation
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Password must contain at least one number")
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        return data
    
    def validate_matric_number(self, value):
        # Check if student exists
        try:
            student = Student.objects.get(matric_number=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found in university database")
        
        # Check if already registered
        if hasattr(student, 'auth'):
            raise serializers.ValidationError("Student already registered")
        
        return value

class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    matric_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        matric_number = data.get('matric_number')
        password = data.get('password')
        
        try:
            student = Student.objects.get(matric_number=matric_number)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Invalid matric number or password")
        
        # Check if registered
        if not hasattr(student, 'auth'):
            raise serializers.ValidationError("Account not registered. Please create password first.")
        
        # Check password
        if not student.auth.check_password(password):
            student.auth.increment_login_attempts()
            raise serializers.ValidationError("Invalid matric number or password")
        
        # Check if locked
        from django.utils import timezone
        if student.auth.locked_until and student.auth.locked_until > timezone.now():
            raise serializers.ValidationError("Account locked. Try again later.")
        
        # Success
        student.auth.reset_login_attempts()
        data['student'] = student
        return data