from fastapi import APIRouter, Request
from producer.kafka_producer import publish_to_topic
from producer.option_formatter import format_option_payload

router = APIRouter()

@router.post("/")
async def receive_option_webhook(request: Request):
    payload = await request.json()
    try:
        option = format_option_payload(payload)
        if option:
            publish_to_topic("option_topic", option)
        return {"status": "accepted"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
