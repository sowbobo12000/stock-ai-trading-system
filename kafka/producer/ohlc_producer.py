import os
import json
import uuid
import time
from datetime import datetime
from confluent_kafka import Producer
from kafka_app.config.kafka_config import get_kafka_config, TOPICS


def fetch_ohlc_data(symbol, use_mock_data=False):
    if use_mock_data:
        return [{
            "symbol": symbol,
            "open": 420.5,
            "high": 430.2,
            "low": 419.1,
            "close": 428.7
        }]

    # 실제 OHLC API 연동 시 구현
    return []


def produce_ohlc_data(ohlc, producer):
    data = {
        "id": str(uuid.uuid4()),
        "symbol": ohlc["symbol"],
        "open": ohlc["open"],
        "high": ohlc["high"],
        "low": ohlc["low"],
        "close": ohlc["close"],
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    producer.produce(
        TOPICS["OHLC"],
        key=ohlc["symbol"],
        value=json.dumps(data).encode("utf-8"),
        on_delivery=lambda err, msg: print("Delivery Report:",
                                           err or f"✅ Delivered to {msg.topic()} [{msg.partition()}]")
    )


def main():
    producer = Producer(get_kafka_config())
    symbol = "AAPL"
    use_mock_data = True

    while True:
        ohlc_list = fetch_ohlc_data(symbol, use_mock_data)
        for ohlc in ohlc_list:
            produce_ohlc_data(ohlc, producer)
        producer.flush()
        time.sleep(15)


if __name__ == "__main__":
    main()
