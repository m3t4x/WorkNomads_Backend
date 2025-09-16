"""WSGI entrypoint for `WorkNomads_Backend`.

Exports `application` for WSGI servers.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkNomads_Backend.settings')

application = get_wsgi_application()
