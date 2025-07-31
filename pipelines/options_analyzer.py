from typing import Dict, List, Tuple, Any, Literal, TypedDict
import os
from dotenv import load_dotenv
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from datetime import datetime, time, timedelta
import pytz
import yfinance as yf
import argparse

# Load environment variables
load_dotenv()

# Debug flag
DEBUG = False

def debug_print(*args, **kwargs):
    """Print debug messages only if DEBUG flag is True"""
    if DEBUG:
        print(*args, **kwargs)

# Initialize shared LLM client
SHARED_LLM = ChatOpenAI(model="gpt-4o", temperature=0)

# Disclaimer messages by language
DISCLAIMERS = {
    "EN": """
IMPORTANT DISCLAIMER:
Please note that the ultimate responsibility for investment decisions and their outcomes lies with the investor.
""",
    "KO": """
중요 안내:
투자 판단과 의사결정, 투자결과에 대한 책임은 결국 투자자 본인이 부담하게 된다는 점을 유념하시기 바랍니다.
"""
}

# Translation prompts
TRANSLATION_PROMPTS = {
    "KO": """Translate the following English investment analysis to Korean. 
    Maintain the professional tone and financial terminology.
    Keep numbers and symbols as is.
    Input: {text}"""
}

# Define state types
class StockAnalysisState(TypedDict, total=False):
    option_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    price_estimates: Dict[str, float]
    error: str
    language: str
    disclaimer: str
    stock_symbol: str
    buy_recommendation: Dict[str, Any]
    sell_recommendation: Dict[str, Any]
    stock_data: Dict[str, Any]
    news_impact: Dict[str, Any]
    translated_results: Dict[str, Any]

def create_initial_state(language: str = "EN", stock_symbol: str = None) -> StockAnalysisState:
    """Create initial state dictionary"""
    return {
        "option_data": None,
        "analysis_results": {},
        "price_estimates": {},
        "error": None,
        "language": language,
        "disclaimer": DISCLAIMERS.get(language, DISCLAIMERS["EN"]),
        "stock_symbol": stock_symbol,
        "buy_recommendation": {},
        "sell_recommendation": {},
        "stock_data": {},
        "news_impact": {},
        "translated_results": {}
    }

def is_market_open() -> bool:
    """Check if the US stock market is currently open."""
    try:
        # Get current time in US/Eastern timezone
        eastern = pytz.timezone('US/Eastern')
        current_time = datetime.now(eastern).time()
        current_date = datetime.now(eastern)
        
        # Market hours: 9:30 AM - 4:00 PM Eastern Time
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check if it's a weekday
        if current_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            debug_print("Market is closed: Weekend")
            return False
        
        # Check for market holidays using yfinance
        # Use SPY as a reference since it's one of the most liquid ETFs
        spy = yf.Ticker("SPY")
        calendar = spy.calendar
        
        if calendar is not None and not calendar.empty:
            # Get the next trading day
            next_trading_day = calendar.index[0]
            # If next trading day is not today, market is closed
            if next_trading_day.date() != current_date.date():
                debug_print(f"Market is closed: Holiday or non-trading day. Next trading day is {next_trading_day.date()}")
                return False
        
        # Check if current time is within market hours
        is_open = market_open <= current_time <= market_close
        debug_print(f"Market is {'open' if is_open else 'closed'}: Current time is {current_time}")
        return is_open
        
    except Exception as e:
        debug_print(f"Error checking market status: {str(e)}")
        # In case of API error, fall back to basic time check
        return market_open <= current_time <= market_close

