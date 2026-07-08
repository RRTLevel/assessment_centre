from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from app_src.api.router import api_router

urlpatterns = [
    path("", include("app_src.urls")),
    path("admin/", admin.site.urls),
    path("api/", include(api_router.urls)),
]

admin.site.site_header = f"{settings.APPLICATION_NAME} | Admin"
