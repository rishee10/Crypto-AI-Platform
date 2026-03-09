import ta

def calculate_indicators(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["macd"] = ta.trend.MACD(df["close"]).macd()
    df["atr"] = ta.volatility.AverageTrueRange(
        df["high"].astype(float),
        df["low"].astype(float),
        df["close"].astype(float)
    ).average_true_range()

    latest = df.iloc[-1]

    return {
        "rsi": round(latest["rsi"], 2),
        "macd": round(latest["macd"], 2),
        "atr": round(latest["atr"], 2),
        "price": round(latest["close"], 2)
    }