def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get current stock data, handling pre-market and after-hours scenarios."""
    try:
        stock = yf.Ticker(symbol)
        
        # Get data for the last 2 days to ensure we have enough data
        hist = stock.history(period="2d")
        
        if hist.empty:
            return {
                "price": 0.0,
                "change": 0.0,
                "volume": 0,
                "timestamp": datetime.now().isoformat(),
                "market_status": "no_data"
            }
        
        # Get the most recent data point
        latest_data = hist.iloc[-1]
        
        # Determine market status
        if is_market_open():
            market_status = "open"
        else:
            market_status = "closed"
        
        return {
            "price": latest_data['Close'],
            "change": latest_data['Close'] - hist.iloc[-2]['Close'],
            "volume": latest_data['Volume'],
            "timestamp": datetime.now().isoformat(),
            "market_status": market_status
        }
    except Exception as e:
        debug_print(f"Error fetching stock data: {str(e)}")
        return {
            "price": 0.0,
            "change": 0.0,
            "volume": 0,
            "timestamp": datetime.now().isoformat(),
            "market_status": "error"
        }

def load_option_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Load and preprocess option data from Alphavantage CSV and fetch real-time data."""
    try:
        debug_print(f"Loading option data for {state.get('stock_symbol')}")
        if not state.get('stock_symbol'):
            raise ValueError("Stock symbol is required")
        
        # Check market status first
        market_status = is_market_open()
        debug_print(f"Market is {'open' if market_status else 'closed'}")
        
        # Load the most recent option data from Alphavantage
        options_dir = f"data/raw/options/{state['stock_symbol']}"
        debug_print(f"Looking for data in: {options_dir}")
        if not os.path.exists(options_dir):
            raise ValueError(f"No option data directory found for {state['stock_symbol']}")
        
        # Get all CSV files and sort them by date (newest first)
        csv_files = sorted([f for f in os.listdir(options_dir) if f.endswith('.csv')], reverse=True)
        debug_print(f"Found {len(csv_files)} CSV files")
        if not csv_files:
            raise ValueError(f"No option data files found for {state['stock_symbol']}")
        
        # Try each file until we find valid data
        valid_data_found = False
        for csv_file in csv_files:
            csv_path = os.path.join(options_dir, csv_file)
            debug_print(f"Trying to load data from: {csv_path}")
            
            # Load and preprocess the data
            df = pd.read_csv(csv_path)
            debug_print(f"Loaded data shape: {df.shape}")
            
            # Check if the CSV contains an error message instead of actual data
            if 'message' in df.columns and 'No data for symbol' in df['message'].iloc[0]:
                debug_print(f"Invalid data in {csv_file}, trying previous file...")
                continue
            
            # Validate required columns
            required_columns = ['strike', 'type', 'open_interest', 'volume', 'implied_volatility']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                debug_print(f"Missing required columns in {csv_file}: {missing_columns}, trying previous file...")
                continue
            
            # If we get here, we found valid data
            valid_data_found = True
            debug_print(f"Found valid data in {csv_file}")
            
            # Calculate option walls (significant open interest levels)
            df['option_wall'] = df['open_interest'] * df['strike']
            
            # Group by strike price and option type to identify walls
            walls = df.groupby(['strike', 'type']).agg({
                'open_interest': 'sum',
                'volume': 'sum',
                'implied_volatility': 'mean',
                'option_wall': 'sum'
            }).reset_index()
            
            # Sort by option wall size to identify significant levels
            walls = walls.sort_values('option_wall', ascending=False)
            debug_print(f"Analyzed {len(walls)} option walls")
            
            # Store both raw data and analyzed walls
            state['option_data'] = {
                'raw_data': df,
                'option_walls': walls,
                'latest_date': csv_file.replace('.csv', '')
            }
            break
        
        if not valid_data_found:
            raise ValueError(f"No valid option data found for {state['stock_symbol']} in any available files")
        
        # Get current stock data
        debug_print(f"Fetching current stock data for {state['stock_symbol']}")
        state['stock_data'] = get_stock_data(state['stock_symbol'])
        debug_print(f"Current price: ${state['stock_data']['price']:.2f} (Market: {state['stock_data']['market_status']})")
        
        # Simplified news impact for now
        state['news_impact'] = {
            "average_sentiment": 0.5,
            "average_impact": 0.5,
            "news_count": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        debug_print("Successfully loaded all data")
        return state
    except Exception as e:
        debug_print(f"Error in load_option_data: {str(e)}")
        state['error'] = f"Error loading data: {str(e)}"
        return state

def analyze_options(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze option data using GPT-4o with focus on option walls."""
    debug_print("\nStarting options analysis...")
    if state.get('error'):
        debug_print(f"Error found in state: {state['error']}")
        return state
    
    try:
        # Create a comprehensive prompt including option walls analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert options analyst specializing in option walls analysis. 
            Analyze the following data and provide insights:
            1. Option walls (significant open interest levels)
            2. Current stock data
            3. News impact analysis
            
            Focus on:
            - Major support and resistance levels from option walls
            - Potential price targets based on option wall distribution
            - Volume and open interest patterns
            - Implied volatility skew
            Consider all factors in your analysis."""),
            ("user", """Option Walls Data:
            {option_walls}
            
            Current Stock Data:
            {stock_data}
            
            News Impact Analysis:
            {news_impact}
            
            Latest Data Date: {latest_date}""")
        ])
        
        chain = prompt | SHARED_LLM | StrOutputParser()
        
        # Prepare data for analysis
        option_walls_str = state.get('option_data', {}).get('option_walls', pd.DataFrame()).to_string()
        debug_print("Prepared data for analysis")
        
        analysis = chain.invoke({
            "option_walls": option_walls_str,
            "stock_data": state.get('stock_data', {}),
            "news_impact": state.get('news_impact', {}),
            "latest_date": state.get('option_data', {}).get('latest_date', '')
        })
        debug_print("Generated analysis")
        
        # Store analysis results in state
        state['analysis_results'] = {
            "options_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        debug_print("Analysis complete")
        
        # Debug output
        debug_print("\nDebug - Analysis results:", state.get('analysis_results', {}))
        
        return state
    except Exception as e:
        debug_print(f"Error in analyze_options: {str(e)}")
        state['error'] = f"Error analyzing options: {str(e)}"
        return state

def estimate_stock_price(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate stock price estimates based on option walls analysis and news impact."""
    if state.get('error'):
        return state
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the option walls analysis and news impact, provide detailed buy and sell recommendations.
            Consider:
            1. Major support and resistance levels from option walls
            2. Current market conditions
            3. News sentiment and impact
            4. Technical indicators
            5. Market trends
            
            Focus on price levels where significant option walls exist, as these often act as support/resistance."""),
            ("user", """Analysis Results:
            {analysis}
            
            Option Walls:
            {option_walls}
            
            News Impact:
            {news_impact}
            
            Current Stock Data:
            {stock_data}""")
        ])
        
        chain = prompt | SHARED_LLM | StrOutputParser()
        
        analysis = state.get('analysis_results', {}).get("options_analysis", "")
        option_walls_str = state.get('option_data', {}).get('option_walls', pd.DataFrame()).to_string()
        
        recommendations = chain.invoke({
            "analysis": analysis,
            "option_walls": option_walls_str,
            "news_impact": state.get('news_impact', {}),
            "stock_data": state.get('stock_data', {})
        })
        
        # Parse recommendations into structured format
        state['buy_recommendation'] = {
            "price_target": state.get('stock_data', {}).get("price", 0.0),
            "reasoning": recommendations,
            "news_impact": state.get('news_impact', {}),
            "option_walls": state.get('option_data', {}).get('option_walls', pd.DataFrame()).to_dict('records')
        }
        
        state['sell_recommendation'] = {
            "warning": "Consider selling if price drops significantly as it may continue to fall",
            "reasoning": recommendations,
            "news_impact": state.get('news_impact', {}),
            "option_walls": state.get('option_data', {}).get('option_walls', pd.DataFrame()).to_dict('records')
        }
        
        return state
    except Exception as e:
        state['error'] = f"Error estimating stock price: {str(e)}"
        return state

