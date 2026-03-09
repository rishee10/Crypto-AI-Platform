from typing import Dict, Any


def generate_report(
    symbol: str,
    timeframe: str,
    indicators: Dict[str, float],
    risk: Dict[str, Any],
    narrative: str,
) -> Dict[str, Any]:
    """
    Combine all agent outputs into a single structured report object.

    This is what the API returns to the frontend – a clean, machine-readable
    summary that is not a chat response, but a deterministic analysis payload.
    """

    return {
        "meta": {
            "symbol": symbol,
            "timeframe": timeframe,
        },
        "market_overview": {
            "price": indicators.get("price"),
            "rsi": indicators.get("rsi"),
            "macd": indicators.get("macd"),
            "atr": indicators.get("atr"),
        },
        "risk_assessment": {
            "level": risk.get("risk_level"),
            "suggested_stop_loss": risk.get("suggested_stop_loss"),
        },
        "ai_commentary": narrative,
    }
