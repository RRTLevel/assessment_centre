from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

from app_src.api_router import api_router

urlpatterns = [
    re_path(r'login/$', auth_views.LoginView.as_view(), {'next_page': '/index'}, name='login'),
    re_path(r'logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

    path('', include('app_src.urls')),
    path('admin/', admin.site.urls),
    path('api/', include(api_router.urls))
]

admin.site.site_header = str(settings.APPLICATION_NAME + " | Admin")