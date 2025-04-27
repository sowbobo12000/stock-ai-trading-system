# infra/lambda/handler.py

import os
import json
import requests
from datetime import datetime
from crawler.yfinance import fetch_articles, fetch_options, fetch_candles
from analyzer.gpt import analyze_article

API_BASE = os.environ.get("API_BASE_URL", "https://your-django-api.com")
API_KEY = os.environ.get("API_KEY", "")  # Optional JWT
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

def lambda_handler(event, context):
    symbol = event.get("symbol")
    data_type = event.get("type", "news")  # 'news', 'option', 'price_candle'

    if not symbol:
        return {"status": "error", "message": "Missing symbol"}

    try:
        if data_type == "news":
            articles = fetch_articles(symbol)
            for article in articles:
                # Analyze news
                analysis = analyze_article(article["content"])

                # Save to Django
                requests.post(f"{API_BASE}/api/crawl/news/", json=article, headers=HEADERS)

                # Save impact
                impact = {
                    "symbol": article["symbol"],
                    "summary": analysis["summary"],
                    "sentiment": analysis["sentiment"],
                    "score": analysis["score"],
                    "related_symbols": [symbol],
                }
                requests.post(f"{API_BASE}/api/impact/", json=impact, headers=HEADERS)

        elif data_type == "option":
            options = fetch_options(symbol)
            for opt in options:
                requests.post(f"{API_BASE}/api/crawl/optiondata/", json=opt, headers=HEADERS)

        elif data_type == "price_candle":
            candles = fetch_candles(symbol)
            for c in candles:
                requests.post(f"{API_BASE}/api/crawl/pricecandle/", json=c, headers=HEADERS)

        else:
            return {"status": "error", "message": f"Invalid type: {data_type}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "ok",
        "symbol": symbol,
        "type": data_type
    }









