def evaluate_risk(indicators):
    rsi = indicators["rsi"]
    atr = indicators["atr"]

    if rsi > 70:
        risk = "High"
    elif rsi > 50:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "risk_level": risk,
        "suggested_stop_loss": "2% below entry"
    }