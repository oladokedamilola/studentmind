# apps/university/management/commands/import_students.py
"""
Management command to import student data from JSON file.
Usage: python manage.py import_students --file students.json
"""
from django.core.management.base import BaseCommand, CommandError
from apps.university.models import Faculty, Department, Student, AcademicYear
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Import student data from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to JSON file')
        parser.add_argument('--create-years', action='store_true', help='Create academic years from data')
    
    def handle(self, *args, **options):
        file_path = options.get('file')
        
        if not file_path:
            raise CommandError('Please provide a JSON file path with --file')
        
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
        
        self.stdout.write(f'Reading file: {file_path}')
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.stdout.write(f'Found {len(data)} student records')
        
        # Track statistics
        stats = {
            'faculties_created': 0,
            'departments_created': 0,
            'students_created': 0,
            'students_updated': 0,
            'errors': 0,
        }
        
        for idx, student_data in enumerate(data, 1):
            try:
                self.process_student(student_data, stats, options)
                
                if idx % 100 == 0:
                    self.stdout.write(f'Processed {idx} records...')
                    
            except Exception as e:
                stats['errors'] += 1
                self.stderr.write(f'Error on record {idx}: {str(e)}')
        
        # Create academic years if requested
        if options.get('create_years'):
            self.create_academic_years(data, stats)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        for key, value in stats.items():
            self.stdout.write(f'{key}: {value}')
    
    def process_student(self, data, stats, options):
        """Process a single student record"""
        
        # Get or create faculty
        faculty_data = data.get('faculty', {})
        faculty, created = Faculty.objects.get_or_create(
            code=faculty_data.get('code', ''),
            defaults={
                'name': faculty_data.get('name', '')
            }
        )
        if created:
            stats['faculties_created'] += 1
        
        # Get or create department
        dept_data = data.get('department', {})
        department, created = Department.objects.get_or_create(
            code=dept_data.get('code', ''),
            defaults={
                'name': dept_data.get('name', ''),
                'faculty': faculty
            }
        )
        if created:
            stats['departments_created'] += 1
        
        # Create or update student
        matric_number = data.get('matric_number')
        if not matric_number:
            raise ValueError('matric_number is required')
        
        student_defaults = {
            'first_name': data.get('first_name', ''),
            'middle_name': data.get('middle_name', ''),
            'last_name': data.get('last_name', ''),
            'email': data.get('email', ''),
            'department': department,
            'year_of_entry': data.get('year_of_entry', 0),
            'status': data.get('status', 'active'),
            'profile_image': data.get('profile_image', ''),
        }
        
        student, created = Student.objects.update_or_create(
            matric_number=matric_number,
            defaults=student_defaults
        )
        
        if created:
            stats['students_created'] += 1
        else:
            stats['students_updated'] += 1
    
    def create_academic_years(self, data, stats):
        """Create academic year records from student data"""
        years = set()
        for student_data in data:
            year = student_data.get('year_of_entry')
            if year:
                years.add(year)
        
        for year in sorted(years):
            year_str = f"{year}/{year+1}"
            AcademicYear.objects.get_or_create(
                year=year_str,
                defaults={
                    'start_year': year,
                    'end_year': year + 1
                }
            )
        
        stats['academic_years_created'] = len(years)