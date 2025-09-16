from typing import Any
from django.utils import timezone
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser

from .models import MediaFile
from .serializers import MediaFileSerializer, FileUploadSerializer


class UploadBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    file_type: str = ""
    allowed_prefix: str = ""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args: Any, **kwargs: Any):
        up_file = request.FILES.get("file")
        if not up_file:
            return Response({"detail": "No file provided with key 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        content_type = getattr(up_file, "content_type", "") or ""
        if not content_type.startswith(self.allowed_prefix + "/"):
            return Response({"detail": f"Invalid content type. Expected {self.allowed_prefix}/*"}, status=status.HTTP_400_BAD_REQUEST)

        instance = MediaFile.objects.create(
            owner_id=str(getattr(request.user, "id", "anonymous")),
            file=up_file,
            file_type=self.file_type,
            original_filename=getattr(up_file, "name", "uploaded"),
            content_type=content_type,
            size=getattr(up_file, "size", 0),
        )

        data = MediaFileSerializer(instance, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)

class UploadImageView(UploadBaseView):
    file_type = MediaFile.TYPE_IMAGE
    allowed_prefix = "image"
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload image file",
        tags=["media"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"}
                },
                "required": ["file"],
            }
        },
        responses={201: MediaFileSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UploadAudioView(UploadBaseView):
    file_type = MediaFile.TYPE_AUDIO
    allowed_prefix = "audio"
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload audio file",
        tags=["media"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"}
                },
                "required": ["file"],
            }
        },
        responses={201: MediaFileSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ListFilesView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaFileSerializer
    pagination_class = None

    @extend_schema(
        summary="List files for current user",
        responses={200: MediaFileSerializer(many=True)},
        tags=["media"],
    )
    def get_queryset(self):
        owner_id = str(getattr(self.request.user, "id", ""))
        return MediaFile.objects.filter(owner_id=owner_id)


class DeleteFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Delete a file by id (must own the file)",
        parameters=[
            {
                "name": "pk",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
                "description": "ID of the media file",
            }
        ],
        responses={204: OpenApiResponse(description="Deleted"), 404: OpenApiResponse(description="Not found")},
        tags=["media"],
    )
    def delete(self, request, pk: int, *args: Any, **kwargs: Any):
        owner_id = str(getattr(request.user, "id", ""))
        obj = get_object_or_404(MediaFile, pk=pk, owner_id=owner_id)
        # Remove the file from storage first; don't save the model afterwards
        try:
            stored = obj.file
            if stored and getattr(stored, "name", None):
                stored.delete(save=False)
        except Exception:
            # If storage delete fails, still remove the DB row to avoid dangling records
            pass
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
