from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clickhouse/', include('src.clickhouse_data.urls')),
]
