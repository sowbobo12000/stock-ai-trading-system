from rest_framework.routers import DefaultRouter
from .views import NewsArticleViewSet, OptionDataViewSet, PriceCandleViewSet

router = DefaultRouter()
router.register(r'news', NewsArticleViewSet)
router.register(r'options', OptionDataViewSet)
router.register(r'candles', PriceCandleViewSet)

urlpatterns = router.urls