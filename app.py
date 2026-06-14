import streamlit as st
import pandas as pd
import plotly.graph_objects as go

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except Exception:
    YFINANCE_AVAILABLE = False

st.set_page_config(page_title="Financial Statement Analyser", layout="wide")

st.markdown("""
<style>
    .main { background-color: #ffffff; }
    .block-container { padding-top: 1.8rem; padding-bottom: 1.8rem; }
    .flag-card {
        background: #fffbf0; border-left: 3px solid #c8a400;
        padding: 0.55rem 1rem; margin: 0.25rem 0; font-size: 0.86rem; color: #333;
    }
    .ok-card {
        background: #f4faf5; border-left: 3px solid #3a7d44;
        padding: 0.55rem 1rem; margin: 0.25rem 0; font-size: 0.86rem; color: #333;
    }
    .critical-card {
        background: #fff5f5; border-left: 3px solid #c0392b;
        padding: 0.55rem 1rem; margin: 0.25rem 0; font-size: 0.86rem; color: #333;
    }
    .section-title {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
        text-transform: uppercase; color: #888; margin: 1.4rem 0 0.5rem 0;
        border-bottom: 1px solid #e8e8e8; padding-bottom: 0.3rem;
    }
    .note {
        font-size: 0.8rem; color: #777; margin-top: 0.2rem;
    }
    h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
    .verdict { background:#fafafa; padding:0.8rem 1.1rem; margin:0.4rem 0 0.6rem; border-radius:2px; }
    .verdict-badge { color:#fff; font-weight:700; font-size:0.8rem; padding:0.15rem 0.6rem;
        border-radius:3px; letter-spacing:0.03em; }
    .verdict-score { color:#555; font-size:0.82rem; margin-left:0.7rem; }
    .verdict-note { color:#333; font-size:0.86rem; margin-top:0.45rem; line-height:1.45; }
    .cat { background:#fff; border:1px solid #ececec; padding:0.5rem 0.7rem; margin:0.15rem 0; border-radius:2px; }
    .cat-name { font-size:0.66rem; text-transform:uppercase; letter-spacing:0.08em; color:#999; }
    .cat-status { font-size:0.95rem; font-weight:600; color:#1a1a1a; margin:0.1rem 0; }
    .cat-note { font-size:0.74rem; color:#777; }
    .flag-action { font-size:0.78rem; color:#5a5a5a; margin-top:0.3rem; font-style:italic; }
</style>
""", unsafe_allow_html=True)

NAVY, BLUE, GREEN = "#1F3864", "#2E75B6", "#4a7c59"

LINE_ITEMS = [
    "Revenue", "COGS", "Gross_Profit", "EBIT", "Interest_Expense", "Net_Income",
    "Total_Assets", "Current_Assets", "Current_Liabilities", "Total_Liabilities",
    "Equity", "Inventory", "Accounts_Receivable", "CFO",
]

# ── Built-in illustrative company ────────────────────────────────────────────────
# Synthetic figures (USD) for a fictional mid-cap industrial firm. Deliberately
# constructed to surface several analytical-review flags so the engine can be
# demonstrated without depending on a live data feed.
SAMPLE_ROWS = [
    {"Period": "2025", "Revenue": 1_250_000_000, "COGS": 900_000_000, "Gross_Profit": 350_000_000,
     "EBIT": 70_000_000, "Interest_Expense": 40_000_000, "Net_Income": 22_000_000,
     "Total_Assets": 1_400_000_000, "Current_Assets": 510_000_000, "Current_Liabilities": 400_000_000,
     "Total_Liabilities": 950_000_000, "Equity": 450_000_000, "Inventory": 195_000_000,
     "Accounts_Receivable": 210_000_000, "CFO": 14_000_000},
    {"Period": "2024", "Revenue": 1_120_000_000, "COGS": 780_000_000, "Gross_Profit": 340_000_000,
     "EBIT": 88_000_000, "Interest_Expense": 35_000_000, "Net_Income": 40_000_000,
     "Total_Assets": 1_300_000_000, "Current_Assets": 500_000_000, "Current_Liabilities": 360_000_000,
     "Total_Liabilities": 870_000_000, "Equity": 430_000_000, "Inventory": 150_000_000,
     "Accounts_Receivable": 165_000_000, "CFO": 46_000_000},
    {"Period": "2023", "Revenue": 1_000_000_000, "COGS": 680_000_000, "Gross_Profit": 320_000_000,
     "EBIT": 85_000_000, "Interest_Expense": 30_000_000, "Net_Income": 41_000_000,
     "Total_Assets": 1_200_000_000, "Current_Assets": 480_000_000, "Current_Liabilities": 330_000_000,
     "Total_Liabilities": 800_000_000, "Equity": 400_000_000, "Inventory": 140_000_000,
     "Accounts_Receivable": 150_000_000, "CFO": 60_000_000},
]

