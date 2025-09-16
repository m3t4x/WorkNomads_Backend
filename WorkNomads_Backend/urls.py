"""URLConf for the `WorkNomads_Backend` site."""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
