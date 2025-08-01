import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import datetime
import time

API_TOKEN = st.secrets["API_TOKEN"]

TICKERS = [
    "PETR4.SA","VALE3.SA","BBAS3.SA","MGLU3.SA","B3SA3.SA","COGN3.SA","ABEV3.SA","BBDC4.SA","ITSA4.SA","AZUL4.SA",
    "VAMO3.SA","ITUB4.SA","RAIZ4.SA","CSAN3.SA","CVCB3.SA","RAIL3.SA","PETR3.SA","PRIO3.SA","BEEF3.SA","CSNA3.SA",
    "GGBR4.SA","LREN3.SA","RENT3.SA","SUZB3.SA","WEGE3.SA","JBSS3.SA","BRFS3.SA","ELET3.SA","ELET6.SA","BRKM5.SA",
    "BRAP4.SA","HAPV3.SA","NTCO3.SA","ASAI3.SA","ENEV3.SA","EGIE3.SA","CPLE6.SA","CMIG4.SA","TAEE11.SA","TRPL4.SA",
    "ENBR3.SA","CPFE3.SA","EMBR3.SA","TIMS3.SA","VIVT3.SA","BRML3.SA","MULT3.SA","IGTI11.SA","ALPA4.SA","CRFB3.SA",
    "PCAR3.SA","MRVE3.SA","CYRE3.SA","EZTC3.SA","TOTS3.SA","QUAL3.SA","YDUQ3.SA","SEER3.SA","SOMA3.SA","AMER3.SA",
    "CASH3.SA","LWSA3.SA","BIDI11.SA","BPAC11.SA","PSSA3.SA","BBSE3.SA","SULA11.SA","HYPE3.SA","RADL3.SA","FLRY3.SA",
    "GNDI3.SA","CSMG3.SA","SBSP3.SA","SAPR11.SA","SANB11.SA","BRDT3.SA","UGPA3.SA","PETZ3.SA","ARZZ3.SA","MOVI3.SA",
    "VIIA3.SA","CAML3.SA","ALSO3.SA","MRFG3.SA","SLCE3.SA","JHSF3.SA","BRSR6.SA","ENAT3.SA","TRIS3.SA","LOGG3.SA",
    "BMGB4.SA","MEAL3.SA","CEAB3.SA","PNVL3.SA","ODPV3.SA","LIGT3.SA","AESB3.SA","NEOE3.SA","CPLE3.SA","CMIN3.SA",
    "RECV3.SA","RRRP3.SA","AERI3.SA","BRPR3.SA","ALUP11.SA","BRAP3.SA","BRSR3.SA","BRSR5.SA","CEGR3.SA","CESP3.SA",
    "CESP5.SA","CESP6.SA","CGAS3.SA","CGAS5.SA","CLSC3.SA","CLSC4.SA","CMIG3.SA","CRIV3.SA","CRIV4.SA","CSAB3.SA",
    "CSAB4.SA","CTKA3.SA","CTKA4.SA","CTNM3.SA","CTNM4.SA","CTSA3.SA","CTSA4.SA","CTSA8.SA","CURY3.SA","CXSE3.SA",
    "DIRR3.SA","DMMO3.SA","DOHL3.SA","DOHL4.SA","EALT3.SA","EALT4.SA","ECOR3.SA","EMAE4.SA","ENGI11.SA","ENGI3.SA",
    "ENGI4.SA","EQPA3.SA","EQPA7.SA","EQTL3.SA","ETER3.SA","EUCA3.SA","EUCA4.SA","EVEN3.SA","FESA3.SA","FESA4.SA",
    "FRAS3.SA","GGBR3.SA","GOAU3.SA","GOAU4.SA","GOLL4.SA","GRND3.SA","GSHP3.SA","GUAR3.SA","HBOR3.SA","HBSA3.SA",
    "HGTX3.SA","IRBR3.SA","ITSA3.SA","ITUB3.SA","KLBN11.SA","KLBN3.SA","KLBN4.SA","LINX3.SA","LIPR3.SA","LUPA3.SA",
    "LUXM4.SA","MDIA3.SA","MELK3.SA","MILS3.SA","MLAS3.SA","MMXM3.SA","OFSA3.SA","OIBR3.SA","OIBR4.SA","OMGE3.SA",
    "PARD3.SA","PFRM3.SA","PINE4.SA","PLPL3.SA","PMAM3.SA","POSI3.SA","PTBL3.SA","RANI3.SA","RAPT3.SA","RAPT4.SA",
    "RLOG3.SA","ROMI3.SA","RSID3.SA","SAPR3.SA","SAPR4.SA","SGPS3.SA","SLED3.SA","SLED4.SA","SMTO3.SA","TAEE3.SA",
    "TAEE4.SA","TASA3.SA","TASA4.SA","TCSA3.SA","TGMA3.SA","TRPL3.SA","TUPY3.SA","UNIP3.SA","UNIP5.SA","UNIP6.SA",
    "USIM3.SA","USIM5.SA","USIM6.SA","VBBR3.SA","VLID3.SA","VULC3.SA","WEST3.SA","WHRL3.SA","WHRL4.SA"
]