def sample_company():
    df = pd.DataFrame(SAMPLE_ROWS).sort_values("Period", ascending=False).reset_index(drop=True)
    return {"df": df, "name": "Northwind Industrial Co. (illustrative)",
            "sector": "Industrials", "currency": "USD"}

# ── Peer-comparison reference set (fixed snapshot, sourced StockAnalysis.com) ─────
PEERS = [
    {"Ticker": "NVDA",  "Sector": "Technology",  "Revenue_Growth": 114.0, "Net_Margin": 55.0, "ROE": 123.0, "Debt_Equity": 0.40, "PE": 47.7, "FCF_Yield": 1.2},
    {"Ticker": "MSFT",  "Sector": "Technology",  "Revenue_Growth": 16.0,  "Net_Margin": 39.0, "ROE": 34.4,  "Debt_Equity": 0.32, "PE": 25.1, "FCF_Yield": 2.6},
    {"Ticker": "META",  "Sector": "Technology",  "Revenue_Growth": 22.0,  "Net_Margin": 37.9, "ROE": 36.0,  "Debt_Equity": 0.10, "PE": 27.2, "FCF_Yield": 3.3},
    {"Ticker": "GOOGL", "Sector": "Technology",  "Revenue_Growth": 14.0,  "Net_Margin": 27.8, "ROE": 32.0,  "Debt_Equity": 0.08, "PE": 28.8, "FCF_Yield": 4.5},
    {"Ticker": "AAPL",  "Sector": "Technology",  "Revenue_Growth": 4.0,   "Net_Margin": 27.0, "ROE": 160.0, "Debt_Equity": 1.50, "PE": 34.5, "FCF_Yield": 3.4},
    {"Ticker": "AMZN",  "Sector": "Consumer",    "Revenue_Growth": 11.0,  "Net_Margin": 9.3,  "ROE": 23.0,  "Debt_Equity": 0.60, "PE": 29.1, "FCF_Yield": 3.0},
    {"Ticker": "JPM",   "Sector": "Financials",  "Revenue_Growth": 1.0,   "Net_Margin": 33.9, "ROE": 16.1,  "Debt_Equity": 1.38, "PE": 14.2, "FCF_Yield": 2.1},
    {"Ticker": "JNJ",   "Sector": "Healthcare",  "Revenue_Growth": 4.0,   "Net_Margin": 28.4, "ROE": 35.0,  "Debt_Equity": 0.60, "PE": 16.5, "FCF_Yield": 3.2},
    {"Ticker": "KO",    "Sector": "Consumer",    "Revenue_Growth": 2.0,   "Net_Margin": 27.3, "ROE": 42.4,  "Debt_Equity": 1.45, "PE": 28.0, "FCF_Yield": 1.4},
    {"Ticker": "XOM",   "Sector": "Energy",      "Revenue_Growth": -4.0,  "Net_Margin": 8.9,  "ROE": 11.1,  "Debt_Equity": 0.19, "PE": 14.5, "FCF_Yield": 3.5},
]

