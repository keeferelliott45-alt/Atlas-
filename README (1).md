# Financial Statement Analyser

An interactive financial analysis tool that performs automated analytical review on multi-year
financial statements, built with Python and Streamlit.

## Overview

The tool automates the kind of analytical review used in audit and financial analysis: it computes
a panel of ratios across profitability, liquidity, leverage, and earnings quality, visualises their
trend over the reporting period, and raises risk flags where the figures deviate from expected
relationships. The flag logic is aligned with analytical procedures under **ISA 520**.

## Features

- **Statement Analysis** — pulls live annual financials for any listed company via Yahoo Finance,
  computes 12 ratios, and renders trend charts for revenue/profitability, margins, liquidity, and
  cash-flow quality.
- **Risk-flag engine** — automatically surfaces analytical-review anomalies: margin compression,
  weak earnings quality (CFO vs net income), receivables growing ahead of revenue, inventory build,
  thin interest coverage, and short-term liquidity stress. Flags are graded High / Medium / Clear.
- **Built-in sample company** — a synthetic illustrative dataset, engineered to trigger the flag
  engine, so the tool can be demonstrated instantly without depending on a live data feed.
- **Peer Comparison** — a filterable comparison of large-cap companies across growth, margin,
  return, leverage, and valuation metrics, with a P/E-vs-margin scatter view.

## Risk-flag logic (ISA 520 analytical procedures)

| Flag | Analytical implication |
|---|---|
| Revenue up while net income falls | Margin compression — investigate cost base |
| CFO / Net Income < 0.75 | Accrual-heavy earnings — review revenue recognition |
| Receivables growing faster than revenue | Collectability or premature recognition risk |
| Inventory up > 25% YoY | Obsolescence or overstatement risk |
| Interest coverage < 2.0x | Going-concern consideration |
| Current ratio < 1.0 | Short-term liquidity risk |

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `localhost:8501`. It loads the sample company by default; switch the
data source to "Live company" to analyse any ticker.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (already done if you're reading this on GitHub).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select this repository and branch, and set the main file path to `app.py`.
4. Click **Deploy**. The app will build using `requirements.txt` and be available at a public URL
   you can link from your resume or portfolio.

## Notes

- Live data is retrieved from Yahoo Finance via the `yfinance` library and cached for one hour.
  Yahoo rate-limits requests, so live lookups can occasionally be unavailable; the built-in sample
  company is always available as a fallback.
- The sample company and the peer-comparison set are illustrative and not investment advice.

## Author

Keefer Elliott — B.Sc. Computational Business Analytics, Frankfurt School of Finance & Management.
