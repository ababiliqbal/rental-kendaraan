import os
import sys
from django.contrib.auth import get_user_model

# Ensure project root is on sys.path so `rental_project` can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_project.settings')
import django
django.setup()
User = get_user_model()

USERNAME = 'testadmin'
EMAIL = 'testadmin@example.com'
PASSWORD = 'TestPass123!'

def main():
    try:
        user = User.objects.get(username=USERNAME)
        user.is_staff = True
        user.is_superuser = True
        user.email = EMAIL
        user.set_password(PASSWORD)
        user.save()
        print('SUPERUSER_UPDATED')
    except User.DoesNotExist:
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print('SUPERUSER_CREATED')

if __name__ == '__main__':
    main()
