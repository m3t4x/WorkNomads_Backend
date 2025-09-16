from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from .serializers import RegisterSerializer, LoginByUsernameOrEmailSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class RegisterView(APIView):
    """Registers a user and returns a short success message.

    Grab tokens afterwards via `/api/auth/login/`.
    """

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Register a new user",
        request=RegisterSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "Registration successful"}},
            },
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Registration successful"}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Login (obtain access & refresh tokens)",
    tags=["auth"],
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginByUsernameOrEmailSerializer


@extend_schema(
    summary="Refresh access token",
    tags=["auth"],
)
class LoginRefreshView(TokenRefreshView):
    pass
