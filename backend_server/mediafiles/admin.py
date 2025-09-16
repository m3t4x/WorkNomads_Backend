from typing import List
from django.contrib import admin
from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ("id", "owner_id", "file_type", "original_filename", "size", "created_at")
    list_filter = ("file_type", "created_at")
    search_fields = ("owner_id", "original_filename")
    ordering = ("-created_at",)
