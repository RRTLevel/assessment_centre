from django.apps import AppConfig

class AppSrcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_src"

    def ready(self):
        import app_src.signals