# ── yfinance loader ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_ticker(ticker: str):
    if not YFINANCE_AVAILABLE:
        return None, "Live data is unavailable in this environment. Use the sample company instead."
    try:
        t = yf.Ticker(ticker.upper().strip())
        info = t.info or {}
        name = info.get("longName") or info.get("shortName") or ticker.upper()
        sector = info.get("sector", "N/A")
        currency = info.get("currency", "USD")

        inc, bal, cf = t.income_stmt, t.balance_sheet, t.cash_flow
    except Exception:
        return None, ("Yahoo Finance did not return data right now (it rate-limits frequently, "
                      "especially from cloud servers). Try again in a moment, or use the sample company.")

    if inc is None or inc.empty:
        return None, f"No financial data found for '{ticker}'. Check the ticker symbol."

    def get_row(df, *keys):
        if df is None or df.empty:
            return None
        for k in keys:
            matches = [i for i in df.index if k.lower() in i.lower()]
            if matches:
                return df.loc[matches[0]]
        return None

    revenue      = get_row(inc, "Total Revenue")
    cogs         = get_row(inc, "Cost Of Revenue", "Cost of Goods")
    gross_profit = get_row(inc, "Gross Profit")
    ebit         = get_row(inc, "EBIT", "Operating Income")
    interest_exp = get_row(inc, "Interest Expense")
    net_income   = get_row(inc, "Net Income")

    cur_assets   = get_row(bal, "Current Assets")
    cur_liab     = get_row(bal, "Current Liabilities")
    tot_assets   = get_row(bal, "Total Assets")
    tot_liab     = get_row(bal, "Total Liabilities Net Minority Interest", "Total Liabilities")
    equity       = get_row(bal, "Stockholders Equity", "Common Stock Equity")
    inventory    = get_row(bal, "Inventory")
    receivables  = get_row(bal, "Receivables", "Accounts Receivable")

    cfo          = get_row(cf, "Operating Cash Flow", "Cash From Operations")

    required = [revenue, gross_profit, ebit, net_income, cur_assets, cur_liab,
                tot_assets, tot_liab, equity, cfo]
    if any(r is None for r in required):
        return None, f"Could not retrieve complete financials for '{ticker}'. Some line items may be unavailable for this company."

    # Yahoo can return different sets of years per statement — use only periods
    # present across all three so we never index a missing date.
    try:
        common = [c for c in inc.columns if c in bal.columns and c in cf.columns]
    except Exception:
        common = list(inc.columns)
    if not common:
        return None, (f"Financial periods for '{ticker}' don't align across the income statement, "
                      "balance sheet, and cash-flow statement, so the data can't be analysed reliably. "
                      "Try another ticker or use the sample company.")
    common = sorted(common, reverse=True)  # most recent first

    def val(series, col, default=0.0):
        if series is None:
            return default
        try:
            v = series.get(col, default)
        except Exception:
            return default
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return default
        try:
            return float(v)
        except Exception:
            return default

    try:
        rows = []
        for col in common:
            rows.append({
                "Period":              col.strftime("%Y"),
                "Revenue":             val(revenue, col),
                "COGS":                val(cogs, col),
                "Gross_Profit":        val(gross_profit, col),
                "EBIT":                val(ebit, col),
                "Interest_Expense":    abs(val(interest_exp, col, 0.0)),
                "Net_Income":          val(net_income, col),
                "Total_Assets":        val(tot_assets, col),
                "Current_Assets":      val(cur_assets, col),
                "Current_Liabilities": val(cur_liab, col),
                "Total_Liabilities":   val(tot_liab, col),
                "Equity":              val(equity, col) or 1.0,
                "Inventory":           val(inventory, col),
                "Accounts_Receivable": val(receivables, col),
                "CFO":                 val(cfo, col),
            })
        df = pd.DataFrame(rows)
        df = df[df["Revenue"] != 0].reset_index(drop=True)  # drop empty/incomplete periods
    except Exception:
        return None, f"Could not process the financials returned for '{ticker}'. Try another ticker or the sample company."

    if df.empty:
        return None, f"Could not retrieve usable financials for '{ticker}'."
    return {"df": df, "name": name, "sector": sector, "currency": currency}, None


