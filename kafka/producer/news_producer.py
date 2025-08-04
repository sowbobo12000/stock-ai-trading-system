import os
import json
import uuid
import time
import requests
from datetime import datetime, timedelta
from confluent_kafka import Producer

# Kafka topic pattern: news_topic_by_ticker (following architecture diagram)
TOPIC_PREFIX = "news_topic"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "dummy")  # NewsAPI.org key
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "dummy")  # Finnhub.io key

def get_kafka_config():
    return {"bootstrap.servers": "127.0.0.1:29092"} 

def fetch_news_data(symbol, use_mock_data=False):
    """
    Fetch related news for a specific stock symbol
    Following architecture diagram: 'Fetch related News' component
    """
    if use_mock_data:
        return [{
            "symbol": symbol,
            "headline": f"Breaking: {symbol} reports strong quarterly earnings",
            "summary": f"{symbol} exceeded analyst expectations with significant revenue growth",
            "url": "https://example.com/news/1",
            "source": "Financial Times",
            "datetime": int(datetime.now().timestamp()),
            "category": "earnings",
            "related": True
        }, {
            "symbol": symbol,
            "headline": f"{symbol} announces new product launch",
            "summary": f"{symbol} unveils innovative technology solution", 
            "url": "https://example.com/news/2",
            "source": "TechCrunch",
            "datetime": int((datetime.now() - timedelta(hours=2)).timestamp()),
            "category": "product",
            "related": True
        }]
    
    # Fetch from Finnhub for company-specific news (primary source)
    try:
        # Calculate date range for recent news
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                news_items = []
                for item in data[:15]:  # Get more items for better relevance
                    # Ensure required fields exist
                    if item.get("headline") and item.get("datetime"):
                        news_items.append({
                            "symbol": symbol,
                            "headline": item.get("headline", ""),
                            "summary": item.get("summary", ""),
                            "url": item.get("url", ""),
                            "source": item.get("source", ""),
                            "datetime": item.get("datetime", 0),
                            "category": item.get("category", "general"),
                            "related": True
                        })
                
                if news_items:
                    print(f"[✅ Finnhub] Fetched {len(news_items)} news items for {symbol}")
                    return news_items
        else:
            print(f"[WARNING] Finnhub API returned status {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Finnhub API error for {symbol}: {e}")
    
    # Fallback to NewsAPI for general market news
    try:
        # Search for company name or symbol with financial keywords
        query = f"{symbol} OR \"{symbol}\" AND (stock OR shares OR earnings OR market)"
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            news_items = []
            for article in data.get("articles", [])[:10]:
                # Convert published date to timestamp
                pub_date = article.get("publishedAt", "")
                try:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                except:
                    timestamp = int(datetime.now().timestamp())
                
                news_items.append({
                    "symbol": symbol,
                    "headline": article.get("title", ""),
                    "summary": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "datetime": timestamp,
                    "category": "market",
                    "related": False  # Less specific match
                })
            
            if news_items:
                print(f"[✅ NewsAPI] Fetched {len(news_items)} news items for {symbol}")
                return news_items
    except Exception as e:
        print(f"[ERROR] NewsAPI error for {symbol}: {e}")
    
    print(f"[WARNING] No news data found for {symbol}")
    return []

def produce_news_data(news_item, producer):
    """
    Produce news data to Kafka topic by ticker
    Following architecture diagram: 'Kafka News topic by TICKER'
    Similar pattern to option_producer
    """
    # Create ticker-specific topic (following architecture diagram)
    topic = f"{TOPIC_PREFIX}_{news_item['symbol'].lower()}"
    
    # Structure data similar to option producer pattern
    data = {
        "id": str(uuid.uuid4()),
        "symbol": news_item["symbol"],
        "headline": news_item["headline"],
        "summary": news_item["summary"],
        "url": news_item["url"],
        "source": news_item["source"],
        "published_at": datetime.fromtimestamp(news_item["datetime"]).strftime("%Y-%m-%d %H:%M:%S"),
        "category": news_item.get("category", "general"),
        "related": news_item.get("related", False),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Produce to ticker-specific topic with symbol as key (for partitioning)
    producer.produce(
        topic,
        key=news_item["symbol"],
        value=json.dumps(data).encode("utf-8"),
        on_delivery=lambda err, msg: print("Delivery Report:", err or f"✅ Delivered to {msg.topic()} [{msg.partition()}]")
    )

def main():
    """
    Main producer loop - following option_producer pattern
    Implements 'Fetch related News' component from architecture diagram
    """
    producer = Producer(get_kafka_config())
    
    # Define symbols to track (similar to option_producer)
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"]
    use_mock_data = True  # Set to False when you have real API keys
    
    print(f"[News Producer] 🚀 Starting news producer for symbols: {symbols}")
    print(f"[News Producer] Mock data mode: {use_mock_data}")
    
    try:
        while True:
            total_news_produced = 0
            
            for symbol in symbols:
                try:
                    print(f"[News Producer] 📰 Fetching related news for {symbol}")
                    news_list = fetch_news_data(symbol, use_mock_data)
                    
                    if news_list:
                        for news_item in news_list:
                            try:
                                produce_news_data(news_item, producer)
                                total_news_produced += 1
                            except Exception as e:
                                print(f"[ERROR] Failed to produce news for {symbol}: {e}")
                        
                        print(f"[News Producer] ✅ Produced {len(news_list)} news items for {symbol}")
                    else:
                        print(f"[News Producer] ⚠️  No news found for {symbol}")
                        
                    # Small delay between symbols to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to fetch news for {symbol}: {e}")
                    continue
            
            # Flush all messages (following option_producer pattern)
            producer.flush()
            print(f"[News Producer] 📊 Total news items produced this cycle: {total_news_produced}")
            print("[News Producer] ⏱️  Waiting 60 seconds before next fetch cycle...")
            time.sleep(60)  # Fetch news every minute
            
    except KeyboardInterrupt:
        print("\n[News Producer] 👋 Shutting down gracefully...")
    except Exception as e:
        print(f"[FATAL ERROR] News producer crashed: {e}")
    finally:
        producer.flush()
        print("[News Producer] 🏁 Producer stopped")

if __name__ == "__main__":
    main()
