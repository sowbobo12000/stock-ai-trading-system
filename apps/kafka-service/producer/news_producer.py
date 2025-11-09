import hashlib
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer

# Kafka topic pattern: news_topic_by_ticker (following architecture diagram)
TOPIC_PREFIX = "news_topic"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "dummy")  # NewsAPI.org key
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "dummy")  # Finnhub.io key


def get_kafka_config():
    return {"bootstrap.servers": "127.0.0.1:29092"}


def generate_news_id(symbol, url, headline):
    """
    Generate a deterministic unique ID for news items to prevent duplicates.
    Uses hash of symbol + url + headline to ensure same news gets same ID.
    """
    # Create unique string from key fields
    unique_string = f"{symbol}:{url}:{headline}"
    
    # Generate hash-based ID
    hash_object = hashlib.md5(unique_string.encode())
    news_id = hash_object.hexdigest()
    
    return f"news_{symbol.lower()}_{news_id[:16]}"


def fetch_financialjuice_news(symbol):
    """
    Fetch news from FinancialJuice for a specific ticker
    Source: https://www.financialjuice.com/Nasdaq/{TICKER}
    """
    try:
        # Construct URL following the pattern Nasdaq/Ticker
        url = f"https://www.financialjuice.com/Nasdaq/{symbol.upper()}"

        # Set headers to mimic a real browser and avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        print(f"[FinancialJuice] Fetching news from: {url}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            news_items = []

            # Look for news content (ignoring signup modals and ads)
            # Try multiple selectors to find news items
            selectors_to_try = [
                'div[class*="news"]',
                'div[class*="headline"]',
                'div[class*="story"]',
                'div[class*="article"]',
                'li[class*="news"]',
                'p[class*="news"]',
                '.market-news',
                '.news-item',
                '.headline',
                '.breaking-news'
            ]

            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"[FinancialJuice] Found {len(elements)} elements with selector: {selector}")
                    break

            # If no specific news selectors found, try to extract text content
            if not elements:
                # Look for any text that might be news content
                # Filter out modal/signup/ad content
                text_elements = soup.find_all(['div', 'p', 'span'],
                                              string=re.compile(r'(breaking|news|reports|announces|says|stated)',
                                                                re.IGNORECASE))
                elements = [elem for elem in text_elements if elem.text and len(elem.text.strip()) > 20]
                print(f"[FinancialJuice] Found {len(elements)} text elements with news keywords")

            # Extract news items from found elements
            for i, element in enumerate(elements[:10]):  # Limit to 10 items
                try:
                    # Extract text content
                    text = element.get_text(strip=True) if element else ""

                    # Skip if text is too short or contains signup/ad keywords
                    skip_keywords = ['sign up', 'join us', 'subscribe', 'login', 'register', 'free trial', 'premium']
                    if len(text) < 20 or any(keyword in text.lower() for keyword in skip_keywords):
                        continue

                    # Try to find associated links
                    link_element = element.find('a') if hasattr(element, 'find') else None
                    news_url = link_element.get('href') if link_element else url

                    # Make relative URLs absolute
                    if news_url and not news_url.startswith('http'):
                        news_url = f"https://www.financialjuice.com{news_url}" if news_url.startswith('/') else url

                    # Create news item
                    news_item = {
                        "symbol": symbol,
                        "headline": text[:200] + "..." if len(text) > 200 else text,  # Truncate long headlines
                        "summary": text,
                        "url": news_url,
                        "source": "FinancialJuice",
                        "datetime": int(datetime.now().timestamp()),  # Current time since we don't have publish time
                        "category": "market",
                        "related": True
                    }

                    news_items.append(news_item)

                except Exception as e:
                    print(f"[FinancialJuice] Error processing element: {e}")
                    continue

            if news_items:
                print(f"[✅ FinancialJuice] Extracted {len(news_items)} news items for {symbol}")
                return news_items
            else:
                print(f"[⚠️ FinancialJuice] No news content found for {symbol}")

                # Debug: Print page structure
                print(f"[DEBUG] Page title: {soup.title.string if soup.title else 'No title'}")
                print(f"[DEBUG] Found {len(soup.find_all(['div', 'p', 'span']))} content elements")

        else:
            print(f"[ERROR] FinancialJuice returned status {response.status_code} for {symbol}")

    except Exception as e:
        print(f"[ERROR] FinancialJuice error for {symbol}: {e}")

    return []


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

    # Try FinancialJuice first - specialized financial news source
    try:
        financialjuice_news = fetch_financialjuice_news(symbol)
        if financialjuice_news:
            return financialjuice_news
    except Exception as e:
        print(f"[ERROR] FinancialJuice error for {symbol}: {e}")

    # Fetch from Finnhub for company-specific news (secondary source)
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
    # Generate deterministic ID to prevent duplicates in OpenSearch
    unique_id = generate_news_id(
        news_item["symbol"], 
        news_item["url"], 
        news_item["headline"]
    )
    
    data = {
        "id": unique_id,
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
        on_delivery=lambda err, msg: print("Delivery Report:",
                                           err or f"✅ Delivered to {msg.topic()} [{msg.partition()}]")
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
