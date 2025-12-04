import os
import sys

# Ensure project root is on sys.path so `rental_project` can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_project.settings')
import django
django.setup()

from django.test import Client

USERNAME = 'testadmin'
PASSWORD = 'TestPass123!'

def main():
    client = Client()
    logged = client.login(username=USERNAME, password=PASSWORD)
    print('LOGIN_SUCCESS', logged)

    r = client.get('/reports/', HTTP_HOST='127.0.0.1')
    print('REPORTS', r.status_code, len(r.content))
    open('report_dashboard_as_admin.html', 'wb').write(r.content)

    r2 = client.get('/reports/booking/', HTTP_HOST='127.0.0.1')
    print('BOOKING', r2.status_code, len(r2.content))
    open('report_booking_as_admin.html', 'wb').write(r2.content)

if __name__ == '__main__':
    main()
