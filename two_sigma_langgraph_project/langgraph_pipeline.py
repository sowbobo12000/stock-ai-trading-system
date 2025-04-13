
from langgraph.graph import StateGraph, END
from tools import run_summary_tool

class AnalysisState(dict): pass

def factor_summary_node(state):
    result = run_summary_tool(state)
    return {"final_summary": result}

graph = StateGraph(AnalysisState)
graph.add_node("FactorSummary", factor_summary_node)
graph.set_entry_point("FactorSummary")
graph.add_edge("FactorSummary", END)

app = graph.compile()

if __name__ == "__main__":
    sample_input = {
        "factor_stats": """
- Global Equity: 연 수익률 12.3%, Sharpe 1.2
- Credit: 수익률 4.5%, 변동성 9%, 회귀계수 0.6
- Commodities: Drawdown -20%, 회귀 t-stat 2.1
이걸 종합해서 결론 도출
"""
    }
    result = app.invoke(sample_input)
    print(result['final_summary'])
