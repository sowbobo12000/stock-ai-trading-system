from confluent_kafka import Consumer, Producer
import json

TOPIC_IN = "ohlc_topic"
TOPIC_OUT = "aggregated_insights"

def aggregate_ohlc(ohlc_data):
    # Example: Moving average, volatility computation
    return {
        "symbol": ohlc_data["symbol"],
        "avg_price": (ohlc_data["high"] + ohlc_data["low"]) / 2
    }

def main():
    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "ohlc_aggregator",
        "auto.offset.reset": "earliest"
    })

    producer = Producer({"bootstrap.servers": "localhost:9092"})

    consumer.subscribe([TOPIC_IN])
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue

        data = json.loads(msg.value().decode("utf-8"))
        aggregated_data = aggregate_ohlc(data)

        producer.produce(
            TOPIC_OUT,
            key=data["symbol"],
            value=json.dumps(aggregated_data).encode("utf-8")
        )
        producer.flush()

if __name__ == "__main__":
    main()