LANG_TEXT = {
    "title": {
        "en": "Magic Formula - B3 Ranked Analysis",
        "pt": "Fórmula Mágica - Análise Ranqueada B3"
    },
    "description": {
        "en": "Joel Greenblatt's Magic Formula is a systematic value investing strategy that helps investors find quality companies trading at attractive prices. It ranks stocks by Earnings Yield, which highlights undervalued opportunities, and Return on Capital, which measures how efficiently a company generates profits. Companies with higher Earnings Yield and higher Return on Capital are more likely to offer strong returns, as they combine attractive pricing with proven business performance.",
        "pt": "A Fórmula Mágica de Joel Greenblatt é uma estratégia sistemática de investimento em valor que ajuda investidores a encontrar empresas de qualidade negociadas a preços atrativos. Ela classifica ações pelo Earnings Yield, que destaca oportunidades subvalorizadas, e pelo Return on Capital, que mede a eficiência da geração de lucros. Empresas com altos índices nesses critérios tendem a oferecer retornos mais sólidos, pois unem preço atrativo e desempenho comprovado."
    },
    "formula": {
        "en": "**Magic Formula Score = (Earnings Yield) + (Return on Capital) * 0.33**",
        "pt": "**Pontuação Fórmula Mágica = (Earnings Yield) + (Return on Capital) * 0,33**"
    },
    "run_button": {
        "en": "Run Analysis",
        "pt": "Executar Análise"
    },
    "date_filter": {
        "en": "Filter by Report Date:",
        "pt": "Filtrar por Data do Balanço:"
    },
    "table_header": {
        "en": "Ranked Results (All Tickers)",
        "pt": "Resultados Rankeados (Todas as Ações)"
    },
    "table_negative": {
        "en": "Tickers with Negative or Zero Earnings Yield or Return on Capital",
        "pt": "Ações com Earnings Yield ou Return on Capital Negativos ou Zero"
    },
    "ticker_counter": {
        "en": "Showing {n} stocks",
        "pt": "Exibindo {n} ações"
    },
    "no_data": {
        "en": "No data to display. Click 'Run Analysis' to begin.",
        "pt": "Nenhum dado para exibir. Clique em 'Executar Análise' para começar."
    },
    "fetch_summary": {
        "en": "Fetched {ok} tickers, {neg} with negative/zero, {fail} failed.",
        "pt": "Buscou {ok} ações, {neg} negativas/zero, {fail} falharam."
    }
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
        if not isinstance(data, list) or len(data) < 150:
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
    last_126 = df['close'].iloc[-126:-1]  # last 6 months, excluding today
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
            time.sleep(0.2)
        progress_bar.empty()
        if all_results:
            df = pd.DataFrame(all_results)
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
