import json
from datetime import datetime
from confluent_kafka import Consumer, KafkaError
from kafka_app.config.kafka_config import get_kafka_config, TOPICS
from kafka_app.config.clickhouse_config import get_clickhouse_client

def analyze_ohlc(ohlc_data):
    try:
        client = get_clickhouse_client()
        timestamp = ohlc_data["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        client.insert(
            "ohlc_data",
            [(
                ohlc_data["id"],
                ohlc_data["symbol"],
                ohlc_data["open"],
                ohlc_data["high"],
                ohlc_data["low"],
                ohlc_data["close"],
                timestamp
            )],
            column_names=["id", "symbol", "open", "high", "low", "close", "timestamp"]
        )
        print(f"[✅ ClickHouse] Inserted OHLC for {ohlc_data['symbol']}")
    except Exception as e:
        print(f"[❌ ERROR] Failed to insert OHLC: {e}")

def main():
    consumer = Consumer({
        **get_kafka_config(),
        "group.id": "ohlc_analysis_group",
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe([TOPICS["OHLC"]])
    print("[Consumer] ✅ OHLC Consumer started...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print("[❌ Error]", msg.error())
                continue
            try:
                analyze_ohlc(json.loads(msg.value().decode("utf-8")))
            except Exception as e:
                print(f"[❌ JSON ERROR] {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
