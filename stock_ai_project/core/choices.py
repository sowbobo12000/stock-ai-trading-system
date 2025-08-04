from django.db import models

from django.db.models import TextChoices

class CrawlStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class AnalysisStatus(models.TextChoices):
    NOT_ANALYZED = 'NOT_ANALYZED', 'Not analyzed'
    ANALYZING = 'ANALYZING', 'Analyzing'
    ANALYZED = 'ANALYZED', 'Analyzed'


class CrawlStatus(TextChoices):
    PENDING = "PENDING", "수집 대기"
    SUCCESS = "SUCCESS", "수집 완료"
    FAILED = "FAILED", "수집 실패"


class AnalysisStatus(TextChoices):
    NOT_ANALYZED = "NOT_ANALYZED", "분석 전"
    IN_PROGRESS = "IN_PROGRESS", "분석 중"
    COMPLETED = "COMPLETED", "분석 완료"
    FAILED = "FAILED", "분석 실패"


class SentimentType(TextChoices):
    POSITIVE = "POSITIVE", "긍정"
    NEGATIVE = "NEGATIVE", "부정"
    NEUTRAL = "NEUTRAL", "중립"


class DataProvider(TextChoices):
    YFINANCE = "YFINANCE", "Yahoo Finance"
    SEEKING_ALPHA = "SEEKING_ALPHA", "Seeking Alpha"
    TRADIER = "TRADIER", "Tradier"
    ALPHA_VANTAGE = "ALPHA_VANTAGE", "Alpha Vantage"


class DealerPosition(TextChoices):
    LONG = "LONG", "딜러 매수 포지션"
    SHORT = "SHORT", "딜러 매도 포지션"


class SentimentChoices(TextChoices):
    POSITIVE = 'POSITIVE', 'Positive'
    NEGATIVE = 'NEGATIVE', 'Negative'
    NEUTRAL = 'NEUTRAL', 'Neutral'

class DealerPosition(TextChoices):
    LONG = 'LONG', 'Long'
    SHORT = 'SHORT', 'Short'

class SignalTypeChoices(TextChoices):
    BUY = 'BUY', 'Buy'
    SELL = 'SELL', 'Sell'
    HOLD = 'HOLD', 'Hold'
