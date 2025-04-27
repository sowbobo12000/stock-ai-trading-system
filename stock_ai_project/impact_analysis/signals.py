from django.db.models.signals import post_save
from django.dispatch import receiver
from crawling_system.models import NewsArticle
from .tasks import analyze_news_impact

@receiver(post_save, sender=NewsArticle)
def trigger_news_analysis(sender, instance, created, **kwargs):
    if created:
        analyze_news_impact.delay(instance.id)
