# apps/university/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
import re

class Faculty(models.Model):
    """Faculty/School within the university"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Department(models.Model):
    """Department within a faculty"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.faculty.code}"

class AcademicYear(models.Model):
    """Academic years (e.g., 2020/2021, 2021/2022)"""
    year = models.CharField(max_length=20, unique=True)  # Format: "2020/2021"
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_year']
    
    def save(self, *args, **kwargs):
        # Ensure only one current academic year
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.year

class Student(models.Model):
    """Core student information from university database"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    # University Information
    matric_number = models.CharField(max_length=20, unique=True, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students')
    year_of_entry = models.IntegerField()  # 2020, 2021, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Profile Image 
    profile_image = models.CharField(max_length=255, blank=True, null=True, help_text="Path to profile image (e.g., students/john_doe.jpg)")
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['matric_number']),
            models.Index(fields=['email']),
            models.Index(fields=['year_of_entry']),
        ]
        ordering = ['last_name', 'first_name']
    
    def get_full_name(self):
        """Return full name with middle name if exists"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_matric_parts(self):
        """Extract year and random part from matric number"""
        # Assuming format: YYYYXXXXX (e.g., 202012345)
        if len(self.matric_number) >= 9:
            year = self.matric_number[:4]
            random_part = self.matric_number[4:]
            return year, random_part
        return None, None
    
    def __str__(self):
        return f"{self.matric_number} - {self.get_full_name()}"


class Enrollment(models.Model):
    """Tracks student enrollments across academic years"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.student.matric_number} - {self.academic_year.year}"