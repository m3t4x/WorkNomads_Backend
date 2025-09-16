from rest_framework import serializers
from .models import MediaFile


class FileUploadSerializer(serializers.Serializer):
    """Used only to show the multipart file field in the API docs."""
    file = serializers.FileField(use_url=False)


class MediaFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = [
            "id",
            "file_type",
            "original_filename",
            "content_type",
            "size",
            "created_at",
            "url",
        ]

    def get_url(self, obj: MediaFile) -> str:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url
