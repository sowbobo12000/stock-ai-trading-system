from fastapi import APIRouter, Request
from producer.kafka_producer import publish_to_topic
from producer.news_formatter import format_news_payload

router = APIRouter()

@router.post("/")
async def receive_news_webhook(request: Request):
    payload = await request.json()
    try:
        news = format_news_payload(payload)
        if news:
            publish_to_topic("news_topic", news)
        return {"status": "accepted"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
