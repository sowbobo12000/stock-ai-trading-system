from rest_framework.routers import DefaultRouter
from .views import OptionDataViewSet, OHLCDataViewSet, NewsDataViewSet

router = DefaultRouter()
router.register(r'options', OptionDataViewSet)
router.register(r'ohlc', OHLCDataViewSet)
router.register(r'news', NewsDataViewSet)

urlpatterns = router.urls
