# urls.py (예: crawling_system/urls.py)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NewsImpactViewSet,
    SignalScoreViewSet,
    GammaExposureViewSet,
    AlertViewSet,
    LLMFeedbackViewSet,
)

router = DefaultRouter()
router.register(r'news-impact', NewsImpactViewSet, basename='news-impact')
router.register(r'signal-score', SignalScoreViewSet, basename='signal-score')
router.register(r'gamma-exposure', GammaExposureViewSet, basename='gamma-exposure')
router.register(r'llm-feedback', LLMFeedbackViewSet, basename='llm-feedback')
router.register(r'alerts', AlertViewSet, basename='alerts')

urlpatterns = [
    path('', include(router.urls)),
]
