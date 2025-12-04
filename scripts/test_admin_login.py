import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_project.settings')
import django
django.setup()

from django.test import Client

c = Client()
r = c.get('/admin-login/', HTTP_HOST='127.0.0.1')
print('STATUS:', r.status_code)
content = r.content.decode('utf-8')
print('HAS_ADMIN_LOGIN_TITLE:', 'Admin Login' in content)
print('HAS_TESTADMIN:', 'testadmin' in content)
print('HAS_PASSWORD:', 'TestPass123!' in content)
print('SIZE:', len(r.content))
print('--- Content preview (first 500 chars) ---')
print(content[:500])
