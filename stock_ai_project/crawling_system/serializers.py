from rest_framework import serializers
from .models import NewsArticle, OptionData, PriceCandle, NewsImpact
from core.serializers import BaseSerializerMixin
from core.choices import SentimentChoices, DealerPosition, SignalTypeChoices


# ✅ NewsArticle
class NewsArticleSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_symbol(self, value):
        return value.upper()

    def validate(self, data):
        if not data.get('title'):
            raise serializers.ValidationError("뉴스 제목은 필수입니다.")
        return data


# ✅ OptionData
class OptionDataSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = OptionData
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_call_or_put(self, value):
        value = value.upper()
        if value not in ['CALL', 'PUT']:
            raise serializers.ValidationError("Value must be 'CALL' or 'PUT'")
        return value


# ✅ PriceCandle
class PriceCandleSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PriceCandle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_interval(self, value):
        allowed = ['1m', '5m', '15m', '1h', '1d']
        if value not in allowed:
            raise serializers.ValidationError(f"Interval must be one of {allowed}")
        return value

    def validate(self, data):
        if data['low'] > data['high']:
            raise serializers.ValidationError("Low price cannot be higher than high price.")
        return data


# ✅ NewsImpact
class NewsImpactSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    sentiment = serializers.ChoiceField(choices=SentimentChoices.choices)
    related_symbols = serializers.ListField(
        child=serializers.CharField(max_length=10), help_text="List of related tickers"
    )
    score = serializers.FloatField(min_value=0.0, max_value=1.0)

    class Meta:
        model = NewsImpact
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
