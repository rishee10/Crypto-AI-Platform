
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

from flask import Flask, render_template, request, jsonify
from orchestrator import run_analysis


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")
    timeframe = data.get("timeframe")

    if not symbol or not timeframe:
        return jsonify({"error": "Missing required fields: symbol, timeframe"}), 400

    try:
        result = run_analysis(symbol, timeframe)
        return jsonify(result)
    except Exception as e:
        # Avoid leaking stack traces to the client; the server logs still show them in debug mode.
        return jsonify({"error": "Analysis failed", "details": str(e)}), 503

if __name__ == "__main__":
    app.run(debug=True)