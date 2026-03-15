"""
Settings package initializer.
Loads the appropriate settings based on DJANGO_ENV environment variable.
"""

import os

environment = os.getenv('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *