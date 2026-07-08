from rest_framework import routers

from .views import NoteViewSet

api_router = routers.DefaultRouter()
api_router.register(r"notes", NoteViewSet, basename="notes")
