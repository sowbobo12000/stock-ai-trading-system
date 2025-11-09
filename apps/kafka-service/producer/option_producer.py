import os
import json
import uuid
import time
import requests
from datetime import datetime
from confluent_kafka import Producer

TOPIC = "option_topic"
API_KEY = os.environ.get("POLYGON_API_KEY", "dummy")

def get_kafka_config():
    return {"bootstrap.servers": "127.0.0.1:29092"} 

def fetch_option_data(symbol, use_mock_data=False):
    if use_mock_data:
        return [{
            "symbol": symbol,
            "strike": 180,
            "expiry": "2025-08-01",
            "call_put": "CALL",
            "implied_volatility": 0.25,
            "volume": 150
        }]
    
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("[ERROR] Polygon API error:", response.text)
        return []

    data = response.json()
    return data.get("results", [])

def produce_option_data(option, producer):
    data = {
        "id": str(uuid.uuid4()),
        "symbol": option["symbol"],
        "expiry_date": option["expiry"],  # YYYY-MM-DD
        "strike_price": option["strike"],
        "call_put": option["call_put"],
        "implied_volatility": option["implied_volatility"],
        "volume": option["volume"],
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    producer.produce(
        TOPIC,
        key=option["symbol"],
        value=json.dumps(data).encode("utf-8"),
        on_delivery=lambda err, msg: print("Delivery Report:", err or f"✅ Delivered to {msg.topic()} [{msg.partition()}]")
    )

def main():
    producer = Producer(get_kafka_config())
    symbol = "AAPL"
    use_mock_data = True

    while True:
        option_list = fetch_option_data(symbol, use_mock_data)
        for option in option_list:
            produce_option_data(option, producer)
        producer.flush()
        time.sleep(10)

if __name__ == "__main__":
    main()
