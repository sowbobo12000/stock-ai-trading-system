import json
import os
from datetime import datetime

import openai
import yaml
from confluent_kafka import Consumer, KafkaError
from utils import get_kafka_config
from opensearchpy import OpenSearch

# Topic pattern for ticker-based topics (following architecture diagram)
TOPIC_PATTERN = "news_topic_*"  # Subscribe to all ticker-based news topics


# Load configuration from YAML file
def load_config():
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'news_analysis_config.yaml')
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        print(f"[Config] ✅ Loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"[Config] ❌ Failed to load config from {config_path}: {e}")
        # Return default configuration
        return {
            'llm': {
                'model': 'gpt-4o',
                'max_tokens': 500,
                'temperature': 0.3,
                'use_mock_fallback': True
            },
            'prompts': {
                'system_prompt': 'You are a financial analyst expert at assessing news impact on stock prices.',
                'analysis_prompt': 'Analyze this news and provide impact score 1-10, reasoning, sentiment, and confidence.'
            },
            'mock_analysis': {'enabled': True}
        }


# Load configuration
CONFIG = load_config()

# OpenSearch configuration
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


def analyze_news_impact_with_llm(news_data, use_mock_analysis=None):
    """
    Use LLM to analyze news impact on stock price
    Returns impact score (1-10) and reasoning
    Uses configurable model and prompts from YAML config
    """
    # Use config setting if not explicitly specified
    if use_mock_analysis is None:
        use_mock_analysis = CONFIG.get('mock_analysis', {}).get('enabled', True)

    if use_mock_analysis:
        # Enhanced mock analysis using config rules
        mock_config = CONFIG.get('mock_analysis', {})
        rules = mock_config.get('rules', {})

                # Check headline and summary for keywords
        text_to_analyze = (news_data.get('headline', news_data.get('title', '')) + ' ' + 
                          news_data.get('summary', news_data.get('description', '')) + ' ' + 
                          news_data.get('title', '') + ' ' + 
                          news_data.get('description', '')).lower()

        # Apply rules based on keywords
        for keyword, rule in rules.items():
            if keyword != 'default' and keyword in text_to_analyze:
                print(f"[Mock Analysis] Applied rule '{keyword}' for {news_data['symbol']}")
                return rule

        # Default rule
        default_rule = rules.get('default', {
            "impact_score": 5,
            "reasoning": "General news with moderate potential impact",
            "sentiment": "neutral",
            "confidence": 0.60
        })
        print(f"[Mock Analysis] Applied default rule for {news_data['symbol']}")
        return default_rule

    try:
        # Get LLM configuration
        llm_config = CONFIG.get('llm', {})
        prompts_config = CONFIG.get('prompts', {})

        # Construct prompt using configurable template
        headline = news_data.get('headline', news_data.get('title', ''))
        summary = news_data.get('summary', news_data.get('description', ''))
        category = news_data.get('category', 'general')
        related = news_data.get('related', False)

        # Use configurable prompt template
        prompt_template = prompts_config.get('analysis_prompt',
                                             'Analyze this news and provide impact score 1-10, reasoning, sentiment, and confidence.')

        # Format the prompt with actual data
        formatted_prompt = prompt_template.format(
            symbol=news_data['symbol'],
            headline=headline,
            summary=summary,
            category=category,
            related=related,
            source=news_data['source']
        )

        # Get system prompt from config
        system_prompt = prompts_config.get('system_prompt',
                                           'You are a financial analyst expert at assessing news impact on stock prices.')

        print(f"[LLM Analysis] Using model: {llm_config.get('model', 'gpt-4o')}")

        response = openai.ChatCompletion.create(
            model=llm_config.get('model', 'gpt-4o'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ],
            max_tokens=llm_config.get('max_tokens', 500),
            temperature=llm_config.get('temperature', 0.3)
        )

        # Parse LLM response
        llm_response = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        try:
            analysis = json.loads(llm_response)
            print(f"[✅ LLM Analysis] Completed for {news_data['symbol']}: Impact {analysis.get('impact_score')}/10")
            return analysis
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            print(f"[WARNING] Could not parse LLM JSON response: {llm_response}")

            # Check if should use mock fallback
            if llm_config.get('use_mock_fallback', True):
                print(f"[Fallback] Using mock analysis for {news_data['symbol']}")
                return analyze_news_impact_with_llm(news_data, use_mock_analysis=True)

            return {
                "impact_score": 5,
                "reasoning": "LLM analysis failed - default moderate impact",
                "sentiment": "neutral",
                "confidence": 0.50
            }

    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")

        # Check if should use mock fallback
        llm_config = CONFIG.get('llm', {})
        if llm_config.get('use_mock_fallback', True):
            print(f"[Fallback] Using mock analysis for {news_data['symbol']} due to LLM error")
            return analyze_news_impact_with_llm(news_data, use_mock_analysis=True)

        return {
            "impact_score": 5,
            "reasoning": f"Analysis failed due to error: {str(e)}",
            "sentiment": "neutral",
            "confidence": 0.30
        }


def save_to_opensearch(news_data, analysis_result, opensearch_client):
    """Save analyzed news data to OpenSearch with duplicate prevention"""
    try:
        # Index name with ticker for better organization (per user request)
        index_name = f"news-analysis-{news_data['symbol'].lower()}"
        document_id = news_data["id"]
        
        # Check if document already exists to prevent unnecessary processing
        try:
            existing = opensearch_client.get(index=index_name, id=document_id)
            print(f"[🔄 Duplicate] News already analyzed for {news_data['symbol']}: {document_id[:16]}...")
            return existing  # Return existing document, don't reprocess
        except Exception:
            # Document doesn't exist, proceed with saving
            pass
        
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

        # Create/update document in OpenSearch (deterministic ID prevents duplicates)
        response = opensearch_client.index(
            index=index_name,
            id=document_id,
            body=document
        )

        print(
            f"[✅ OpenSearch] Saved analysis for {news_data['symbol']}: Impact Score {analysis_result['impact_score']}/10")
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
        print(f"[Analysis] Analyzing news: {news_data.get('headline', news_data.get('title', 'No title'))[:50]}...")
        analysis_result = analyze_news_impact_with_llm(news_data, use_mock_analysis=True)

        # Save to OpenSearch
        save_to_opensearch(news_data, analysis_result, opensearch_client)

        print(f"[Analysis] Completed analysis for {news_data['symbol']} - Impact: {analysis_result['impact_score']}/10")

    except Exception as e:
        print(f"[❌ ERROR] Analysis failed for {news_data.get('symbol', 'unknown')}: {e}")


def main():
    """Main consumer loop"""
    print("[News Analysis Consumer] 🚀 Starting with configurable LLM analysis")
    print(f"[Config] Model: {CONFIG.get('llm', {}).get('model', 'default')}")
    print(f"[Config] Mock analysis: {CONFIG.get('mock_analysis', {}).get('enabled', True)}")

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
        consumer.subscribe(
            ["news_topic_aapl", "news_topic_msft", "news_topic_googl", "news_topic_tsla", "news_topic_nvda"])
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
