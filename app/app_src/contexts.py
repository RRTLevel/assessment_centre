"""Template context processors registered in settings.TEMPLATES."""

from django.conf import settings

from .permissions import nav_permissions


def application_metadata(request):
    """Expose the application name, version and environment to every template."""
    return {
        "application_name": settings.APPLICATION_NAME,
        "application_version": settings.APPLICATION_VERSION,
        "application_environment": settings.APPLICATION_ENVIRONMENT,
    }


def navigation_permissions(request):
    return nav_permissions(request.user)
