
# 🌟 Intelligent Stock Trading Assistant

> AI-powered stock analysis platform built with Django, Celery, LangGraph/OpenAI, and OpenSearch.  
> Designed to crawl financial news, analyze sentiment, and generate actionable trading signals using modular micro-agents.

---

## 📐 System Architecture

```text
[ Crawling System ]
    └── Modular crawlers (Yahoo, Bloomberg, SeekingAlpha)

[ Analyze System ]
    └── GPT / LangGraph LLM sentiment + summary

[ Impact Analysis System ]
    └── Stores analyzed result in DB, optionally pushes to OpenSearch

[ Main Stock Agent ]
    └── Consumes analysis and generates signals

[ Alerting Engine ]
    └── Triggers alerts based on trading rules or AI findings

[ Metadata Layer ]
    └── PostgreSQL, OpenSearch, Redis
```

---

## 🎨 Ghibli-style System Flow

![Architecture - Ghibli Style](./docs/assets/ghibli_architecture_diagram.png)

---

## ⚙️ Tech Stack

| Layer              | Technology                            |
|-------------------|----------------------------------------|
| Backend Framework | Django + Django REST Framework (DRF)   |
| Auth              | SimpleJWT                              |
| Async Tasks       | Celery + Redis                         |
| Language Model    | GPT / LangGraph                        |
| Crawling System   | Modular (Interface + Task-based)       |
| Database          | PostgreSQL                             |
| Search Layer      | OpenSearch                             |
| API Docs          | Swagger via drf-yasg                   |

---

## 💼 Key Features

### ✈️ Crawling System
- Interface-based architecture (`BaseNewsCrawler`)
- Per-source crawler modules (`yfinance`, `seekingalpha`, ...)
- Celery async orchestration for real-time + scheduled jobs
- Duplicate detection via (symbol, source, title)

### 🧠 Impact Analysis
- `NewsImpact` model links to `NewsArticle`
- Stores:
  - Sentiment (positive, negative, neutral)
  - Confidence score
  - LLM-generated summary
  - Related symbols
- Status management with enums: `ANALYZING`, `ANALYZED`

### 🔐 Authentication
- JWT token-based auth via `djangorestframework-simplejwt`
- All ViewSets protected with `IsAuthenticated`

### 📊 Swagger API Docs
- Auto-generated from serializers
- `@action` support with descriptions and schemas

---

## 🔁 Example Data Flow

```text
User registers TSLA
    ↓
CrawlingSystem fetches from Yahoo/Bloomberg
    ↓
Articles saved → Celery triggers analyze_news_impact
    ↓
LLM generates summary + sentiment
    ↓
Saved in NewsImpact model
    ↓
Optional: push to OpenSearch
    ↓
Consumed by StockAgent or Alert Engine
```

---

## 🔧 API Highlights

| Method | Endpoint                                     | Description                            |
|--------|----------------------------------------------|----------------------------------------|
| POST   | `/api/crawl/news/{id}/analyze/`              | Trigger LLM analysis for a news item   |
| POST   | `/api/crawl/news/{id}/reset_analysis/`       | Reset analysis result                  |
| POST   | `/api/crawl/news/fetch_now/?symbol=TSLA`     | Fetch news immediately for a symbol    |
| GET    | `/api/crawl/candles/stats/`                  | Get candle data statistics             |

---

## 🧱 Project Structure

```text
stock_ai_project/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── urls_api.py
├── core/
│   ├── models.py
│   ├── choices.py
│   └── serializers.py
├── crawling_system/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py
│   └── crawling/
│       ├── base.py
│       └── yfinance_crawler.py
├── impact_analysis/
│   ├── models.py
│   ├── tasks.py
│   └── signals.py
├── manage.py
└── docs/
    └── assets/
        └── ghibli_architecture_diagram.png
```

---

## ✅ What’s Done

- [x] Django + DRF project structure
- [x] Interface-based crawling architecture
- [x] Modular crawlers for Yahoo & more
- [x] Celery async task integration
- [x] LLM sentiment analysis pipeline
- [x] NewsImpact storage + enum-based status
- [x] Swagger + JWT protected APIs
- [x] Custom `@action()` routes for analyze/reset

---

## 🗺️ Roadmap: What’s Next?

| Feature                               | Priority |
|--------------------------------------|----------|
| 🔥 LangGraph agent integration        | High     |
| 🔄 Push NewsImpact to OpenSearch     | High     |
| 📡 WebSocket-based alert push        | Medium   |
| 🧠 Rule-based signal engine          | High     |
| ⭐ Favorite stock tracking per user  | Medium   |
| 🧪 LangChain + Pinecone integration  | Low      |

---

## 📜 License

MIT License

---

## ✨ Made with love, tech, and Ghibli vibes by [Your Team Name]
