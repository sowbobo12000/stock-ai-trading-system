from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clickhouse/', include('apps.clickhouse_data.urls')),
]