# ── Ratio engine ───────────────────────────────────────────────────────────────
def compute_ratios(df):
    periods = df["Period"].tolist()
    r = pd.DataFrame(index=[
        "Gross Margin (%)","Net Margin (%)","EBIT Margin (%)",
        "Current Ratio","Quick Ratio","Debt-to-Equity",
        "ROA (%)","ROE (%)","Interest Coverage",
        "CFO / Net Income","Receivables Days","Inventory Days"
    ], columns=periods, dtype=float)
    for i, p in enumerate(periods):
        row = df.iloc[i]
        rev  = row["Revenue"]   if row["Revenue"]   != 0 else 1
        eq   = row["Equity"]    if row["Equity"]    != 0 else 1
        ta   = row["Total_Assets"] if row["Total_Assets"] != 0 else 1
        cl   = row["Current_Liabilities"] if row["Current_Liabilities"] != 0 else 1
        ni   = row["Net_Income"] if row["Net_Income"] != 0 else 1
        cogs = row["COGS"]      if row["COGS"]      != 0 else 1

        r.loc["Gross Margin (%)",   p] = row["Gross_Profit"] / rev * 100
        r.loc["Net Margin (%)",     p] = row["Net_Income"]   / rev * 100
        r.loc["EBIT Margin (%)",    p] = row["EBIT"]         / rev * 100
        r.loc["Current Ratio",      p] = row["Current_Assets"] / cl
        r.loc["Quick Ratio",        p] = (row["Current_Assets"] - row["Inventory"]) / cl
        r.loc["Debt-to-Equity",     p] = row["Total_Liabilities"] / eq
        r.loc["ROA (%)",            p] = row["Net_Income"] / ta * 100
        r.loc["ROE (%)",            p] = row["Net_Income"] / eq * 100
        r.loc["Interest Coverage",  p] = row["EBIT"] / row["Interest_Expense"] if row["Interest_Expense"] != 0 else 0
        r.loc["CFO / Net Income",   p] = row["CFO"] / ni
        r.loc["Receivables Days",   p] = row["Accounts_Receivable"] / rev * 365
        r.loc["Inventory Days",     p] = row["Inventory"] / cogs * 365
    return r

def red_flags(df, ratios):
    flags = []  # (severity, message, suggested_procedure)
    p = df["Period"].tolist()
    latest = p[0]
    ni_latest = df["Net_Income"].iloc[0]

    if len(df) >= 2:
        rev_g = (df["Revenue"].iloc[0] - df["Revenue"].iloc[-1]) / abs(df["Revenue"].iloc[-1]) * 100
        ni_g  = (df["Net_Income"].iloc[0] - df["Net_Income"].iloc[-1]) / abs(df["Net_Income"].iloc[-1]) * 100
        if rev_g > 0 and ni_g < -15:
            flags.append(("critical",
                f"Revenue grew {rev_g:.1f}% over the period while net income fell {abs(ni_g):.1f}%.",
                "Investigate margin compression: input-cost inflation, pricing pressure, or one-off charges."))

    if ni_latest <= 0:
        flags.append(("critical",
            f"Net loss reported in the most recent period ({latest}).",
            "Identify the drivers of the loss and assess whether going-concern indicators are present."))
    else:
        cfo_ni = float(ratios.loc["CFO / Net Income", latest])
        if cfo_ni < 0.75:
            flags.append(("critical",
                f"CFO / Net Income = {cfo_ni:.2f} — earnings are not well supported by operating cash flow.",
                "Test revenue recognition and cutoff; review accruals and working-capital movements."))

    if len(df) >= 2:
        cogs_pct = df["COGS"] / df["Revenue"].replace(0, 1)
        if cogs_pct.iloc[0] - cogs_pct.iloc[1] > 0.05:
            flags.append(("warning",
                f"COGS as a share of revenue rose {(cogs_pct.iloc[0]-cogs_pct.iloc[1])*100:.1f}pp year-over-year.",
                "Review input costs and product mix for sustained margin pressure."))

        rec_g  = (df["Accounts_Receivable"].iloc[0] - df["Accounts_Receivable"].iloc[1]) / (abs(df["Accounts_Receivable"].iloc[1]) or 1)
        rev_g1 = (df["Revenue"].iloc[0] - df["Revenue"].iloc[1]) / (abs(df["Revenue"].iloc[1]) or 1)
        if rec_g > rev_g1 + 0.05:
            flags.append(("warning",
                f"Receivables grew {rec_g*100:.1f}% against revenue growth of {rev_g1*100:.1f}%.",
                "Test collectability and revenue cutoff; review the allowance for doubtful accounts."))

        inv_g = (df["Inventory"].iloc[0] - df["Inventory"].iloc[1]) / (abs(df["Inventory"].iloc[1]) or 1)
        if inv_g > 0.25 and df["Inventory"].iloc[0] > 0:
            flags.append(("warning",
                f"Inventory rose {inv_g*100:.1f}% year-over-year.",
                "Assess obsolescence and net realisable value; review inventory turnover."))

    cr = float(ratios.loc["Current Ratio", latest])
    if cr < 1.0:
        flags.append(("critical",
            f"Current ratio = {cr:.2f} — current liabilities exceed current assets.",
            "Review short-term funding, covenant compliance, and available liquidity headroom."))
    elif cr < 1.3:
        flags.append(("warning",
            f"Current ratio of {cr:.2f} is below a comfortable threshold.",
            "Monitor working-capital management and the schedule of near-term obligations."))

    dte = float(ratios.loc["Debt-to-Equity", latest])
    if dte < 0:
        flags.append(("critical",
            "Negative shareholders' equity — total liabilities exceed total assets.",
            "Assess solvency and going-concern; review the accumulated deficit and any covenant breaches."))
    elif dte > 2.0:
        flags.append(("warning",
            f"Debt-to-equity = {dte:.2f}.",
            "Review debt covenants, the maturity profile, and refinancing exposure."))

    ic = float(ratios.loc["Interest Coverage", latest])
    if 0 < ic < 2.0:
        flags.append(("critical",
            f"Interest coverage = {ic:.2f}x — a thin margin over interest obligations.",
            "Stress-test debt servicing under lower EBIT; consider going-concern implications."))

    if not flags:
        flags.append(("ok",
            "No significant analytical-review flags identified across the review period.",
            "Standard substantive procedures appropriate; no elevated-risk areas indicated."))
    return flags

