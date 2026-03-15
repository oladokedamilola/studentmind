"""
Management command to test GitHub Models connection
Usage: python manage.py test_github_models
"""
from django.core.management.base import BaseCommand
from apps.chat.services.openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test connection to GitHub Models (Microsoft Foundry Inference)'
    
    def add_arguments(self, parser):
        parser.add_argument('--message', type=str, default='Hello, are you working?', help='Test message to send')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing GitHub Models connection...'))
        
        service = OpenAIService()
        success, result = service.test_connection()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'✅ Connection successful!'))
            self.stdout.write(f'Response: {result}')
        else:
            self.stdout.write(self.style.ERROR(f'❌ Connection failed!'))
            self.stdout.write(self.style.ERROR(f'Error: {result}'))
            
        # Test full response generation
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Testing full response generation:')
        
        test_message = options['message']
        response = service.generate_response(test_message)
        
        if response['success']:
            self.stdout.write(self.style.SUCCESS(f'\nUser: {test_message}'))
            self.stdout.write(f'AI: {response["message"]}')
            self.stdout.write(f'\nToken usage: {response["token_usage"]}')
            self.stdout.write(f'Response time: {response["response_time"]}ms')
        else:
            self.stdout.write(self.style.ERROR(f'Error: {response["message"]}'))