def translate_results(state: Dict[str, Any]) -> Dict[str, Any]:
    """Translate analysis results to the target language if not English."""
    if state.get('error') or state.get('language') == "EN":
        return state
    
    try:
        # Translation prompts for different content types
        translation_prompts = {
            "analysis": """Translate the following English investment analysis to Korean. 
            Maintain the professional tone and financial terminology.
            Keep numbers, symbols, and technical terms as is.
            Input: {text}""",
            
            "recommendation": """Translate the following English investment recommendation to Korean.
            Maintain the professional tone and financial terminology.
            Keep numbers, symbols, and technical terms as is.
            Input: {text}""",
            
            "stock_data": """Translate the following English stock data description to Korean.
            Keep numbers, symbols, and technical terms as is.
            Input: {text}"""
        }
        
        # Create translation chain
        def create_translation_chain(prompt_template):
            return ChatPromptTemplate.from_messages([
                ("system", prompt_template),
                ("user", "{text}")
            ]) | SHARED_LLM | StrOutputParser()
        
        # Translate each component
        translated_content = {}
        
        # Translate analysis results
        if state.get('analysis_results', {}).get("options_analysis"):
            analysis_chain = create_translation_chain(translation_prompts["analysis"])
            translated_content["analysis"] = analysis_chain.invoke({
                "text": state['analysis_results']["options_analysis"]
            })
        
        # Translate buy recommendation
        if state.get('buy_recommendation', {}).get("reasoning"):
            recommendation_chain = create_translation_chain(translation_prompts["recommendation"])
            translated_content["buy_recommendation"] = recommendation_chain.invoke({
                "text": state['buy_recommendation']["reasoning"]
            })
        
        # Translate sell recommendation
        if state.get('sell_recommendation', {}).get("reasoning"):
            recommendation_chain = create_translation_chain(translation_prompts["recommendation"])
            translated_content["sell_recommendation"] = recommendation_chain.invoke({
                "text": state['sell_recommendation']["reasoning"]
            })
        
        # Translate stock data description
        if state.get('stock_data'):
            stock_data_text = f"Current Price: ${state['stock_data'].get('price', 0.0):.2f}\n"
            stock_data_text += f"Price Change: ${state['stock_data'].get('change', 0.0):.2f}\n"
            stock_data_text += f"Volume: {state['stock_data'].get('volume', 0):,}\n"
            stock_data_text += f"Market Status: {state['stock_data'].get('market_status', 'unknown')}"
            
            stock_data_chain = create_translation_chain(translation_prompts["stock_data"])
            translated_content["stock_data"] = stock_data_chain.invoke({
                "text": stock_data_text
            })
        
        state['translated_results'] = translated_content
        return state
    except Exception as e:
        state['error'] = f"Error translating results: {str(e)}"
        return state

