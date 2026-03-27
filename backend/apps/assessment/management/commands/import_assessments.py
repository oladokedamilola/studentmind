# apps/assessment/management/commands/import_assessments.py
"""
Management command to import assessments from JSON file.
Usage: python manage.py import_assessments --file data/assessments.json
"""

from django.core.management.base import BaseCommand, CommandError
from apps.assessment.models import Assessment, Question
import json
import os

class Command(BaseCommand):
    help = 'Import assessments from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path to JSON file')
        parser.add_argument('--clear', action='store_true', help='Clear existing assessments before import')
    
    def handle(self, *args, **options):
        file_path = options.get('file')
        
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
        
        self.stdout.write(f'Reading file: {file_path}')
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data if requested
        if options.get('clear'):
            self.stdout.write('Clearing existing assessments...')
            Question.objects.all().delete()
            Assessment.objects.all().delete()
        
        # Import assessments
        for asmt_data in data.get('assessments', []):
            assessment, created = Assessment.objects.update_or_create(
                code=asmt_data['code'],
                defaults={
                    'name': asmt_data['name'],
                    'description': asmt_data['description'],
                    'instructions': asmt_data.get('instructions', ''),
                    'scoring_guide': asmt_data.get('scoring_guide', ''),
                    'min_score': asmt_data.get('min_score', 0),
                    'max_score': asmt_data.get('max_score', 27),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'  Created assessment: {assessment.name}')
            else:
                self.stdout.write(f'  Updated assessment: {assessment.name}')
            
            # Import questions
            for idx, q_data in enumerate(asmt_data.get('questions', []), 1):
                question, q_created = Question.objects.update_or_create(
                    assessment=assessment,
                    order=q_data.get('order', idx),
                    defaults={
                        'text': q_data['text'],
                        'question_type': 'likert',
                        'option_labels': ["Not at all", "Several days", "More than half the days", "Nearly every day"]
                    }
                )
                
                if q_created:
                    self.stdout.write(f'    Created question: {question.text[:50]}...')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import complete!'))