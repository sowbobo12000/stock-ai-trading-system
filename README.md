# Options Trading Analysis System

This system analyzes stock options data using LangGraph and provides trading recommendations based on option walls analysis. It helps traders identify potential support/resistance levels and make informed trading decisions based on options market data.

## Prerequisites

1. Python 3.8 or higher
2. Required Python packages (install via `pip install -r requirements.txt`):
   - langchain
   - langchain-openai
   - langgraph
   - pandas
   - yfinance
   - python-dotenv
   - pandas-market-calendars

3. Environment Variables:
   - Create a `.env` file in the root directory with:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ALPHAVANTAGE_API_KEY=your_alphavantage_api_key
     ```

## Data Collection

Before running the analysis, you need to collect options data:

```bash
python pipelines/options_data_collector.py
```

This will download options data for the specified symbols (currently set to QQQ, SPY, and NFLX).

## Running the Analysis

The options analysis system can be run with different options:

### Basic Usage
```bash
python pipelines/options_analyzer.py SYMBOL
```
Example:
```bash
python pipelines/options_analyzer.py NFLX
```

### With Language Selection
```bash
python pipelines/options_analyzer.py SYMBOL --language [EN|KO]
```
Example:
```bash
python pipelines/options_analyzer.py NFLX --language KO
```

### With Debug Output
```bash
python pipelines/options_analyzer.py SYMBOL --debug
```

### All Options
```bash
python pipelines/options_analyzer.py SYMBOL --language [EN|KO] --debug
```

## Analysis Output

The system provides:
1. Current stock price and volume
2. Options analysis including:
   - Major support and resistance levels
   - Option walls analysis
   - Volume and open interest patterns
3. Buy/Sell recommendations
4. Price targets based on option walls

## Example Output
```
==================================================
DISCLAIMER:
Please note that the ultimate responsibility for investment decisions and their outcomes lies with the investor.
==================================================

Stock Analysis for NFLX:
--------------------------------------------------

Current Price: $123.45
Price Change: $2.34
Volume: 1,234,567

OPTIONS ANALYSIS:
[Detailed options analysis will appear here]

BUY RECOMMENDATION:
Consider buying when the price reaches around $120.00
Reasoning: [Buy recommendation reasoning]

SELL RECOMMENDATION:
[Warning message]
Reasoning: [Sell recommendation reasoning]
```

## Troubleshooting

1. If you get an error about missing data:
   - Ensure you've run the data collection script first
   - Check that the stock symbol is correct
   - Verify that the data directory exists at `data/raw/options/SYMBOL/`

2. If you get API errors:
   - Verify your API keys in the `.env` file
   - Check your API usage limits
   - Ensure you have internet connectivity

## Contributing

Feel free to submit issues and enhancement requests! 