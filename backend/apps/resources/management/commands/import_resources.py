# apps/resources/management/commands/import_resources.py
"""
Management command to import resources from JSON file.
Usage: python manage.py import_resources --file resources.json
"""

from django.core.management.base import BaseCommand, CommandError
from apps.resources.models import ResourceCategory, ResourceTag, ResourceItem
import json
import os
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import resources from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path to JSON file')
        parser.add_argument('--clear', action='store_true', help='Clear existing resources before import')
    
    def handle(self, *args, **options):
        file_path = options.get('file')
        
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
        
        self.stdout.write(f'Reading file: {file_path}')
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data if requested
        if options.get('clear'):
            self.stdout.write('Clearing existing resources...')
            ResourceItem.objects.all().delete()
            ResourceCategory.objects.all().delete()
            ResourceTag.objects.all().delete()
        
        # Import categories
        categories = {}
        for cat_data in data.get('categories', []):
            category, created = ResourceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data.get('description', ''),
                    'icon': cat_data.get('icon', ''),
                    'order': cat_data.get('order', 0)
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Updated category: {category.name}')
        
        # Import resources
        resources_created = 0
        for res_data in data.get('resources', []):
            # Get or create tags
            tags = []
            for tag_name in res_data.get('tags', []):
                tag, _ = ResourceTag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            
            # Get categories
            resource_categories = []
            for cat_name in res_data.get('categories', []):
                if cat_name in categories:
                    resource_categories.append(categories[cat_name])
            
            # Create resource
            resource, created = ResourceItem.objects.update_or_create(
                title=res_data['title'],
                defaults={
                    'content': res_data['content'],
                    'summary': res_data.get('summary', '')[:300],
                    'resource_type': res_data.get('resource_type', 'article'),
                    'author': res_data.get('author', ''),
                    'source': res_data.get('source', ''),
                    'external_url': res_data.get('external_url', ''),
                    'duration_minutes': res_data.get('duration_minutes'),
                    'is_published': res_data.get('is_published', True),
                    'published_at': timezone.now() if res_data.get('is_published', True) else None
                }
            )
            
            # Set many-to-many relationships
            resource.categories.set(resource_categories)
            resource.tags.set(tags)
            
            # Store video URL separately if needed (we'll add a field)
            if res_data.get('video_url'):
                resource.external_url = res_data['video_url']
                resource.save()
            
            if created:
                resources_created += 1
                self.stdout.write(f'  Created resource: {resource.title}')
            else:
                self.stdout.write(f'  Updated resource: {resource.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import complete: {resources_created} resources created'))