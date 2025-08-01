# Magic Formula & Early Momentum for B3 (Streamlit App)

This project provides a powerful, user-friendly tool to identify undervalued Brazilian stocks likely to start moving higher. It combines:

- **Value:** Joel Greenblatt’s Magic Formula (Earnings Yield + 0.33 × Return on Capital)
- **Momentum:** Early-trend detection using price returns and breakout logic

## Features

- **Automated Data**: Gets all required fundamentals and prices via [EODHD](https://eodhd.com) APIs (paid/free, subject to your subscription)
- **Exchange Rate Integration:** Converts fundamentals using USD/BRL via Yahoo Finance
- **Early Momentum Detection:**  
    - 6m Momentum (return from 7M to 1M ago)
    - 1m Momentum (return over the last 1M)
    - Breakscore (is today a new 6M high?)
- **Composite Scoring:** Sorts the universe by value and momentum signals (“Magic Rank Momentum”)
- **Multilingual UI:** English and Portuguese interface
- **Simple Deployment:** One-click deploy via [Streamlit Cloud](https://streamlit.io/cloud) or local run

## Requirements

- Python 3.8+
- streamlit, pandas, requests, yfinance
- EODHD API key (add to Streamlit secrets as `API_TOKEN`)

## Usage

1. Clone this repo
2. Set your EODHD API token under `.streamlit/secrets.toml`
3. Install requirements:  
   `pip install -r requirements.txt`
4. Run:  
   `streamlit run magic_formula_momentum.py`
5. Interact via the browser UI

## Example Output

| Ticker   | Report Date | Earnings Yield | Return on Capital | 6m Momentum | 1m Momentum | Breakscore | Weighted Score | Magic Rank Momentum | Rank |
|----------|-------------|---------------|-------------------|-------------|-------------|------------|---------------|---------------------|------|
| PETR4.SA | 2025-06-30  | 12.5%         | 18.2%             | 14.2%       | 3.1%        | 1          | 18.51         | 28.41               | 1    |

## License

MIT or your choice

## Authors

- Your Name

---

If you use or extend this project, please cite the original Magic Formula research and the EODHD API.
