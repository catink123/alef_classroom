import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

# Check if superuser already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@alef.edu',
        password='admin123',
        role='ADMIN',
        first_name='Admin',
        last_name='User',
        is_verified=True
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
