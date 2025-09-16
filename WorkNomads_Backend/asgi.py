"""ASGI entrypoint for `WorkNomads_Backend`.

Exports `application` for ASGI servers.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkNomads_Backend.settings')

application = get_asgi_application()
