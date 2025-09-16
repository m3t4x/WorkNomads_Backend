from django.db import models
from django.utils import timezone


def upload_to(instance: "MediaFile", filename: str) -> str:
    # Keep uploads under a type-based folder; keep the original filename.
    subdir = "images" if instance.file_type == MediaFile.TYPE_IMAGE else "audio"
    return f"{subdir}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


class MediaFile(models.Model):
    TYPE_IMAGE = "image"
    TYPE_AUDIO = "audio"
    TYPE_CHOICES = [
        (TYPE_IMAGE, "Image"),
        (TYPE_AUDIO, "Audio"),
    ]

    # ID from the Auth Server JWT; stored as a string to avoid tight coupling.
    owner_id = models.CharField(max_length=64, db_index=True)

    file = models.FileField(upload_to=upload_to)
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.file_type}:{self.original_filename} ({self.owner_id})"
