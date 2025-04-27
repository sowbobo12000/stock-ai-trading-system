
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsArticle

@receiver(post_save, sender=NewsArticle)
def handle_news_created(sender, instance, created, **kwargs):
    if created:
        print(f"📰 새 뉴스 저장됨: {instance.title} ({instance.symbol})")
