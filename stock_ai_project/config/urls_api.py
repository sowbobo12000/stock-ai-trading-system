from django.urls import path, include

urlpatterns = [
    path('crawl/', include('crawling_system.urls')),     # /api/crawl/
    # path('agent/', include('main_stock_agent.urls')),  # /api/agent/
    # path('analyze/', include('analyze_system.urls')),  # /api/analyze/
]