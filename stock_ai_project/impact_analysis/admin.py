from django.contrib import admin
from .models import NewsImpact

@admin.register(NewsImpact)
class NewsImpactAdmin(admin.ModelAdmin):
    list_display = ('news', 'sentiment', 'score', 'status', 'created_at')
    search_fields = ('news__symbol', 'sentiment')
