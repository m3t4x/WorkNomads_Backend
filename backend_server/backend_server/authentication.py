import os
from typing import Optional, Tuple

import jwt
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class AuthUser:
    """Tiny user object we build from JWT claims (no DB lookup here)."""

    def __init__(self, user_id: str | int, username: str = "", email: str = "", first_name: str = "", last_name: str = ""):
        self.id = user_id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @property
    def is_authenticated(self) -> bool:  # DRF checks this
        return True


class ExternalJWTAuthentication(authentication.BaseAuthentication):
    """Accepts a Bearer token from the auth service and checks its signature.

    We skip Django's user model entirely and just return a minimal user-like
    object with a couple of fields from the token.
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[AuthUser, dict]]:
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None
        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Bad Authorization header. Expected: 'Bearer <token>'.")

        token = parts[1]
        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT_SIGNING_KEY,
                algorithms=[getattr(settings, "SIMPLE_JWT_ALGORITHM", "HS256")],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token.")

        user_id = payload.get("user_id") or payload.get("sub")
        username = payload.get("username") or payload.get("user_name") or ""
        email = payload.get("email") or ""
        first_name = payload.get("first_name") or ""
        last_name = payload.get("last_name") or ""
        if not user_id:
            raise exceptions.AuthenticationFailed("Token missing required subject/user_id.")

        user = AuthUser(user_id=user_id, username=username, email=email, first_name=first_name, last_name=last_name)
        return user, payload


class ExternalJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Tells drf-spectacular how to render the Bearer auth in Swagger UI."""

    target_class = "backend_server.authentication.ExternalJWTAuthentication"
    name = "ExternalJWTAuthentication"
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
