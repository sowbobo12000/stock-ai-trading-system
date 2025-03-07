from langgraph.graph import StateGraph, START, END

class StockGraphState:
    stock_data: list
    vector_data: list
    time_series_forecast: list
    tree_based_predictions: list

workflow = StateGraph(StockGraphState)

def fetch_data(state):
    print("Fetching stock data...")
    return {"stock_data": ["TSLA", "AAPL"]}

def vectorize(state):
    print("Vectorizing financial texts...")
    return {"vector_data": ["Vector1", "Vector2"]}

def predict_time_series(state):
    print("Predicting future stock prices...")
    return {"time_series_forecast": [205.4, 210.0]}

def predict_tree(state):
    print("Predicting with XGBoost model...")
    return {"tree_based_predictions": [206.0, 209.5]}

workflow.add_node("fetch_data", fetch_data)
workflow.add_node("vectorize", vectorize)
workflow.add_node("predict_time_series", predict_time_series)
workflow.add_node("predict_tree", predict_tree)

workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "vectorize")
workflow.add_edge("vectorize", "predict_time_series")
workflow.add_edge("predict_time_series", "predict_tree")
workflow.add_edge("predict_tree", END)

compiled_graph = workflow.compile()
print("Running Workflow:")
compiled_graph.invoke({})