def render_flags(flags):
    for item in flags:
        severity, msg = item[0], item[1]
        action = item[2] if len(item) > 2 else ""
        css   = {"critical": "critical-card", "warning": "flag-card", "ok": "ok-card"}[severity]
        label = {"critical": "High", "warning": "Medium", "ok": "Clear"}[severity]
        action_html = f"<div class='flag-action'>Suggested procedure: {action}</div>" if action else ""
        st.markdown(f"<div class='{css}'><strong>{label}</strong> &mdash; {msg}{action_html}</div>", unsafe_allow_html=True)

def assess_health(df, ratios):
    latest = df["Period"].iloc[0]
    ni = df["Net_Income"].iloc[0]
    def g(name): return float(ratios.loc[name, latest])

    cats = {}  # name -> (score 0-100, status, note)

    nm = g("Net Margin (%)")
    if ni <= 0:        cats["Profitability"] = (20, "Weak", f"Loss-making; net margin {nm:.1f}%.")
    elif nm >= 12:     cats["Profitability"] = (92, "Strong", f"Net margin {nm:.1f}%.")
    elif nm >= 5:      cats["Profitability"] = (70, "Adequate", f"Net margin {nm:.1f}%.")
    else:              cats["Profitability"] = (45, "Thin", f"Net margin {nm:.1f}%.")

    cr = g("Current Ratio")
    if cr >= 1.5:      cats["Liquidity"] = (90, "Strong", f"Current ratio {cr:.2f}x.")
    elif cr >= 1.2:    cats["Liquidity"] = (72, "Adequate", f"Current ratio {cr:.2f}x.")
    elif cr >= 1.0:    cats["Liquidity"] = (50, "Tight", f"Current ratio {cr:.2f}x.")
    else:              cats["Liquidity"] = (25, "Weak", f"Current ratio {cr:.2f}x (below 1.0).")

    dte = g("Debt-to-Equity")
    ic  = g("Interest Coverage")
    lev = 100
    notes = []
    if dte < 0:
        lev = 10; notes.append("negative equity")
    else:
        if dte > 2:   lev -= 35
        elif dte > 1: lev -= 15
        notes.append(f"D/E {dte:.2f}")
    if ic > 0:
        if ic < 2:    lev -= 35
        elif ic < 4:  lev -= 12
        notes.append(f"interest cover {ic:.2f}x")
    lev = max(lev, 5)
    lev_status = "Strong" if lev >= 80 else "Moderate" if lev >= 55 else "Stretched" if lev >= 35 else "Weak"
    cats["Leverage"] = (lev, lev_status, "; ".join(notes) + ".")

    if ni <= 0:
        cats["Earnings Quality"] = (30, "n/a", "Not meaningful while loss-making.")
    else:
        cq = g("CFO / Net Income")
        if cq >= 1.0:   cats["Earnings Quality"] = (90, "Strong", f"CFO/NI {cq:.2f}x.")
        elif cq >= 0.8: cats["Earnings Quality"] = (68, "Adequate", f"CFO/NI {cq:.2f}x.")
        elif cq >= 0.6: cats["Earnings Quality"] = (45, "Weak", f"CFO/NI {cq:.2f}x.")
        else:           cats["Earnings Quality"] = (25, "Poor", f"CFO/NI {cq:.2f}x.")

    weights = {"Profitability": 0.30, "Liquidity": 0.25, "Leverage": 0.25, "Earnings Quality": 0.20}
    score = sum(cats[k][0] * weights[k] for k in cats)
    if score >= 78:    rating, color = "Healthy", "#3a7d44"
    elif score >= 62:  rating, color = "Stable", "#2E75B6"
    elif score >= 45:  rating, color = "Watch", "#c8a400"
    else:              rating, color = "At Risk", "#c0392b"

    strengths = [k for k in cats if cats[k][0] >= 75]
    concerns  = [k for k in cats if cats[k][0] < 50]
    parts = []
    if strengths: parts.append(f"Strengths: {', '.join(s.lower() for s in strengths)}.")
    if concerns:  parts.append(f"Areas of concern: {', '.join(c.lower() for c in concerns)}.")
    if not parts: parts.append("A broadly balanced profile with no category standing out either way.")
    return {"score": score, "rating": rating, "color": color, "cats": cats, "narrative": " ".join(parts)}

