import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import datetime
import time

API_TOKEN = st.secrets["API_TOKEN"]

TICKERS = [
    # ... paste your full ticker list here ...
]

LANG_TEXT = {
    # ... paste the full LANG_TEXT dictionary as in your script ...
}

if 'error_msgs' not in st.session_state:
    st.session_state.error_msgs = []
if 'dismissed_errors' not in st.session_state:
    st.session_state.dismissed_errors = set()

@st.cache_data(ttl=3600)
def get_usd_to_brl_rate():
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
        st.error("Could not fetch USD/BRL exchange rate.")
        return None
    except Exception as e:
        st.error(f"yfinance error: {e}")
        return None

def get_financial_data(ticker):
    url = f"https://eodhd.com/api/fundamentals/{ticker}?api_token={API_TOKEN}&fmt=json"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        income_stmt_q = data.get('Financials', {}).get('Income_Statement', {}).get('quarterly', {})
        balance_sheet_q = data.get('Financials', {}).get('Balance_Sheet', {}).get('quarterly', {})
        valuation = data.get('Valuation', {})
        if not income_stmt_q or not balance_sheet_q:
            return [], f"No quarterly data for {ticker}"

        results = []
        debug_msgs = []
        common_dates = sorted(set(income_stmt_q.keys()) & set(balance_sheet_q.keys()), reverse=True)
        for date in common_dates:
            income_report = income_stmt_q.get(date, {})
            balance_sheet_report = balance_sheet_q.get(date, {})
            ebit = income_report.get('ebit')
            total_debt = balance_sheet_report.get('shortLongTermDebtTotal')
            total_equity = balance_sheet_report.get('totalStockholderEquity')
            enterprise_value = valuation.get('EnterpriseValue', 0)

            def to_float(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return None

            ebit = to_float(ebit)
            total_debt = to_float(total_debt)
            total_equity = to_float(total_equity)
            enterprise_value = to_float(enterprise_value)

            missing = []
            if ebit is None:
                missing.append("ebit")
            if total_debt is None and total_equity is None:
                missing.append("debt+equity")
            if enterprise_value is None:
                missing.append("enterprise_value")

            if missing:
                debug_msgs.append(f"{ticker} {date}: missing fields - {', '.join(missing)}")
                continue

            results.append({
                "report_date": date,
                "ebit_usd": ebit,
                "enterprise_value_brl": enterprise_value,
                "total_debt_brl": total_debt if total_debt is not None else 0,
                "total_equity_brl": total_equity if total_equity is not None else 0,
            })

        if not results:
            return [], "; ".join(debug_msgs) if debug_msgs else "No valid quarterly data found"
        return results, None
    except Exception as e:
        return [], f"Error: {str(e)}"

def get_eod_prices(ticker, api_token, start_date, end_date):
    url = f"https://eodhd.com/api/eod/{ticker}?api_token={api_token}&from={start_date}&to={end_date}&fmt=json"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 150:  # at least 7+ months of data
            return None
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception:
        return None

def get_6m_momentum(df):
    days_per_month = 21
    if df is None or len(df) < 8 * days_per_month:
        return None
    # 6m skip 1 = (close_1m_ago - close_7m_ago) / close_7m_ago
    close_7m_ago = df['close'].iloc[-(7 * days_per_month)]
    close_1m_ago = df['close'].iloc[-(1 * days_per_month)]
    return (close_1m_ago - close_7m_ago) / close_7m_ago * 100

def get_1m_momentum(df):
    days_per_month = 21
    if df is None or len(df) < 2 * days_per_month:
        return None
    close_now = df['close'].iloc[-1]
    close_1m_ago = df['close'].iloc[-(1 * days_per_month)]
    return (close_now - close_1m_ago) / close_1m_ago * 100

def get_breakscore(df):
    if df is None or len(df) < 127:
        return 0
    last_126 = df['close'].iloc[-126:-1]  # last 6m, excluding today
    today_close = df['close'].iloc[-1]
    return int(today_close > last_126.max())

st.set_page_config(layout="wide")

with st.sidebar:
    lang = st.radio("Language / Idioma", options=["en", "pt"], format_func=lambda x: "English" if x == "en" else "Português")
    if st.session_state.error_msgs:
        to_remove = []
        for i, msg in enumerate(st.session_state.error_msgs):
            if msg in st.session_state.dismissed_errors:
                continue
            cols = st.columns([0.93, 0.07])
            with cols[0]:
                st.warning(msg)
            with cols[1]:
                close_button = st.button("🗙", key=f"close_{i}", help="Dismiss", use_container_width=True)
                if close_button:
                    st.session_state.dismissed_errors.add(msg)
                    to_remove.append(msg)
        for msg in to_remove:
            st.session_state.error_msgs.remove(msg)

st.title(LANG_TEXT["title"][lang])
st.markdown(f"... {LANG_TEXT['description'][lang]}", unsafe_allow_html=True)
st.markdown(LANG_TEXT["formula"][lang])

if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'all_dates' not in st.session_state:
    st.session_state.all_dates = []
if 'fetch_log' not in st.session_state:
    st.session_state.fetch_log = []

if st.button(LANG_TEXT["run_button"][lang]):
    st.session_state.error_msgs = []
    st.session_state.dismissed_errors = set()
    st.session_state.fetch_log = []
    rate = get_usd_to_brl_rate()
    if not rate:
        st.error("Cannot proceed without the BRL/USD exchange rate.")
    else:
        all_results = []
        all_dates = set()
        failed = []
        neg = []
        ok = []
        progress_bar = st.progress(0, text="Fetching data for tickers...")
        for i, ticker in enumerate(TICKERS):
            progress_text = f"Fetching data for {ticker} ({i+1}/{len(TICKERS)})"
            progress_bar.progress((i + 1) / len(TICKERS), text=progress_text)
            quarter_results, err = get_financial_data(ticker)
            today = datetime.date.today()
            # At least 8 months of data
            start_date = (today - datetime.timedelta(days=300)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            df_price = get_eod_prices(ticker, API_TOKEN, start_date, end_date)
            m6 = get_6m_momentum(df_price)
            m1 = get_1m_momentum(df_price)
            breakscore = get_breakscore(df_price)
            if quarter_results:
                for financials in quarter_results:
                    report_date_obj = pd.to_datetime(financials["report_date"]).date()
                    if not (datetime.date(2024, 1, 1) <= report_date_obj <= datetime.date.today()):
                        continue
                    ebit_brl = financials["ebit_usd"] * rate
                    ey_value = (ebit_brl / financials["enterprise_value_brl"]) * 100 if financials["enterprise_value_brl"] else 0
                    capital_employed_brl = financials["total_debt_brl"] + financials["total_equity_brl"]
                    capital_employed_usd = (capital_employed_brl / rate) if rate else 0
                    roc_value = (financials["ebit_usd"] / capital_employed_usd) * 100 if capital_employed_usd else 0
                    weighted_score = (ey_value * 1) + (roc_value * 0.33)
                    all_results.append({
                        "Ticker": ticker,
                        "Report Date": financials["report_date"],
                        "Earnings Yield": ey_value,
                        "Return on Capital": roc_value,
                        "6m Momentum": m6,
                        "1m Momentum": m1,
                        "Breakscore": breakscore,
                        "Weighted Score": weighted_score
                    })
                    all_dates.add(financials["report_date"])
                    if ey_value > 0 and roc_value > 0:
                        ok.append(ticker)
                    else:
                        neg.append(ticker)
            else:
                failed.append(ticker)
            st.session_state.fetch_log.append(f"{ticker}: {err}")
            time.sleep(0.2)  # prevent API bans
        progress_bar.empty()
        if all_results:
            df = pd.DataFrame(all_results)
            # Composite score (tweak the weights as desired)
            df['Magic Rank Momentum'] = (
                df['Weighted Score'] +
                0.5 * df['6m Momentum'].fillna(0) +
                0.2 * df['1m Momentum'].fillna(0) +
                2 * df['Breakscore'].fillna(0)
            )
            df = df.sort_values('Magic Rank Momentum', ascending=False).reset_index(drop=True)
            df['Rank'] = df.index + 1
            st.session_state.results_df = df
            st.session_state.all_dates = sorted(list(all_dates), reverse=True)
            st.session_state.fetch_summary = LANG_TEXT["fetch_summary"][lang].format(
                ok=len(ok), neg=len(neg), fail=len(failed)
            )
        else:
            st.session_state.results_df = None
            st.session_state.all_dates = []
            st.session_state.fetch_summary = LANG_TEXT["fetch_summary"][lang].format(ok=0, neg=0, fail=len(TICKERS))

# --- Display Logic ---

if st.session_state.results_df is not None and not st.session_state.results_df.empty:
    df = st.session_state.results_df.copy()
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date.today()
    df['Report Date'] = pd.to_datetime(df['Report Date']).dt.date
    df = df[(df['Report Date'] >= start_date) & (df['Report Date'] <= end_date)]
    df = df.sort_values('Rank', ascending=True)
    df = df.drop_duplicates(subset=['Ticker'], keep='first')

    st.markdown("---")
    st.info(st.session_state.fetch_summary)
    st.subheader(LANG_TEXT["table_header"][lang])
    st.markdown(f"**{LANG_TEXT['ticker_counter'][lang].format(n=len(df))}**")
    st.dataframe(
        df[[
            "Ticker", "Report Date", "Earnings Yield", "Return on Capital",
            "6m Momentum", "1m Momentum", "Breakscore", "Weighted Score",
            "Magic Rank Momentum", "Rank"
        ]],
        column_config={
            "Earnings Yield": st.column_config.NumberColumn(format="%.2f%%"),
            "Return on Capital": st.column_config.NumberColumn(format="%.2f%%"),
            "6m Momentum": st.column_config.NumberColumn(format="%.2f%%"),
            "1m Momentum": st.column_config.NumberColumn(format="%.2f%%"),
            "Weighted Score": st.column_config.NumberColumn(format="%.2f"),
            "Magic Rank Momentum": st.column_config.NumberColumn(format="%.2f"),
            "Rank": st.column_config.NumberColumn()
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(LANG_TEXT["no_data"][lang])
