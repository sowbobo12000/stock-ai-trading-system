from confluent_kafka import Consumer, KafkaError
import json
import clickhouse_connect
from consumer.utils import get_kafka_config
from datetime import datetime, date

TOPIC = "option_topic"

def analyze_option(option_data):
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='default',
            password=''
        )

        # ⬇️ expiry_date 문자열을 date로 변환
        expiry_date = option_data['expiry_date']
        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

        # ⬇️ timestamp 문자열을 datetime으로 변환
        timestamp = option_data['timestamp']
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        client.insert(
            'option_data',
            [(
                option_data['id'],
                option_data['symbol'],
                expiry_date,
                option_data['strike_price'],
                option_data['call_put'],
                option_data['implied_volatility'],
                option_data['volume'],
                timestamp
            )],
            column_names=[
                'id', 'symbol', 'expiry_date', 'strike_price', 'call_put',
                'implied_volatility', 'volume', 'timestamp'
            ]
        )

        print(f"[✅ ClickHouse] Inserted data for {option_data['symbol']}")
    except Exception as e:
        print(f"[❌ ERROR] Failed to insert to ClickHouse: {e}")
        
def main():
    consumer = Consumer({
        **get_kafka_config(),
        "group.id": "option_analysis_group",
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe([TOPIC])
    print("[Consumer] ✅ Subscribed and waiting for messages...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print("[❌ Consumer Error]", msg.error())
                continue

            try:
                option_data = json.loads(msg.value().decode("utf-8"))
                analyze_option(option_data)
            except Exception as e:
                print(f"[❌ JSON ERROR] {e}")

    except KeyboardInterrupt:
        print("👋 Consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
