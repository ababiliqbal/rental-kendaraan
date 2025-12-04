import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_project.settings')
import django
django.setup()

from django.test import Client

client = Client()
r = client.get('/login/', HTTP_HOST='127.0.0.1')
content = r.content.decode('utf-8')

print('STATUS:', r.status_code)
print('HAS_ADMIN_INFO:', 'Admin Login' in content)
print('HAS_TESTADMIN:', 'testadmin' in content)
print('HAS_PASSWORD:', 'TestPass123!' in content)
print('HAS_FILL_BTN:', 'fill-admin-btn' in content)
print('HAS_JS:', 'fill-admin-btn' in content and 'value' in content)
print('')

if all([
    r.status_code == 200,
    'Admin Login' in content,
    'testadmin' in content,
    'TestPass123!' in content,
    'fill-admin-btn' in content
]):
    print('✓ Login page dengan admin credentials berhasil dibuat!')
else:
    print('✗ Ada masalah dengan login page')
