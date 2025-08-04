from confluent_kafka import Consumer, KafkaError
import json
import os
import uuid
from datetime import datetime
from opensearchpy import OpenSearch
import openai
from consumer.utils import get_kafka_config

# Topic pattern for ticker-based topics (following architecture diagram)
TOPIC_PATTERN = "news_topic_*"  # Subscribe to all ticker-based news topics

# OpenSearch configuration (works with Docker Compose)
OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.environ.get("OPENSEARCH_PORT", "9200"))
OPENSEARCH_USERNAME = os.environ.get("OPENSEARCH_USERNAME", "")  # No auth for testing
OPENSEARCH_PASSWORD = os.environ.get("OPENSEARCH_PASSWORD", "")  # No auth for testing
OPENSEARCH_USE_SSL = os.environ.get("OPENSEARCH_USE_SSL", "false").lower() == "true"

# OpenAI configuration
openai.api_key = os.environ.get("OPENAI_API_KEY", "dummy")

def get_opensearch_client():
    """Initialize OpenSearch client (works with Docker Compose setup)"""
    # Configure authentication only if credentials are provided
    auth_config = {}
    if OPENSEARCH_USERNAME and OPENSEARCH_PASSWORD:
        auth_config['http_auth'] = (OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD)
    
    return OpenSearch(
        hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
        use_ssl=OPENSEARCH_USE_SSL,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        **auth_config
    )

