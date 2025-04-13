
from langchain.agents.openai_assistant import OpenAIAssistantRunnable

summary_agent = OpenAIAssistantRunnable.create_assistant(
    name="Factor Summary GPT",
    instructions="수익률, 회귀 결과, 통계 수치를 종합해서 전문가 수준의 전략 분석과 결론을 도출해줘."
)

def run_summary_tool(context: dict):
    input_text = context['factor_stats']
    return summary_agent.invoke({"input": input_text})['output']
