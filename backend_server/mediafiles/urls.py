from django.urls import path
from .views import UploadImageView, UploadAudioView, ListFilesView, DeleteFileView

urlpatterns = [
    path("upload/image/", UploadImageView.as_view(), name="upload-image"),
    path("upload/audio/", UploadAudioView.as_view(), name="upload-audio"),
    path("list/", ListFilesView.as_view(), name="list-files"),
    path("delete/<int:pk>/", DeleteFileView.as_view(), name="delete-file"),
]
