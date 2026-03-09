import os
import time
from typing import Literal, Optional

import requests

Provider = Literal["heuristic", "groq", "ollama", "gemini"]


def _safe_float(x) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def _heuristic_commentary(symbol, price, rsi, atr) -> str:
    price_f = _safe_float(price)
    rsi_f = _safe_float(rsi)
    atr_f = _safe_float(atr)

    if rsi_f is None or atr_f is None:
        return (
            f"{symbol}: Indicators unavailable or invalid. "
            "Unable to generate commentary without RSI/ATR."
        )

    if rsi_f >= 70:
        rsi_view = "overbought"
        bias = "elevated pullback risk"
    elif rsi_f <= 30:
        rsi_view = "oversold"
        bias = "bounce potential"
    else:
        rsi_view = "neutral"
        bias = "trend/range dependent on confirmation"

    vol_view = "high" if (price_f and atr_f >= 0.02 * price_f) else "moderate"
    px = f"{price_f:.2f}" if price_f is not None else str(price)

    return (
        f"{symbol} is trading around {px}. RSI ({rsi_f:.2f}) is {rsi_view}, suggesting {bias}. "
        f"ATR ({atr_f:.2f}) implies {vol_view} volatility; consider position sizing and using stops."
    )


def _groq_commentary(symbol, price, rsi, atr) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _heuristic_commentary(symbol, price, rsi, atr)

    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    timeout_s = float(os.getenv("GROQ_TIMEOUT", "30"))
    max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "350"))

    user_prompt = f"""
Symbol: {symbol}
Price: {price}
RSI: {rsi}
ATR: {atr}

Give a short market analysis and trading insight.
""".strip()

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional crypto analyst. Be concise, practical, and risk-aware. "
                    "Do not claim certainty; use probabilities and conditional language."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout_s,
        )
        resp.raise_for_status()
        data = resp.json()
        content = (
            ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        ).strip()
        return content or _heuristic_commentary(symbol, price, rsi, atr)
    except Exception:
        return _heuristic_commentary(symbol, price, rsi, atr)


def _ollama_commentary(symbol, price, rsi, atr) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    timeout_s = float(os.getenv("OLLAMA_TIMEOUT", "30"))

    prompt = f"""
You are a professional crypto analyst.
Write a short, practical market analysis (5-8 sentences) with risk-aware trading insight.

Symbol: {symbol}
Price: {price}
RSI: {rsi}
ATR: {atr}
""".strip()

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout_s,
        )
        resp.raise_for_status()
        data = resp.json()
        text = (data.get("response") or "").strip()
        return text or _heuristic_commentary(symbol, price, rsi, atr)
    except Exception:
        return _heuristic_commentary(symbol, price, rsi, atr)


_gemini_client = None


def _gemini_commentary(symbol, price, rsi, atr) -> str:
    """Optional provider. Falls back to heuristic if not configured or fails."""
    global _gemini_client

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return _heuristic_commentary(symbol, price, rsi, atr)

    # Lazy import so removing Gemini deps later won't break the app.
    from google import genai  # type: ignore
    from google.genai import errors as genai_errors  # type: ignore

    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=api_key)

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = f"""
You are a professional crypto analyst.

Symbol: {symbol}
Price: {price}
RSI: {rsi}
ATR: {atr}

Give a short market analysis and trading insight.
""".strip()

    for attempt in range(3):
        try:
            response = _gemini_client.models.generate_content(model=model, contents=prompt)
            return getattr(response, "text", "") or str(response)
        except genai_errors.ClientError as e:
            status_code = getattr(e, "status_code", None) or getattr(e, "code", None)
            if status_code == 429 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return _heuristic_commentary(symbol, price, rsi, atr)
        except Exception:
            return _heuristic_commentary(symbol, price, rsi, atr)


def analyze_market(symbol, price, rsi, atr) -> str:
    """
    Select provider using environment variable:
      - AI_PROVIDER=groq       (recommended)
      - AI_PROVIDER=heuristic  (free deterministic fallback)
      - AI_PROVIDER=ollama     (free local LLM)
      - AI_PROVIDER=gemini     (optional)
    """
    provider: Provider = os.getenv("AI_PROVIDER", "heuristic").strip().lower()  # type: ignore[assignment]

    if provider == "groq":
        return _groq_commentary(symbol, price, rsi, atr)
    if provider == "ollama":
        return _ollama_commentary(symbol, price, rsi, atr)
    if provider == "gemini":
        return _gemini_commentary(symbol, price, rsi, atr)
    return _heuristic_commentary(symbol, price, rsi, atr)



