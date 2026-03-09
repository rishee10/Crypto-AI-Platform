const $ = (id) => document.getElementById(id);

function setStatus(kind, text) {
  const pill = $("statusPill");
  pill.classList.remove("status--loading", "status--ok", "status--err");
  if (kind === "loading") pill.classList.add("status--loading");
  if (kind === "ok") pill.classList.add("status--ok");
  if (kind === "err") pill.classList.add("status--err");
  pill.textContent = text;
}

function fmtNum(x, digits = 2) {
  const n = Number(x);
  if (Number.isFinite(n)) return n.toFixed(digits);
  return String(x ?? "");
}

function riskBadge(level) {
  const l = String(level || "").toLowerCase();
  if (l.includes("high")) return ["badge badge--bad", "High risk"];
  if (l.includes("medium")) return ["badge badge--warn", "Medium risk"];
  if (l.includes("low")) return ["badge badge--good", "Low risk"];
  return ["badge", level || "—"];
}

function renderReport(data) {
  const report = $("report");

  if (!data || data.error) {
    report.innerHTML = `<div class="empty">${data?.error ? `${data.error}${data.details ? ` — ${data.details}` : ""}` : "No data returned."}</div>`;
    return;
  }

  const meta = data.meta || {};
  const mkt = data.market_overview || {};
  const risk = data.risk_assessment || {};
  const narrative = data.ai_commentary || "";

  const [badgeClass, badgeText] = riskBadge(risk.level);

  report.innerHTML = `
    <div class="row">
      <div>
        <div class="sectionTitle">
          <span>Overview</span>
          <span class="${badgeClass}">${badgeText}</span>
        </div>
        <div class="metricGrid">
          <div class="metric">
            <div class="metric__label">Symbol</div>
            <div class="metric__value">${meta.symbol || "—"}</div>
          </div>
          <div class="metric">
            <div class="metric__label">Timeframe</div>
            <div class="metric__value">${meta.timeframe || "—"}</div>
          </div>
          <div class="metric">
            <div class="metric__label">Price</div>
            <div class="metric__value">${fmtNum(mkt.price, 2)}</div>
          </div>
          <div class="metric">
            <div class="metric__label">RSI</div>
            <div class="metric__value">${fmtNum(mkt.rsi, 2)}</div>
          </div>
          <div class="metric">
            <div class="metric__label">MACD</div>
            <div class="metric__value">${fmtNum(mkt.macd, 2)}</div>
          </div>
          <div class="metric">
            <div class="metric__label">ATR</div>
            <div class="metric__value">${fmtNum(mkt.atr, 2)}</div>
          </div>
        </div>
      </div>

      <div>
        <div class="sectionTitle">
          <span>AI commentary</span>
          <span class="badge">Stop: ${risk.suggested_stop_loss || "—"}</span>
        </div>
        <div class="textBlock">${(narrative || "—").replace(/</g, "&lt;")}</div>
      </div>
    </div>
  `;
}

async function runAnalysis() {
  const btn = $("analyzeBtn");
  const symbol = $("symbol").value.trim().toUpperCase();
  const timeframe = $("timeframe").value;

  if (!symbol) {
    setStatus("err", "Missing symbol");
    renderReport({ error: "Please enter a symbol (e.g. ETHUSDT)." });
    return;
  }

  btn.disabled = true;
  btn.classList.add("btn--loading");
  setStatus("loading", "Analyzing…");

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, timeframe }),
    });
    const data = await res.json().catch(() => ({}));

    $("raw").textContent = JSON.stringify(data, null, 2);
    renderReport(data);

    if (res.ok && !data.error) setStatus("ok", "Done");
    else setStatus("err", `Error (${res.status})`);
  } catch (e) {
    $("raw").textContent = JSON.stringify({ error: "Network error", details: String(e) }, null, 2);
    renderReport({ error: "Network error", details: String(e) });
    setStatus("err", "Network error");
  } finally {
    btn.disabled = false;
    btn.classList.remove("btn--loading");
  }
}

document.addEventListener("click", (e) => {
  const chip = e.target.closest?.(".chip");
  if (chip && chip.dataset.symbol) {
    $("symbol").value = chip.dataset.symbol;
    $("symbol").focus();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  $("analyzeBtn").addEventListener("click", runAnalysis);
  $("symbol").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runAnalysis();
  });
});



