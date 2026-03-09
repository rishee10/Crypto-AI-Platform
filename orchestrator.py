from agents.data_agent import fetch_market_data
from agents.indicator_agent import calculate_indicators
from agents.analysis_agent import analyze_market
from agents.risk_agent import evaluate_risk
from agents.report_agent import generate_report


def run_analysis(symbol: str, timeframe: str):
    """
    Orchestrate the full multi-agent crypto analysis workflow:
      1. Data agent: fetch OHLCV market data from the exchange
      2. Indicator agent: compute technical indicators (RSI, MACD, ATR, price)
      3. Risk agent: evaluate risk profile given indicators
      4. Analysis agent: use LLM to generate qualitative market analysis
      5. Report agent: combine everything into a structured report object
    """

    # 1) Fetch raw market data
    df = fetch_market_data(symbol=symbol, interval=timeframe, limit=200)

    # 2) Technical indicators
    indicators = calculate_indicators(df)

    # 3) Risk evaluation
    risk = evaluate_risk(indicators)

    # 4) LLM-based qualitative analysis
    narrative = analyze_market(
        symbol=symbol,
        price=indicators["price"],
        rsi=indicators["rsi"],
        atr=indicators["atr"],
    )

    # 5) Final structured report
    report = generate_report(
        symbol=symbol,
        timeframe=timeframe,
        indicators=indicators,
        risk=risk,
        narrative=narrative,
    )

    return report