def analyze_news_impact_with_llm(news_data, use_mock_analysis=True):
    """
    Use LLM to analyze news impact on stock price
    Returns impact score (1-10) and reasoning
    """
    if use_mock_analysis:
        # Mock analysis for testing
        title = news_data.get("title", "")
        if "earnings" in title.lower() or "revenue" in title.lower():
            return {
                "impact_score": 8,
                "reasoning": "Earnings-related news typically has high impact on stock price",
                "sentiment": "positive",
                "confidence": 0.85
            }
        elif "lawsuit" in title.lower() or "investigation" in title.lower():
            return {
                "impact_score": 7,
                "reasoning": "Legal issues can negatively impact stock price",
                "sentiment": "negative", 
                "confidence": 0.80
            }
        else:
            return {
                "impact_score": 5,
                "reasoning": "General news with moderate potential impact",
                "sentiment": "neutral",
                "confidence": 0.60
            }
    
    try:
        # Construct prompt for LLM analysis (updated for new data structure)
        headline = news_data.get('headline', news_data.get('title', ''))
        summary = news_data.get('summary', news_data.get('description', ''))
        category = news_data.get('category', 'general')
        related = news_data.get('related', False)
        
        prompt = f"""
        Analyze the following news article about {news_data['symbol']} and rate its potential impact on the stock price.

        Headline: {headline}
        Summary: {summary}
        Category: {category}
        Related to company: {related}
        Source: {news_data['source']}

        Please provide:
        1. Impact Score (1-10 scale): 
           - 1-2: Much Negative Impace
           - 3-4: Negative Impact
           - 5-6: Neutral Impact
           - 7-8: Positive Impact
           - 9-10: Much Positive Impact
        2. Reasoning: Brief explanation for the score
        3. Sentiment: positive, negative, or neutral
        4. Confidence: How confident you are in this assessment (0.0-1.0)

        Respond in JSON format:
        {{
            "impact_score": <integer 1-10>,
            "reasoning": "<explanation>",
            "sentiment": "<positive/negative/neutral>",
            "confidence": <float 0.0-1.0>
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst expert at assessing news impact on stock prices."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        # Parse LLM response
        llm_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        try:
            analysis = json.loads(llm_response)
            return analysis
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            print(f"[WARNING] Could not parse LLM JSON response: {llm_response}")
            return {
                "impact_score": 5,
                "reasoning": "LLM analysis failed - default moderate impact",
                "sentiment": "neutral",
                "confidence": 0.50
            }

    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")
        return {
            "impact_score": 5,
            "reasoning": f"Analysis failed due to error: {str(e)}",
            "sentiment": "neutral",
            "confidence": 0.30
        }

def save_to_opensearch(news_data, analysis_result, opensearch_client):
    """Save analyzed news data to OpenSearch"""
    try:
        # Prepare document for OpenSearch (updated for new data structure)
        document = {
            "id": news_data["id"],
            "symbol": news_data["symbol"],
            "headline": news_data.get("headline", news_data.get("title", "")),  # Support both formats
            "summary": news_data.get("summary", news_data.get("description", "")),  # Support both formats
            "url": news_data["url"],
            "source": news_data["source"],
            "published_at": news_data["published_at"],
            "category": news_data.get("category", "general"),
            "related": news_data.get("related", False),
            
            # LLM Analysis Results
            "impact_score": analysis_result["impact_score"],
            "impact_reasoning": analysis_result["reasoning"],
            "llm_sentiment": analysis_result["sentiment"],
            "analysis_confidence": analysis_result["confidence"],
            
            # Metadata
            "analyzed_at": datetime.utcnow().isoformat(),
            "analysis_timestamp": news_data["timestamp"]
        }

        # Index name with ticker for better organization (per user request)
        index_name = f"news-analysis-{news_data['symbol'].lower()}"
        
        # Create/update document in OpenSearch
        response = opensearch_client.index(
            index=index_name,
            id=news_data["id"],
            body=document
        )

        print(f"[✅ OpenSearch] Saved analysis for {news_data['symbol']}: Impact Score {analysis_result['impact_score']}/10")
        return response

    except Exception as e:
        print(f"[❌ ERROR] Failed to save to OpenSearch: {e}")
        return None

def analyze_news(news_data):
    """Main analysis function that coordinates LLM analysis and OpenSearch storage"""
    try:
        # Get OpenSearch client
        opensearch_client = get_opensearch_client()
        
        # Analyze news impact with LLM
        print(f"[Analysis] Analyzing news: {news_data['title'][:50]}...")
        analysis_result = analyze_news_impact_with_llm(news_data, use_mock_analysis=True)
        
        # Save to OpenSearch
        save_to_opensearch(news_data, analysis_result, opensearch_client)
        
        print(f"[Analysis] Completed analysis for {news_data['symbol']} - Impact: {analysis_result['impact_score']}/10")
        
    except Exception as e:
        print(f"[❌ ERROR] Analysis failed for {news_data.get('symbol', 'unknown')}: {e}")

def main():
    """Main consumer loop"""
    consumer = Consumer({
        **get_kafka_config(),
        "group.id": "news_analysis_group",
        "auto.offset.reset": "earliest"
    })

    # Subscribe to all ticker-based news topics (following architecture diagram)
    from confluent_kafka.admin import AdminClient, NewTopic
    
    # Get list of existing ticker topics
    admin_client = AdminClient(get_kafka_config())
    metadata = admin_client.list_topics(timeout=10)
    
    # Find all news_topic_* topics
    news_topics = [topic for topic in metadata.topics if topic.startswith("news_topic_")]
    
    if news_topics:
        consumer.subscribe(news_topics)
        print(f"[Consumer] ✅ Subscribed to {len(news_topics)} ticker-based news topics")
    else:
        # Fallback to pattern-based subscription
        consumer.subscribe(["news_topic_aapl", "news_topic_msft", "news_topic_googl", "news_topic_tsla", "news_topic_nvda"])
        print("[Consumer] ✅ Subscribed to default ticker topics")
    
    print("[Consumer] ⏳ Waiting for news messages...")

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
                news_data = json.loads(msg.value().decode("utf-8"))
                analyze_news(news_data)
            except Exception as e:
                print(f"[❌ JSON ERROR] {e}")

    except KeyboardInterrupt:
        print("👋 Consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
