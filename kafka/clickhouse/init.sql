-- option_data: 옵션 정보
CREATE TABLE IF NOT EXISTS option_data (
    id UUID,
    symbol String,
    expiry_date Date,
    strike_price Float64,
    call_put String,
    implied_volatility Float64,
    volume UInt32,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (symbol, expiry_date, strike_price, call_put);

-- news_data: 뉴스 정보
CREATE TABLE IF NOT EXISTS news_data (
    id UUID,
    title String,
    body String,
    ticker Array(String),
    provider String,
    published_at DateTime,
    url String,
    sentiment String,
    impact_score Float64,
    summary String
) ENGINE = MergeTree()
ORDER BY (published_at);