def format_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """Format the final output message."""
    debug_print("\nFormatting output...")
    if state.get('error'):
        debug_print(f"Error found in state: {state['error']}")
        return {
            **state,  # Include all existing state
            "formatted_output": f"Error: {state['error']}"
        }
    
    try:
        output = []
        output.append("=" * 50)
        output.append("DISCLAIMER:")
        output.append(DISCLAIMERS.get(state.get('language', 'EN'), DISCLAIMERS["EN"]))
        output.append("=" * 50)
        
        if state.get('stock_symbol'):
            output.append(f"\nStock Analysis for {state['stock_symbol']}:")
            output.append("-" * 50)
            
            # Add current price information
            if state.get('stock_data'):
                if state.get('language') != "EN" and state.get('translated_results', {}).get('stock_data'):
                    output.append(state['translated_results']['stock_data'])
                else:
                    output.append(f"\nCurrent Price: ${state['stock_data'].get('price', 0.0):.2f}")
                    output.append(f"Price Change: ${state['stock_data'].get('change', 0.0):.2f}")
                    output.append(f"Volume: {state['stock_data'].get('volume', 0):,}")
                    output.append(f"Market Status: {state['stock_data'].get('market_status', 'unknown')}")
            
            # Add analysis results
            if state.get('analysis_results'):
                output.append("\nOPTIONS ANALYSIS:")
                if state.get('language') != "EN" and state.get('translated_results', {}).get('analysis'):
                    output.append(state['translated_results']['analysis'])
                elif isinstance(state['analysis_results'], dict) and 'options_analysis' in state['analysis_results']:
                    output.append(state['analysis_results']['options_analysis'])
                else:
                    output.append(str(state['analysis_results']))
            
            # Add buy/sell recommendations
            if state.get('buy_recommendation'):
                output.append("\nBUY RECOMMENDATION:")
                if state.get('language') != "EN" and state.get('translated_results', {}).get('buy_recommendation'):
                    output.append(state['translated_results']['buy_recommendation'])
                elif state.get('buy_recommendation', {}).get('reasoning'):
                    output.append(state['buy_recommendation']['reasoning'])
            
            if state.get('sell_recommendation'):
                output.append("\nSELL RECOMMENDATION:")
                if state.get('language') != "EN" and state.get('translated_results', {}).get('sell_recommendation'):
                    output.append(state['translated_results']['sell_recommendation'])
                elif state.get('sell_recommendation', {}).get('reasoning'):
                    output.append(state['sell_recommendation']['reasoning'])
        
        formatted_text = "\n".join(output)
        debug_print("Output formatting complete")
        debug_print("Debug - Formatted text length:", len(formatted_text))
        
        # Return the complete state with formatted output
        return {
            **state,  # Include all existing state
            "formatted_output": formatted_text
        }
    except Exception as e:
        debug_print(f"Error in format_output: {str(e)}")
        return {
            **state,  # Include all existing state
            "formatted_output": f"Error formatting output: {str(e)}",
            "error": str(e)
        }

