from fastapi import APIRouter, Request
from producer.kafka_producer import publish_to_topic
from producer.ohlc_formatter import format_ohlc_payload

router = APIRouter()

@router.post("/")
async def receive_ohlc_webhook(request: Request):
    payload = await request.json()
    try:
        ohlc = format_ohlc_payload(payload)
        if ohlc:
            publish_to_topic("ohlc_topic", ohlc)
        return {"status": "accepted"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
