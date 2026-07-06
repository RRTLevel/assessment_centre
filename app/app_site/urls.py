from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from app_src.api_router import api_router
from app_src.views import RememberMeLoginView


urlpatterns = [
    re_path(r"login/$", RememberMeLoginView.as_view(), name="login"),
    re_path(r"logout/$", auth_views.LogoutView.as_view(), {"next_page": "/"}, name="logout"),
    path("", include("app_src.urls")),
    path("admin/", admin.site.urls),
    path("api/", include(api_router.urls)),
]

admin.site.site_header = str(settings.APPLICATION_NAME + " | Admin")