def should_continue(state: Dict[str, Any]) -> str:
    """Determine if the pipeline should continue or end."""
    if state.get('error'):
        return "error"
    return "continue"

# Create the graph
def create_stock_analysis_graph() -> StateGraph:
    """Create and configure the LangGraph pipeline."""
    workflow = StateGraph(StockAnalysisState)
    
    # Add nodes with proper state handling
    workflow.add_node("load_data", lambda x: load_option_data(x))
    workflow.add_node("analyze_options", lambda x: analyze_options(x))
    workflow.add_node("estimate_price", lambda x: estimate_stock_price(x))
    workflow.add_node("translate_results", lambda x: translate_results(x))
    workflow.add_node("format_output", lambda x: format_output(x))
    
    # Add edges with proper state handling
    workflow.add_edge("load_data", "analyze_options")
    workflow.add_edge("analyze_options", "estimate_price")
    workflow.add_edge("estimate_price", "translate_results")
    workflow.add_edge("translate_results", "format_output")
    workflow.add_edge("format_output", END)
    
    # Set entry point
    workflow.set_entry_point("load_data")
    
    return workflow

def run_pipeline(language: Literal["EN", "KO"] = "EN", stock_symbol: str = None, debug: bool = False) -> Dict[str, Any]:
    """Run the complete stock analysis pipeline."""
    global DEBUG
    DEBUG = debug
    
    debug_print(f"\nStarting pipeline for {stock_symbol}")
    if not stock_symbol:
        raise ValueError("Stock symbol is required")
    
    # Create initial state
    initial_state = create_initial_state(language=language, stock_symbol=stock_symbol)
    debug_print("Created initial state")
    
    # Create and compile the graph
    graph = create_stock_analysis_graph()
    app = graph.compile()
    debug_print("Compiled graph")
    
    try:
        # Run the pipeline
        debug_print("Running pipeline...")
        result = app.invoke(initial_state)
        debug_print("Pipeline completed")
        
        # Debug output
        debug_print("\nDebug - Result keys:", result.keys() if result else "No result")
        debug_print("Debug - State contents:", {k: v for k, v in result.items() if k != 'option_data'} if result else "No state")
        
        # Ensure we have a formatted output
        if not result or "formatted_output" not in result:
            debug_print("No formatted output found in result")
            # Create a formatted output from the available data
            formatted_output = format_output(result if result else initial_state)
            return formatted_output
        
        # Debug the formatted output
        debug_print("\nDebug - Formatted output length:", len(result.get("formatted_output", "")))
        debug_print("Debug - First 100 chars of formatted output:", result.get("formatted_output", "")[:100])
        
        return result
    except Exception as e:
        debug_print(f"Error in pipeline: {str(e)}")
        return {
            "formatted_output": f"Error running pipeline: {str(e)}",
            "error": str(e),
            "language": language,
            "stock_symbol": stock_symbol
        }

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run stock options analysis pipeline')
    parser.add_argument('symbol', type=str, help='Stock symbol to analyze (e.g., NFLX, AAPL)')
    parser.add_argument('--language', type=str, choices=['EN', 'KO'], default='EN',
                      help='Output language (EN or KO, default: EN)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug output')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Run pipeline with command line arguments
        results = run_pipeline(
            language=args.language,
            stock_symbol=args.symbol,
            debug=args.debug
        )
        print("\nFinal output:")
        print(results.get("formatted_output", "No output available"))
    except Exception as e:
        print(f"Error: {str(e)}")
