from django.contrib.auth.models import User
from rest_framework import serializers
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class LoginByUsernameOrEmailSerializer(TokenObtainPairSerializer):
    """Allow login using either username or email.

    This accepts the standard SimpleJWT payload:
    - {"username": "<username or email>", "password": "..."}

    For convenience, it also accepts {"email": "...", "password": "..."}.
    We normalize inputs to the actual username before calling the parent.
    """

    def validate(self, attrs):
        identifier = attrs.get("username") or attrs.get("email") or ""
        if identifier:
            # If it looks like an email, try to resolve it to a username.
            if "@" in identifier:
                user = (
                    User.objects.filter(Q(email__iexact=identifier)).order_by("id").first()
                )
                if user:
                    attrs["username"] = getattr(user, User.USERNAME_FIELD, user.username)
            # else: assume it's already a username

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Include a few handy claims for the backend to consume (optional)
        token["username"] = user.get_username()
        if getattr(user, "email", ""):
            token["email"] = user.email
        if getattr(user, "first_name", ""):
            token["first_name"] = user.first_name
        if getattr(user, "last_name", ""):
            token["last_name"] = user.last_name
        return token
