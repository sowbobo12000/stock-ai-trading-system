from rest_framework import serializers
from .models import NewsArticle, OptionData, PriceCandle
from core.serializers import BaseSerializerMixin

class NewsArticleSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    symbol = serializers.CharField(help_text="Stock symbol (e.g., TSLA)")
    title = serializers.CharField(help_text="Headline of the news")
    content = serializers.CharField(help_text="Full text of the news article")
    source = serializers.CharField(help_text="News source name")
    published_at = serializers.DateTimeField(help_text="Original publication datetime")

    class Meta:
        model = NewsArticle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_symbol(self, value):
        return value.upper()  # 종목 대문자 변환

    def validate(self, data):
        if not data['title']:
            raise serializers.ValidationError("뉴스 제목은 필수입니다.")
        return data


class OptionDataSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    symbol = serializers.CharField(help_text="Stock symbol (e.g., TSLA)")
    strike_price = serializers.FloatField(help_text="Strike price of the option")
    call_or_put = serializers.CharField(
        help_text="Option type: CALL or PUT"
    )
    expiry_date = serializers.DateField(help_text="Expiration date of the option")
    implied_volatility = serializers.FloatField(help_text="Implied volatility (0.0 to 1.0)")

    class Meta:
        model = OptionData
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_call_or_put(self, value):
        value = value.upper()
        if value not in ['CALL', 'PUT']:
            raise serializers.ValidationError("Value must be 'CALL' or 'PUT'")
        return value


class PriceCandleSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    symbol = serializers.CharField(help_text="Stock symbol (e.g., AAPL)")
    interval = serializers.CharField(help_text="Candle interval (e.g., 1m, 5m, 1h, 1d)")
    timestamp = serializers.DateTimeField(help_text="Time of this candle")
    open = serializers.FloatField(help_text="Opening price")
    high = serializers.FloatField(help_text="Highest price during interval")
    low = serializers.FloatField(help_text="Lowest price during interval")
    close = serializers.FloatField(help_text="Closing price")
    volume = serializers.IntegerField(help_text="Trading volume")

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


#Todo
'''
related_symbols 같은 JSON 필드는 ListField로 validate 가능

score, volatility → 0~1 실수 범위 제한

interval, call_or_put, symbol 등은 enum validator 도입 가능
'''
