CREATE TABLE IF NOT EXISTS user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    ticker VARCHAR(16) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_news_preference (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    keywords TEXT[],
    sentiment_preference VARCHAR(32) DEFAULT 'all'
);

CREATE TABLE IF NOT EXISTS user_news_read (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    news_id UUID NOT NULL,
    read_at TIMESTAMP DEFAULT NOW()
);
