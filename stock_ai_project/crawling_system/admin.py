from django.contrib import admin
from .models import NewsArticle, OptionData, PriceCandle

@admin.register(NewsArticle)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'title', 'published_at', 'source')

@admin.register(OptionData)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'strike_price', 'call_or_put', 'expiry_date')

@admin.register(PriceCandle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'interval', 'timestamp', 'close')
