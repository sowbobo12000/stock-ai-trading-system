from celery import shared_task
from crawling_system.models import NewsArticle
from .models import NewsImpact
from core.choices import AnalysisStatus

@shared_task
def analyze_news_impact(news_id):
    news = NewsArticle.objects.get(id=news_id)

    # Dummy LLM result (replace with actual OpenAI / LangGraph call)
    sentiment = "positive"
    score = 0.92
    summary = f"LLM summary for article: {news.title}"
    related_symbols = [news.symbol]

    NewsImpact.objects.update_or_create(
        news=news,
        defaults={
            "sentiment": sentiment,
            "score": score,
            "summary": summary,
            "related_symbols": related_symbols,
            "status": AnalysisStatus.ANALYZED
        }
    )
