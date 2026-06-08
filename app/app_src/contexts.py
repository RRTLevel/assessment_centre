from django.conf import settings

def applicationNameContext(request):
    application_name = settings.APPLICATION_NAME
    return{"application_name":application_name}

def applicationVersionContext(request):
    application_version = settings.APPLICATION_VERSION
    return{"application_version":application_version}

def applicationEnvironmentContext(request):
    application_environment = settings.APPLICATION_ENVIRONMENT
    return{"application_environment":application_environment}