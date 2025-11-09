# kafka_app/config/kafka_config.py
import os

TOPICS = {
    "OPTION": "option_topic",
    "NEWS": "news_topic",
    "OHLC": "ohlc_topic"
}

def get_kafka_config():
    return {
        "bootstrap.servers": os.getenv("KAFKA_BROKER", "127.0.0.1:29092")
    }