def render_assessment(health):
    st.markdown(
        f"<div class='verdict' style='border-left:5px solid {health['color']};'>"
        f"<span class='verdict-badge' style='background:{health['color']};'>{health['rating']}</span>"
        f"<span class='verdict-score'>Composite score {health['score']:.0f} / 100</span>"
        f"<div class='verdict-note'>{health['narrative']}</div>"
        f"</div>", unsafe_allow_html=True)
    cols = st.columns(len(health["cats"]))
    for col, (name, vals) in zip(cols, health["cats"].items()):
        sc, status, note = vals
        col.markdown(
            f"<div class='cat'><div class='cat-name'>{name}</div>"
            f"<div class='cat-status'>{status}</div>"
            f"<div class='cat-note'>{note}</div></div>", unsafe_allow_html=True)

def fmt_large(val, currency="USD"):
    sym = "$" if currency == "USD" else ""
    if abs(val) >= 1e12: return f"{sym}{val/1e12:.2f}T"
    if abs(val) >= 1e9:  return f"{sym}{val/1e9:.2f}B"
    if abs(val) >= 1e6:  return f"{sym}{val/1e6:.2f}M"
    return f"{sym}{val:,.0f}"


# ── Analysis renderer (shared by sample + live) ──────────────────────────────────
def render_analysis(result, source_note):
    df       = result["df"]
    name     = result["name"]
    sector   = result["sector"]
    currency = result["currency"]
    ratios   = compute_ratios(df)
    periods  = df["Period"].tolist()
    latest   = periods[0]

    st.markdown("---")
    st.markdown(f"<div class='section-title'>{name} &nbsp;&middot;&nbsp; {sector}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Overall Assessment</div>", unsafe_allow_html=True)
    render_assessment(assess_health(df, ratios))

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Revenue",       fmt_large(df["Revenue"].iloc[0], currency))
    k2.metric("Net Income",    fmt_large(df["Net_Income"].iloc[0], currency))
    k3.metric("Net Margin",    f"{ratios.loc['Net Margin (%)', latest]:.1f}%")
    k4.metric("Current Ratio", f"{ratios.loc['Current Ratio', latest]:.2f}x")
    k5.metric("CFO / Net Inc", f"{ratios.loc['CFO / Net Income', latest]:.2f}x")

    st.markdown("<div class='section-title'>Risk Flags (ISA 520 analytical review)</div>", unsafe_allow_html=True)
    render_flags(red_flags(df, ratios))

    st.markdown("<div class='section-title'>Trends</div>", unsafe_allow_html=True)
    x = periods[::-1]

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for label, col, color in [("Revenue","Revenue",NAVY),("Gross Profit","Gross_Profit",BLUE),("Net Income","Net_Income",GREEN)]:
            fig.add_trace(go.Bar(x=x, y=[df.loc[df["Period"]==p, col].values[0]/1e9 for p in x], name=label, marker_color=color))
        fig.update_layout(barmode="group", title="Revenue & Profitability ($B)", height=300,
                          paper_bgcolor="white", plot_bgcolor="white", font=dict(family="Arial", size=11, color="#333"),
                          legend=dict(orientation="h", y=-0.28), margin=dict(t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure()
        for m, color in [("Gross Margin (%)", NAVY), ("Net Margin (%)", BLUE), ("EBIT Margin (%)", GREEN)]:
            fig2.add_trace(go.Scatter(x=x, y=[float(ratios.loc[m, p]) for p in x], mode="lines+markers", name=m, line=dict(color=color, width=2)))
        fig2.update_layout(title="Margin Trends", height=300, paper_bgcolor="white", plot_bgcolor="white",
                           font=dict(family="Arial", size=11, color="#333"), yaxis=dict(ticksuffix="%"),
                           legend=dict(orientation="h", y=-0.28), margin=dict(t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = go.Figure()
        for m, color, dash in [("Current Ratio", NAVY, "solid"), ("Quick Ratio", BLUE, "dash")]:
            fig3.add_trace(go.Scatter(x=x, y=[float(ratios.loc[m, p]) for p in x], mode="lines+markers", name=m, line=dict(color=color, width=2, dash=dash)))
        fig3.add_hline(y=1.0, line_dash="dot", line_color="#c0392b", annotation_text="1.0x", annotation_font_size=10)
        fig3.update_layout(title="Liquidity", height=300, paper_bgcolor="white", plot_bgcolor="white",
                           font=dict(family="Arial", size=11, color="#333"), legend=dict(orientation="h", y=-0.28), margin=dict(t=40, b=10))
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=x, y=[df.loc[df["Period"]==p,"CFO"].values[0]/1e9 for p in x], mode="lines+markers", name="Operating Cash Flow", line=dict(color=NAVY, width=2)))
        fig4.add_trace(go.Scatter(x=x, y=[df.loc[df["Period"]==p,"Net_Income"].values[0]/1e9 for p in x], mode="lines+markers", name="Net Income", line=dict(color="#c0392b", width=2, dash="dash")))
        fig4.update_layout(title="Earnings Quality (CFO vs Net Income, $B)", height=300, paper_bgcolor="white", plot_bgcolor="white",
                           font=dict(family="Arial", size=11, color="#333"), legend=dict(orientation="h", y=-0.28), margin=dict(t=40, b=10))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-title'>Ratio Summary</div>", unsafe_allow_html=True)
    formatted = pd.DataFrame(index=ratios.index, columns=ratios.columns)
    for idx in ratios.index:
        for col in ratios.columns:
            v = float(ratios.loc[idx, col])
            if "%" in idx:      formatted.loc[idx, col] = f"{v:.1f}%"
            elif "Days" in idx: formatted.loc[idx, col] = f"{v:.0f} days"
            else:               formatted.loc[idx, col] = f"{v:.2f}x"
    st.dataframe(formatted, use_container_width=True)
    st.markdown(f"<div class='note'>{source_note}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("## Financial Statement Analyser")
st.markdown("<div class='note'>Automated analytical review of multi-year financial statements: ratio analysis, "
            "trend visualisation, and risk-flag detection aligned with ISA 520 analytical procedures.</div>",
            unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Statement Analysis", "Peer Comparison"])

# ── TAB 1 ────────────────────────────────────────────────────────────────────────
with tab1:
    source = st.radio("Data source", ["Sample company (illustrative)", "Live company (Yahoo Finance)"],
                      horizontal=True, label_visibility="collapsed")

    if source.startswith("Sample"):
        st.caption("A built-in illustrative company with figures constructed to demonstrate the risk-flag engine. "
                   "Switch to 'Live company' to analyse any listed ticker.")
        render_analysis(sample_company(),
                        "Illustrative dataset — synthetic figures for demonstration only.")
    else:
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            ticker_input = st.text_input("Ticker", value="", label_visibility="collapsed",
                                         placeholder="Enter a ticker, e.g. AAPL, MSFT, JPM")
        with col_btn:
            load = st.button("Load", use_container_width=True)

        if load and ticker_input.strip():
            with st.spinner(f"Loading {ticker_input.upper()}..."):
                result, error = load_ticker(ticker_input)
            if error:
                st.warning(error)
            else:
                render_analysis(result,
                                "Source: Yahoo Finance via yfinance. Annual financials, retrieved on load.")
        elif load:
            st.info("Enter a ticker symbol first.")
        else:
            st.info("Enter a ticker and press Load. If Yahoo Finance is unavailable, use the sample company above.")

# ── TAB 2 ────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("Comparative analysis of large-cap companies across core profitability, leverage, and valuation "
                "metrics. Fixed reference snapshot.")

    sdf = pd.DataFrame(PEERS)
    all_sectors = sorted(sdf["Sector"].unique().tolist())

    with st.expander("Filters", expanded=True):
        selected_sectors = st.multiselect("Sectors", options=all_sectors, default=all_sectors)
        f1, f2, f3 = st.columns(3)
        min_rev = f1.slider("Min Revenue Growth (%)", -20.0, 120.0,  0.0, 1.0)
        min_nm  = f2.slider("Min Net Margin (%)",       0.0,  60.0,  5.0, 0.5)
        max_pe  = f3.slider("Max P/E",                  5.0, 120.0, 60.0, 1.0)
        f4, f5, f6 = st.columns(3)
        min_roe = f4.slider("Min ROE (%)",              0.0, 100.0, 10.0, 1.0)
        max_de  = f5.slider("Max Debt / Equity",        0.0,   3.0,  2.0, 0.05)
        min_fcf = f6.slider("Min FCF Yield (%)",        0.0,   6.0,  1.0, 0.1)

    filtered = sdf[
        (sdf["Sector"].isin(selected_sectors)) &
        (sdf["Revenue_Growth"] >= min_rev) & (sdf["Net_Margin"] >= min_nm) &
        (sdf["PE"] <= max_pe) & (sdf["ROE"] >= min_roe) &
        (sdf["Debt_Equity"] <= max_de) & (sdf["FCF_Yield"] >= min_fcf)
    ].reset_index(drop=True)

    st.markdown(f"<div class='section-title'>{len(filtered)} company(ies) match the current filters</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No companies match the current criteria.")
    else:
        rename = {"Revenue_Growth": "Rev Growth %", "Net_Margin": "Net Margin %", "ROE": "ROE %",
                  "Debt_Equity": "D/E", "PE": "P/E", "FCF_Yield": "FCF Yield %"}
        display_cols = ["Ticker", "Sector", "Revenue_Growth", "Net_Margin", "ROE", "Debt_Equity", "PE", "FCF_Yield"]
        st.dataframe(filtered[display_cols].rename(columns=rename), use_container_width=True, hide_index=True)

        sector_colors = {"Technology": NAVY, "Consumer": BLUE, "Financials": "#7f8c8d", "Healthcare": GREEN, "Energy": "#c0392b"}
        fig5 = go.Figure()
        for sector in filtered["Sector"].unique():
            sub = filtered[filtered["Sector"] == sector]
            fig5.add_trace(go.Scatter(
                x=sub["PE"], y=sub["Net_Margin"], mode="markers+text", text=sub["Ticker"],
                textposition="top center", name=sector,
                marker=dict(size=sub["Revenue_Growth"].clip(lower=2, upper=60),
                            color=sector_colors.get(sector, "#888"), line=dict(width=1, color="#aaa"), opacity=0.85)
            ))
        fig5.update_layout(title="P/E vs Net Margin  —  bubble size: revenue growth  |  colour: sector",
                           xaxis_title="P/E Ratio", yaxis_title="Net Margin (%)", height=440,
                           paper_bgcolor="white", plot_bgcolor="white",
                           font=dict(family="Arial", size=11, color="#333"), legend=dict(title="Sector"), margin=dict(t=50))
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div class='note'>Reference snapshot: figures as of Q1 2026 (StockAnalysis.com). "
                "For comparative illustration, not investment advice.</div>", unsafe_allow_html=True)
