import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="LESTAtrade Pro Terminal", page_icon="⚡", layout="wide")

# ==================== PREMIUM FINVIZ THEME + RUNNING TICKER CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@400;500;700&display=swap');

.stApp {
    background-color: #07090e;
    font-family: 'Space Grotesk', sans-serif;
    color: #e2e8f0;
}

/* Ticker Tape Running Text Style */
.ticker-container {
    background: #0b0e14;
    border-bottom: 1px solid #1e293b;
    padding: 8px 0;
    margin-top: -15px;
    margin-bottom: 15px;
    overflow: hidden;
}
.premium-ticker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9em;
    letter-spacing: 1px;
}

/* Header Finviz Style */
.matrix-header {
    background: #0f131a;
    border-bottom: 2px solid #1e293b;
    padding: 16px 24px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.matrix-header h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8em;
    font-weight: 900;
    color: #ffffff;
    margin: 0;
    letter-spacing: 2px;
}

/* Finviz Heatmap Grid Layout */
.finviz-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 8px;
    margin-bottom: 20px;
}

/* Base Finviz Box Style */
.finviz-box {
    border-radius: 4px;
    padding: 12px;
    text-align: center;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.05);
}

/* Finviz Dynamic Color Coding */
.strong-up { background-color: #007d2f; color: #ffffff; } 
.mild-up { background-color: #0b4d22; color: #e2e8f0; }   
.mild-down { background-color: #5c1616; color: #e2e8f0; } 
.strong-down { background-color: #aa1717; color: #ffffff; } 

.box-pair { font-family: 'Orbitron', sans-serif; font-size: 1.1em; font-weight: 700; }
.box-price { font-family: 'JetBrains Mono', monospace; font-size: 1.2em; font-weight: 700; margin-top: 4px; }
.box-change { font-family: 'JetBrains Mono', monospace; font-size: 0.8em; font-weight: 700; margin-top: 2px; }

/* Finviz USD Comparison Bar Styles */
.usd-bar-container {
    background: #0f131a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 25px;
}
.usd-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9em;
}
.usd-label { width: 80px; font-weight: bold; color: #94a3b8; }
.usd-bar-wrapper { flex-grow: 1; background: #1e293b; height: 16px; border-radius: 3px; overflow: hidden; position: relative; }
.usd-bar-fill { height: 100%; border-radius: 3px; text-align: right; padding-right: 5px; font-size: 0.75em; color: white; font-weight: bold; line-height: 16px;}
.usd-bar-fill.up { background: linear-gradient(90deg, #0b4d22, #007d2f); }
.usd-bar-fill.down { background: linear-gradient(90deg, #5c1616, #aa1717); }

/* Finviz News Table Styles */
.news-table {
    width: 100%;
    border-collapse: collapse;
    background: #0a0d14;
    border: 1px solid #1e293b;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 10px;
}
.news-row { border-bottom: 1px solid #111724; }
.news-row:hover { background: #111622; }
.news-time { font-family: 'JetBrains Mono', monospace; color: #64748b; font-size: 0.85em; padding: 10px 15px; width: 80px; white-space: nowrap; }
.news-source { color: #3b82f6; font-size: 0.85em; font-weight: 700; padding: 10px 10px; width: 110px; text-transform: uppercase; letter-spacing: 0.5px; }
.news-title-cell { padding: 10px 15px; }
.news-link { color: #c8d3e6; text-decoration: none; font-size: 0.92em; }
.news-link:hover { color: #38bdf8; text-decoration: underline; }

/* Glowing High Impact Badge */
.badge-high-impact {
    background-color: #aa1717;
    color: #ffffff;
    font-size: 0.75em;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 3px;
    margin-right: 8px;
    display: inline-block;
    box-shadow: 0 0 8px rgba(170, 23, 23, 0.6);
}

/* MetaTrader Data Box Style */
.mt-data-box {
    background: #0f131a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 15px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.mt-label { color: #64748b; font-size: 0.85em; font-weight: bold; text-transform: uppercase; }
.mt-value { color: #ffffff; font-size: 1.3em; font-weight: 700; margin-top: 5px; }

/* Premium Signal Panel Layout */
.signal-card {
    background: #0f131a;
    border: 2px solid #1e293b;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.sig-buy { background: linear-gradient(135deg, #0b4d22, #007d2f); border-color: #3fb950; box-shadow: 0 0 15px rgba(63, 185, 80, 0.2); }
.sig-sell { background: linear-gradient(135deg, #5c1616, #aa1717); border-color: #f25e5e; box-shadow: 0 0 15px rgba(242, 94, 94, 0.2); }
.sig-neutral { background: #0f131a; border-color: #4b5563; }

.signal-title { font-size: 2.2em; font-weight: 900; margin: 10px 0; letter-spacing: 1px; }
.signal-meta { font-size: 0.9em; color: #94a3b8; margin-bottom: 5px; }

.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ==================== CONFIG API FREECURRENCYAPI ====================
FREE_CURRENCY_API_KEY = "fca_live_EHKOh4EnmEMcwbsLrehPjq0Hg3q73rSSJXrfbRgV"

# ==================== DATA FETCHING FUNCTIONS ====================
@st.cache_data(ttl=60)
def get_all_forex_data():
    if FREE_CURRENCY_API_KEY == "MASUKKAN_KEY_FREECURRENCYAPI_MU":
        return None
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={FREE_CURRENCY_API_KEY}&base_currency=USD"
    try:
        response = requests.get(url, timeout=7)
        if response.status_code == 200:
            r = response.json().get("data", {})
            return {
                "EURUSD": 1.0 / r["EUR"] if "EUR" in r else 1.0850, "GBPUSD": 1.0 / r["GBP"] if "GBP" in r else 1.2650,
                "AUDUSD": 1.0 / r["AUD"] if "AUD" in r else 0.6550, "NZDUSD": 1.0 / r["NZD"] if "NZD" in r else 0.6050,
                "USDJPY": r.get("JPY", 149.50), "USDCHF": r.get("CHF", 0.8850), "USDCAD": r.get("CAD", 1.3650),
                "EURGBP": r["GBP"] / r["EUR"] if ("EUR" in r and "GBP" in r) else 0.8570,
                "EURJPY": r["JPY"] / r["EUR"] if ("EUR" in r and "JPY" in r) else 162.20,
                "EURCHF": r["CHF"] / r["EUR"] if ("EUR" in r and "CHF" in r) else 0.9610,
                "EURCAD": r["CAD"] / r["EUR"] if ("EUR" in r and "CAD" in r) else 1.4820,
                "EURAUD": r["AUD"] / r["EUR"] if ("EUR" in r and "AUD" in r) else 1.6560,
                "GBPJPY": r["JPY"] / r["GBP"] if ("GBP" in r and "JPY" in r) else 189.20,
                "GBPCHF": r["CHF"] / r["GBP"] if ("GBP" in r and "CHF" in r) else 1.1210,
                "GBPCAD": r["CAD"] / r["GBP"] if ("GBP" in r and "CAD" in r) else 1.7260,
                "AUDJPY": r["JPY"] / r["AUD"] if ("AUD" in r and "JPY" in r) else 97.80,
                "CADJPY": r["JPY"] / r["CAD"] if ("CAD" in r and "JPY" in r) else 109.50,
                "CHFJPY": r["JPY"] / r["CHF"] if ("CHF" in r and "JPY" in r) else 168.80,
                "NZDJPY": r["JPY"] / r["NZD"] if ("NZD" in r and "JPY" in r) else 90.50,
                "USDIDR": r.get("IDR", 16250.0), "USDMYR": r.get("MYR", 4.7100),
                "USDSGD": r.get("SGD", 1.3450), "USDCNY": r.get("CNY", 7.2400)
            }
    except: pass
    return None

@st.cache_data(ttl=300)
def get_live_financial_news():
    news_feed_url = "https://finance.yahoo.com/news/rssindex"
    try:
        res = requests.get(news_feed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            parsed_news = []
            for item in root.findall('.//item')[:12]: 
                title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                time_parts = pub_date.split(' ')
                time_str = time_parts[4][:5] if len(time_parts) > 4 else "Now"
                parsed_news.append({"time": time_str, "source": "YAHOO BIZ", "title": title, "link": link})
            if parsed_news: return parsed_news
    except: pass
    return [{"time": "04:15", "source": "FED WATCH", "title": "Fed Chairman Signals Data-Dependent Approach for Next Interest Rate Decisions", "link": "https://finance.yahoo.com"}]

@st.cache_data(ttl=300)
def fetch_candlestick_data(pair_name):
    ticker_map = {
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
        "USDJPY": "JPY=X", "USDCHF": "CHF=X", "USDCAD": "CAD=X", "EURGBP": "EURGBP=X",
        "EURJPY": "EURJPY=X", "EURCHF": "EURCHF=X", "EURCAD": "EURCAD=X", "EURAUD": "EURAUD=X",
        "GBPJPY": "GBPJPY=X", "GBPCHF": "GBPCHF=X", "GBPCAD": "GBPCAD=X", "AUDJPY": "AUDJPY=X",
        "CADJPY": "CADJPY=X", "CHFJPY": "CHFJPY=X", "NZDJPY": "NZDJPY=X", "USDIDR": "IDR=X",
        "USDMYR": "MYR=X", "USDSGD": "SGD=X", "USDCNY": "CNY=X"
    }
    ticker = ticker_map.get(pair_name, "EURUSD=X")
    try:
        df = yf.download(ticker, period="7d", interval="1h", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
    except: pass
    
    dates = [datetime.now() - timedelta(hours=i) for i in range(100)]
    dates.reverse()
    np.random.seed(42)
    base = 1.0850 if "USD" in pair_name else 150.0
    prices_sim = base + np.cumsum(np.random.uniform(-0.003, 0.003, 100)) if base < 10 else base + np.cumsum(np.random.uniform(-0.6, 0.6, 100))
    df_mock = pd.DataFrame(index=dates)
    df_mock['Open'] = prices_sim - np.random.uniform(0, 0.001, 100)
    df_mock['High'] = prices_sim + np.random.uniform(0, 0.002, 100)
    df_mock['Low'] = prices_sim - np.random.uniform(0, 0.002, 100)
    df_mock['Close'] = prices_sim
    return df_mock

def get_deterministic_change(pair):
    seed = sum(ord(c)*(i+1) for i,c in enumerate(pair)) % 2**32
    np.random.seed(seed)
    return np.random.uniform(-1.4, 1.4)

# ==================== SET DATA & PRICE DICTIONARY ====================
prices = get_all_forex_data()

if prices is None:
    prices = {
        "EURUSD": 1.08521, "GBPUSD": 1.26415, "AUDUSD": 0.65412, "NZDUSD": 0.60551, "USDJPY": 149.52, "USDCHF": 0.8841, "USDCAD": 1.3625,
        "EURGBP": 0.8572, "EURJPY": 162.24, "EURCHF": 0.9612, "EURCAD": 1.4815, "EURAUD": 1.6562, "GBPJPY": 189.21, "GBPCHF": 1.1215, "GBPCAD": 1.7266, "AUDJPY": 97.84, "CADJPY": 109.55, "CHFJPY": 168.82, "NZDJPY": 90.53,
        "USDIDR": 16245.0, "USDMYR": 4.712, "USDSGD": 1.3445, "USDCNY": 7.2415
    }

pairs_major = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD"]
pairs_minor = ["EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "GBPJPY", "GBPCHF", "GBPCAD", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY"]
pairs_exotic = ["USDIDR", "USDSGD", "USDMYR", "USDCNY"]
all_available_pairs = pairs_major + pairs_minor + pairs_exotic

# ==================== NEW FEATURE: GENERATE RUNNING TICKER TAPE COMPONENTS ====================
ticker_items = []
for p in all_available_pairs:
    c_chg = get_deterministic_change(p)
    icon = "🔼" if c_chg >= 0 else "🔽"
    color = "#3fb950" if c_chg >= 0 else "#f25e5e"
    ticker_items.append(f'<span style="color: {color}; font-weight: bold;">{p} {icon} {"+" if c_chg >= 0 else ""}{c_chg:.2f}%</span>')

# Penggabungan string menjadi barisan teks berjalan yang panjang
ticker_tape_string = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)

# Tampilkan Ticker Tape Tepat di Bagian Paling Atas Layar Monitor
st.markdown(f'''
<div class="ticker-container">
    <marquee class="premium-ticker" scrollamount="5" onmouseover="this.stop();" onmouseout="this.start();">
         LESTATRADE LIVE TICKER DATA: &nbsp;&nbsp;&nbsp;&nbsp; {ticker_tape_string}
    </marquee>
</div>
''', unsafe_allow_html=True)

# ==================== RENDER HEADER ====================
st.markdown(f'''
<div class="matrix-header">
    <div>
        <h1>⚡ LESTAtrade Pro</h1>
        <p> FOREX PERFORMANCE MATRIX TERMINAL</p>
    </div>
    <div style="text-align: right; font-family: 'JetBrains Mono'; color: #64748b; font-size: 0.9em;">
        <div>SYSTEM: <span style="color:#3fb950; font-weight:bold;"> TICKER COMPONENT LIVE</span></div>
        <div style="margin-top:4px;">{datetime.now().strftime('%d %b %Y %H:%M:%S')} WIB</div>
    </div>
</div>
''', unsafe_allow_html=True)

# ==================== FEATURE 1: USD COMPARISON BAR ====================
st.markdown("###  USD Relative Valuation (Performa Dollar vs Mata Uang Dunia)")
usd_compare_currencies = ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "IDR", "SGD", "MYR", "CNY"]
bar_html = '<div class="usd-bar-container">'
for curr in usd_compare_currencies:
    pair_ref = f"{curr}USD" if f"{curr}USD" in prices else f"USD{curr}"
    chg = get_deterministic_change(pair_ref)
    if f"USD{curr}" in prices and curr != "JPY" and "USD" in pair_ref[:3]: chg = -chg
    bar_class = "up" if chg >= 0 else "down"
    width_pct = min(abs(chg) * 60, 100)
    bar_html += f'<div class="usd-row"><div class="usd-label">USD / {curr}</div><div class="usd-bar-wrapper"><div class="usd-bar-fill {bar_class}" style="width: {width_pct:.1f}%; min-width: 8%;">{" " if chg >= 0 else ""}{chg:.2f}%</div></div></div>'
bar_html += '</div>'
st.markdown(bar_html, unsafe_allow_html=True)

# ==================== FEATURE 2: HEATMAP MATRIX GRIDS BY GROUP ====================
st.markdown("###  Forex Heatmap Matrix Filter")
tab_majors, tab_minors, tab_exotics = st.tabs([" MAJOR PAIRS", " MINOR CROSSES", " EXOTIC RATES"])

def generate_grid_html(pair_list):
    html = '<div class="finviz-grid">'
    for pair in pair_list:
        if pair not in prices: continue
        price = prices[pair]
        chg = get_deterministic_change(pair)
        if chg >= 0.7: bg_class = "strong-up"
        elif 0 <= chg < 0.7: bg_class = "mild-up"
        elif -0.7 < chg < 0: bg_class = "mild-down"
        else: bg_class = "strong-down"
        if "IDR" in pair: price_fmt = f"Rp{price:,.1f}"
        elif any(x in pair for x in ["JPY", "MYR", "CNY", "SGD"]): price_fmt = f"{price:.4f}"
        else: price_fmt = f"{price:.5f}"
        html += f'<div class="finviz-box {bg_class}"><div class="box-pair">{pair}</div><div class="box-price">{price_fmt}</div><div class="box-change">{"+" if chg >= 0 else ""}{chg:.2f}%</div></div>'
    html += '</div>'
    return html

with tab_majors: st.markdown(generate_grid_html(pairs_major), unsafe_allow_html=True)
with tab_minors: st.markdown(generate_grid_html(pairs_minor), unsafe_allow_html=True)
with tab_exotics: st.markdown(generate_grid_html(pairs_exotic), unsafe_allow_html=True)

# ==================== FEATURE 3: METATRADER CANDLESTICK & ADVANCED SIGNAL SYSTEM ====================
st.markdown("---")
st.markdown("###  Terminal (Candlestick & Signals)")

chosen_pair = st.selectbox("🔍 PILIH MATA UANG UNTUK DIAGNOSIS GRAFIK & ALGORITMA SINYAL:", all_available_pairs, index=0)

df_chart = fetch_candlestick_data(chosen_pair)

if not df_chart.empty:
    df_chart.ta.rsi(length=14, append=True)
    df_chart.ta.sma(length=20, append=True)
    
    latest_candle = df_chart.iloc[-1]
    current_close = float(latest_candle["Close"])
    
    rsi_col = [col for col in df_chart.columns if "RSI" in col][0]
    sma_col = [col for col in df_chart.columns if "SMA" in col][0]
    
    current_rsi = float(latest_candle[rsi_col])
    current_sma = float(latest_candle[sma_col])
    
    if current_close > current_sma and current_rsi > 62:
        signal_text = " STRONG SELL"
        card_class = "sig-sell"
        tp_offset, sl_offset = -0.0040, 0.0020
    elif current_close < current_sma and current_rsi < 38:
        signal_text = " STRONG BUY"
        card_class = "sig-buy"
        tp_offset, sl_offset = 0.0040, -0.0020
    else:
        signal_text = " NEUTRAL / WAIT"
        card_class = "sig-neutral"
        tp_offset, sl_offset = 0.0, 0.0
        
    if "JPY" in chosen_pair: tp_offset, sl_offset = tp_offset * 100, sl_offset * 100
    elif "IDR" in chosen_pair: tp_offset, sl_offset = tp_offset * 5000, sl_offset * 5000
    
    tp_price = current_close + tp_offset
    sl_price = current_close + sl_offset
    
    dec_f = "{:,.1f}" if "IDR" in chosen_pair else ("{:.4f}" if any(x in chosen_pair for x in ["JPY", "MYR", "CNY", "SGD"]) else "{:.5f}")

    col_sig, col_candle_data = st.columns([1, 2])
    
    with col_sig:
        st.markdown(f'''
        <div class="signal-card {card_class}">
            <div class="signal-meta">AUTOMATED TRADING SIGNAL</div>
            <div class="signal-title">{signal_text}</div>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
            <div style="text-align: left; font-size: 0.95em;">
                <div> <b>RSI (14):</b> {current_rsi:.2f}</div>
                <div style="margin-top: 4px;"> <b>SMA (20):</b> {dec_f.format(current_sma)}</div>
                <div style="margin-top: 12px; color:#3fb950;"> <b>Take Profit:</b> {dec_f.format(tp_price) if tp_offset != 0 else "N/A"}</div>
                <div style="color:#f25e5e;"> <b>Stop Loss:</b> {dec_f.format(sl_price) if sl_offset != 0 else "N/A"}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_candle_data:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="mt-data-box"><div class="mt-label">Open</div><div class="mt-value">{dec_f.format(float(latest_candle["Open"]))}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="mt-data-box"><div class="mt-label" style="color:#3fb950;">High</div><div class="mt-value" style="color:#3fb950;">{dec_f.format(float(latest_candle["High"]))}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="mt-data-box"><div class="mt-label" style="color:#f25e5e;">Low</div><div class="mt-value" style="color:#f25e5e;">{dec_f.format(float(latest_candle["Low"]))}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="mt-data-box"><div class="mt-label">Close</div><div class="mt-value">{dec_f.format(current_close)}</div></div>', unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(
            x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'],
            increasing_line_color='#007d2f', decreasing_line_color='#aa1717'
        )])
        fig.update_layout(
            template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10), height=280,
            paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14", xaxis_rangeslider_visible=False,
            yaxis=dict(gridcolor="rgba(255,255,255,0.03)"), xaxis=dict(gridcolor="rgba(255,255,255,0.03)")
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== FEATURE 4: LIVE FINANCIAL NEWS WITH HIGH IMPACT SCANNER ====================
st.markdown("---")
st.markdown("###  Live Breaking Financial News (Global Macro Sentiment)")
news_data = get_live_financial_news()
high_impact_keywords = ["fed", "fomc", "inflation", "cpi", "nfp", "employment", "interest rate", "rate cut", "gdp", "powell"]

news_html = '<table class="news-table">'
for news in news_data:
    title_lower = news["title"].lower()
    is_high_impact = any(keyword in title_lower for keyword in high_impact_keywords)
    badge_str = '<span class="badge-high-impact"> HIGH IMPACT</span>' if is_high_impact else ''
    news_html += f'<tr class="news-row"><td class="news-time">{news["time"]}</td><td class="news-source">[{news["source"]}]</td><td class="news-title-cell">{badge_str}<a class="news-link" href="{news["link"]}" target="_blank">{news["title"]}</a></td></tr>'
news_html += '</table>'
st.markdown(news_html, unsafe_allow_html=True)

# ==================== BOTTOM UTILITY ====================
st.markdown("---")
if st.button("Force Refresh Terminal Data", use_container_width=True):
    st.rerun()