from django.apps import AppConfig


class ImpactAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'impact_analysis'

    # apps.py 안에서 자동 로드 설정
    class ImpactAnalysisConfig(AppConfig):
        name = 'impact_analysis'

        def ready(self):
            import impact_analysis.signals

