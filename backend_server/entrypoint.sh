#!/usr/bin/env sh
set -e

# Export env if present (safe, without relying on xargs flags)
set -a
[ -f "/app/.env" ] && . /app/.env || true
set +a

python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# Optionally create/update a superuser so admin isn't empty
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
python manage.py shell <<'PY'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL','')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
u, created = User.objects.get_or_create(username=username, defaults={
    'email': email,
    'is_staff': True,
    'is_superuser': True,
})
if not created:
    u.is_staff = True
    u.is_superuser = True
u.email = email
u.set_password(password)
u.save()
print('Superuser ready:', u.username)
PY
fi

python manage.py runserver 0.0.0.0:8000
