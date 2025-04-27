from celery import shared_task
from .models import NewsArticle
from .crawling.yfinance_crawler import YahooFinanceCrawler
from core.choices import CrawlStatus

@shared_task
def crawl_all_news_for_symbol(symbol: str):
    crawlers = [
        YahooFinanceCrawler(symbol),
        # Add more: SeekingAlphaCrawler(symbol), etc.
    ]

    for crawler in crawlers:
        articles = crawler.fetch_articles()
        for article in articles:
            # Duplicate prevention
            exists = NewsArticle.objects.filter(
                title=article['title'],
                source=article['source'],
                symbol=article['symbol'],
            ).exists()
            if not exists:
                NewsArticle.objects.create(
                    **article,
                    crawl_status=CrawlStatus.SUCCESS
                )
