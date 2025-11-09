from clickhouse_backend import models
from django.utils import timezone

# -----------------------------
# Option 데이터
# -----------------------------
class OptionData(models.ClickhouseModel):
    id = models.StringField(primary_key=True)
    symbol = models.StringField(low_cardinality=True)
    expiry_date = models.DateField()
    strike_price = models.Float64Field()
    call_put = models.StringField(low_cardinality=True)
    implied_volatility = models.Float64Field()
    volume = models.Int32Field()
    timestamp = models.DateTime64Field(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        engine = models.MergeTree(
            order_by=("symbol", "expiry_date", "timestamp"),
            partition_by=models.toYYYYMM("expiry_date"),
            primary_key=("symbol", "expiry_date"),
            index_granularity=8192
        )

# -----------------------------
# OHLC 데이터
# -----------------------------
class OHLCData(models.ClickhouseModel):
    id = models.StringField(primary_key=True)
    symbol = models.StringField(low_cardinality=True)
    open = models.Float64Field()
    high = models.Float64Field()
    low = models.Float64Field()
    close = models.Float64Field()
    timestamp = models.DateTime64Field(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        engine = models.MergeTree(
            order_by=("symbol", "timestamp"),
            partition_by=models.toYYYYMM("timestamp"),
            primary_key=("symbol", "timestamp"),
            index_granularity=8192
        )

# -----------------------------
# 뉴스 데이터
# -----------------------------
class NewsData(models.ClickhouseModel):
    id = models.StringField(primary_key=True)
    symbol = models.StringField(low_cardinality=True)
    headline = models.StringField()
    sentiment = models.StringField(low_cardinality=True)
    impact_score = models.Float64Field(default=0.0)
    timestamp = models.DateTime64Field(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        engine = models.MergeTree(
            order_by=("symbol", "timestamp"),
            partition_by=models.toYYYYMM("timestamp"),
            primary_key=("symbol", "timestamp"),
            index_granularity=8192
        )
