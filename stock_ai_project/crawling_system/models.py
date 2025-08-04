from django.db import models
from core.models import BaseModel
from core.choices import CrawlStatus, AnalysisStatus, SentimentType, DataProvider, DealerPosition


class NewsArticle(BaseModel):
    symbol = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField()

    crawl_status = models.CharField(
        max_length=20,
        choices=CrawlStatus.choices,
        default=CrawlStatus.PENDING
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.NOT_ANALYZED
    )

    class Meta:
        indexes = [models.Index(fields=['symbol', 'published_at'])]

    def __str__(self):
        return f"[{self.symbol}] {self.title[:50]}"


class OptionData(BaseModel):
    symbol = models.CharField(max_length=10)
    strike_price = models.FloatField()
    call_or_put = models.CharField(max_length=4, choices=[("CALL", "Call"), ("PUT", "Put")])
    expiry_date = models.DateField()
    implied_volatility = models.FloatField()
    provider = models.CharField(
        max_length=50,
        choices=DataProvider.choices,
        default=DataProvider.YFINANCE
    )

    def __str__(self):
        return f"{self.symbol} {self.call_or_put} {self.strike_price} ({self.provider})"


class PriceCandle(BaseModel):
    symbol = models.CharField(max_length=10)
    interval = models.CharField(max_length=10, choices=[
        ("1m", "1분"), ("5m", "5분"), ("15m", "15분"),
        ("1h", "1시간"), ("1d", "1일")
    ])
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'interval', 'timestamp')
        indexes = [models.Index(fields=["symbol", "interval", "timestamp"])]

    def __str__(self):
        return f"{self.symbol} @ {self.timestamp} [{self.interval}]"


# ──────────────── 분석 결과 모델들 ────────────────

class NewsImpact(BaseModel):
    news = models.OneToOneField(NewsArticle, on_delete=models.CASCADE, related_name='impact')
    sentiment = models.CharField(max_length=20, choices=SentimentType.choices)
    score = models.FloatField(help_text="0.0 to 1.0, confidence level")
    summary = models.TextField()
    related_symbols = models.JSONField(default=list)

    def __str__(self):
        return f"{self.news.symbol} Impact - {self.sentiment} ({self.score:.2f})"


