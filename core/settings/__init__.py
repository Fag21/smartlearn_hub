# SmartLearn Hub Settings Package
# Environment-specific settings are loaded based on DJANGO_SETTINGS_MODULE

from .base import *

# Import the appropriate settings based on DJANGO_SETTINGS_MODULE
# Default to development if not specified
import os

settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'core.settings.development')

if settings_module == 'core.settings.production':
    from .production import *
elif settings_module == 'core.settings.testing':
    from .testing import *
else:
    from .development import *