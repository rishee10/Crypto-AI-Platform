## Groq setup (LLM commentary)

This app can generate `ai_commentary` using **Groq's OpenAI-compatible API**.

### 1) Add to your `.env`

Set these variables:

- **`AI_PROVIDER=groq`**
- **`GROQ_API_KEY=YOUR_KEY_HERE`**


### 2) Run the app

```bash
python app.py
```

### 3) Test the API

```bash
curl -X POST http://127.0.0.1:5000/api/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"symbol\":\"ETHUSDT\",\"timeframe\":\"1h\"}"
```

If Groq is unreachable or misconfigured, the server will automatically fall back to deterministic `heuristic` commentary (so you won't see 500s).


