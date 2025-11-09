from django.contrib import admin
from .models import OptionData, OHLCData, NewsData

@admin.register(OptionData)
class OptionDataAdmin(admin.ModelAdmin):
    list_display = ("symbol", "expiry_date", "strike_price", "call_put", "volume", "timestamp")
    search_fields = ("symbol",)
    list_filter = ("call_put", "expiry_date")

@admin.register(OHLCData)
class OHLCDataAdmin(admin.ModelAdmin):
    list_display = ("symbol", "open", "high", "low", "close", "timestamp")
    search_fields = ("symbol",)

@admin.register(NewsData)
class NewsDataAdmin(admin.ModelAdmin):
    list_display = ("symbol", "headline", "sentiment", "impact_score", "timestamp")
    search_fields = ("symbol", "headline")
    list_filter = ("sentiment",)
