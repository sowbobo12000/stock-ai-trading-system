def compute_signal_score(data):
    """
    볼린저 밴드 + RSI + MACD + Disparity Index 기반 점수 계산 예시
    """
    score = 50
    if data.get("disparity") < -3:
        score += 10
    if data.get("rsi") < 35:
        score += 10
    if data.get("macd_histogram") < 0:
        score += 5
    if data.get("bollinger_breakdown"):
        score += 15
    return min(score, 100)