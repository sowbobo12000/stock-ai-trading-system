from django.db import models
from core.models import BaseModel
from core.choices import AnalysisStatus
from crawling_system.models import NewsArticle


class NewsImpact(BaseModel):
    news = models.OneToOneField(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name='impact'
    )

    sentiment = models.CharField(
        max_length=10,
        choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')],
        help_text="Overall LLM sentiment classification"
    )

    score = models.FloatField(
        help_text="Sentiment confidence score (0.0 ~ 1.0)",
        default=0.0
    )

    summary = models.TextField(
        help_text="LLM-generated abstract or summary of the article"
    )

    related_symbols = models.JSONField(
        default=list,
        help_text="Other tickers mentioned in the article (besides primary)"
    )

    status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.ANALYZING
    )

    impact_type = models.CharField(
        max_length=20,
        choices=[
            ('earnings', 'Earnings'),
            ('macro', 'Macro'),
            ('regulation', 'Regulation'),
            ('product', 'Product'),
            ('merger', 'M&A'),
            ('technical', 'Technical'),
            ('other', 'Other')
        ],
        default='other',
        help_text="What kind of event this article is classified as"
    )

    ai_model_version = models.CharField(
        max_length=30,
        default='gpt-4-turbo',
        help_text="Which LLM model was used for this analysis"
    )

    analysis_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the LLM finished analysis"
    )

    risk_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional riskiness score (0~1) based on keywords or LLM judgment"
    )

    class Meta:
        indexes = [
            models.Index(fields=['sentiment']),
            models.Index(fields=['status']),
            models.Index(fields=['impact_type']),
            models.Index(fields=['analysis_time']),
        ]

    def __str__(self):
        return f"[{self.news.symbol}] {self.sentiment.upper()} ({self.score:.2f})"


# impact_analysis/models.py
class LLMFeedback(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    news = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20, choices=[('positive', 'Positive'), ('negative', 'Negative')])
    comment = models.TextField(blank=True)

