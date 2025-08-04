from django.db import models
from core.models import BaseModel

class GammaExposure(BaseModel):
    symbol = models.CharField(max_length=10)
    expiry_date = models.DateField()
    gex_value = models.FloatField(help_text="Gamma Exposure")
    delta_exposure = models.FloatField()
    dealer_position = models.CharField(
        max_length=10,
        choices=DealerPosition.choices,
        help_text="Dealer hedging position"
    )

    class Meta:
        indexes = [models.Index(fields=["symbol", "expiry_date"])]

    def __str__(self):
        return f"{self.symbol} GEX @ {self.expiry_date}"


class SignalScore(BaseModel):
    symbol = models.CharField(max_length=10)
    time_frame = models.CharField(max_length=10, choices=[
        ("1h", "1시간"), ("4h", "4시간"), ("1d", "1일")
    ])
    signal_type = models.CharField(max_length=10, choices=[
        ("BUY", "매수"), ("SELL", "매도"), ("HOLD", "관망")
    ])
    score = models.FloatField(help_text="0 ~ 100 점수")
    description = models.TextField()

    class Meta:
        indexes = [models.Index(fields=["symbol", "time_frame"])]

    def __str__(self):
        return f"[{self.symbol}] {self.signal_type} ({self.score}) [{self.time_frame}]"
