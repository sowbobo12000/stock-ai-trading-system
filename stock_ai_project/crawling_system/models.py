# crawling_system/models.py

from django.db import models
from core.models import BaseModel
from core.choices import CrawlStatus, AnalysisStatus

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
    call_or_put = models.CharField(max_length=4)
    expiry_date = models.DateField()
    implied_volatility = models.FloatField()
    provider = mentorQ & alpha vintage


    def __str__(self):
        return f"{self.symbol} {self.call_or_put} {self.strike_price}"


class PriceCandle(BaseModel):
    symbol = models.CharField(max_length=10)
    interval = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'interval', 'timestamp')

    def __str__(self):
        return f"{self.symbol} @ {self.timestamp} [{self.interval}]"



