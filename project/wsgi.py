"""
WSGI config for Swapit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

path = '/var/www/html/myproject/'
if path not in sys.path:
    sys.path.append(path)

path = '/var/www/html/myproject/myproject/'
if path not in sys.path:
    sys.path.append(path)

path = '/var/www/html/myproject/myproject/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
application = get_wsgi_application()
