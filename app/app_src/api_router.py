from rest_framework import routers
from .api_views import noteViewSet

api_router = routers.DefaultRouter()

api_router.register(r"notes", noteViewSet, basename="notes")

