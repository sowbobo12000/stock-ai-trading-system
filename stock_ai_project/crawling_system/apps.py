from django.apps import AppConfig

class CrawlingSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crawling_system'

    def ready(self):
        import crawling_system.signals
