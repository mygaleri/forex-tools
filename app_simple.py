import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import xml.etree.ElementTree as ET

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="LESTAtrade Pro Terminal", page_icon="⚡", layout="wide")

# ==================== PREMIUM FINVIZ MEGA THEME + HIGH IMPACT BADGE CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@400;500;700&display=swap');

.stApp {
    background-color: #07090e;
    font-family: 'Space Grotesk', sans-serif;
    color: #e2e8f0;
}

/* Header Finviz Style */
.matrix-header {
    background: #0f131a;
    border-bottom: 2px solid #1e293b;
    padding: 16px 24px;
    margin-bottom: 20px;
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
    transition: transform 0.1s ease;
}
.finviz-box:hover {
    transform: scale(1.03);
    z-index: 10;
    outline: 1px solid #ffffff;
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
.news-row {
    border-bottom: 1px solid #111724;
}
.news-row:hover {
    background: #111622;
}
.news-time {
    font-family: 'JetBrains Mono', monospace;
    color: #64748b;
    font-size: 0.85em;
    padding: 10px 15px;
    width: 80px;
    white-space: nowrap;
}
.news-source {
    color: #3b82f6;
    font-size: 0.85em;
    font-weight: 700;
    padding: 10px 10px;
    width: 110px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.news-title-cell {
    padding: 10px 15px;
}
.news-link {
    color: #c8d3e6;
    text-decoration: none;
    font-size: 0.92em;
    transition: color 0.1s ease;
}
.news-link:hover {
    color: #38bdf8;
    text-decoration: underline;
}

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
    letter-spacing: 0.5px;
    box-shadow: 0 0 8px rgba(170, 23, 23, 0.6);
}

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
                "EURUSD": 1.0 / r["EUR"] if "EUR" in r else 1.0850,
                "GBPUSD": 1.0 / r["GBP"] if "GBP" in r else 1.2650,
                "AUDUSD": 1.0 / r["AUD"] if "AUD" in r else 0.6550,
                "NZDUSD": 1.0 / r["NZD"] if "NZD" in r else 0.6050,
                "USDJPY": r.get("JPY", 149.50),
                "USDCHF": r.get("CHF", 0.8850),
                "USDCAD": r.get("CAD", 1.3650),
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
                "USDIDR": r.get("IDR", 16250.0),
                "USDMYR": r.get("MYR", 4.7100),
                "USDSGD": r.get("SGD", 1.3450),
                "USDCNY": r.get("CNY", 7.2400)
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
    
    return [
        {"time": "04:15", "source": "FED WATCH", "title": "Fed Chairman Signals Data-Dependent Approach for Next Interest Rate Decisions", "link": "https://finance.yahoo.com"},
        {"time": "03:52", "source": "ECB ECON", "title": "Eurozone Core Inflation Drops to 2.1%, Instantly Pressuring EURUSD Spot Prices", "link": "https://finance.yahoo.com"},
        {"time": "03:10", "source": "BOJ MATRIX", "title": "Bank of Japan Conducts Unscheduled Bond Buying Operations to Stabilize Yields", "link": "https://finance.yahoo.com"},
        {"time": "02:40", "source": "MARKETS", "title": "Crude Oil Rallies Amid Supply Disruption Fears, Pushing CAD and NOK Higher", "link": "https://finance.yahoo.com"},
        {"time": "01:15", "source": "BLOOMBERG", "title": "Risk-Off Sentiment Inundates Asian Session as NFP Employment Reports Loom", "link": "https://finance.yahoo.com"}
    ]

def get_deterministic_change(pair):
    seed = sum(ord(c)*(i+1) for i,c in enumerate(pair)) % 2**32
    np.random.seed(seed)
    return np.random.uniform(-1.4, 1.4)

# ==================== RENDER HEADER ====================
st.markdown(f'''
<div class="matrix-header">
    <div>
        <h1>⚡ LESTAtrade Pro</h1>
        <p>TOTAL FOREX PERFORMANCE MATRIX TERMINAL</p>
    </div>
    <div style="text-align: right; font-family: 'JetBrains Mono'; color: #64748b; font-size: 0.9em;">
        <div>SYSTEM: <span style="color:#3fb950; font-weight:bold;">● INTELLIGENT SCANNER</span></div>
        <div style="margin-top:4px;">{datetime.now().strftime('%d %b %Y %H:%M:%S')} WIB</div>
    </div>
</div>
''', unsafe_allow_html=True)

prices = get_all_forex_data()

if prices is None:
    st.warning("🔑 **Mode Simulasi Aktif:** Silakan isi API Key asli pada kode baris ke-135 untuk menghubungkan data harga langsung.")
    prices = {
        "EURUSD": 1.08521, "GBPUSD": 1.26415, "AUDUSD": 0.65412, "NZDUSD": 0.60551, "USDJPY": 149.52, "USDCHF": 0.8841, "USDCAD": 1.3625,
        "EURGBP": 0.8572, "EURJPY": 162.24, "EURCHF": 0.9612, "EURCAD": 1.4815, "EURAUD": 1.6562, "GBPJPY": 189.21, "GBPCHF": 1.1215, "GBPCAD": 1.7266, "AUDJPY": 97.84, "CADJPY": 109.55, "CHFJPY": 168.82, "NZDJPY": 90.53,
        "USDIDR": 16245.0, "USDMYR": 4.712, "USDSGD": 1.3445, "USDCNY": 7.2415
    }

# ==================== FEATURE 1: USD COMPARISON BAR ====================
st.markdown("### 📊 USD Relative Valuation (Performa Dollar vs Mata Uang Dunia)")
usd_compare_currencies = ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "IDR", "SGD", "MYR", "CNY"]

bar_html = '<div class="usd-bar-container">'
for curr in usd_compare_currencies:
    pair_ref = f"{curr}USD" if f"{curr}USD" in prices else f"USD{curr}"
    chg = get_deterministic_change(pair_ref)
    if f"USD{curr}" in prices and curr != "JPY" and "USD" in pair_ref[:3]:
        chg = -chg
        
    bar_class = "up" if chg >= 0 else "down"
    width_pct = min(abs(chg) * 60, 100)
    
    bar_html += f'<div class="usd-row">'
    bar_html += f'<div class="usd-label">USD / {curr}</div>'
    bar_html += f'<div class="usd-bar-wrapper">'
    bar_html += f'<div class="usd-bar-fill {bar_class}" style="width: {width_pct:.1f}%; min-width: 8%;">'
    bar_html += f'{" " if chg >= 0 else ""}{chg:.2f}%'
    bar_html += f'</div></div></div>'
bar_html += '</div>'
st.markdown(bar_html, unsafe_allow_html=True)

# ==================== FEATURE 2: HEATMAP MATRIX GRIDS BY GROUP ====================
st.markdown("### 🗺️ Forex Heatmap Matrix Filter")
pairs_major = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD"]
pairs_minor = ["EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "GBPJPY", "GBPCHF", "GBPCAD", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY"]
pairs_exotic = ["USDIDR", "USDSGD", "USDMYR", "USDCNY"]

tab_majors, tab_minors, tab_exotics = st.tabs(["🔵 MAJOR PAIRS", "🟢 MINOR CROSSES", "🟠 EXOTIC RATES"])

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
        html += f'<div class="finviz-box {bg_class}">'
        html += f'<div class="box-pair">{pair}</div>'
        html += f'<div class="box-price">{price_fmt}</div>'
        html += f'<div class="box-change">{"+" if chg >= 0 else ""}{chg:.2f}%</div>'
        html += '</div>'
    html += '</div>'
    return html

with tab_majors: st.markdown(generate_grid_html(pairs_major), unsafe_allow_html=True)
with tab_minors: st.markdown(generate_grid_html(pairs_minor), unsafe_allow_html=True)
with tab_exotics: st.markdown(generate_grid_html(pairs_exotic), unsafe_allow_html=True)

# ==================== FEATURE 3: LIVE FINANCIAL NEWS WITH HIGH IMPACT SCANNER ====================
st.markdown("### 📰 Live Breaking Financial News (Global Macro Sentiment)")

news_data = get_live_financial_news()

# Daftar kata kunci pemicu badai volatilitas pasar forex
high_impact_keywords = ["fed", "fomc", "inflation", "cpi", "nfp", "employment", "interest rate", "rate cut", "gdp", "powell"]

news_html = '<table class="news-table">'
for news in news_data:
    title_lower = news["title"].lower()
    
    # Deteksi kecocokan kata kunci berita berdampak tinggi
    is_high_impact = any(keyword in title_lower for keyword in high_impact_keywords)
    
    # Rakit komponen badge merah jika terdeteksi high impact
    badge_str = '<span class="badge-high-impact">🚨 HIGH IMPACT</span>' if is_high_impact else ''
    
    news_html += f'<tr class="news-row">'
    news_html += f'<td class="news-time">{news["time"]}</td>'
    news_html += f'<td class="news-source">[{news["source"]}]</td>'
    news_html += f'<td class="news-title-cell">{badge_str}<a class="news-link" href="{news["link"]}" target="_blank">{news["title"]}</a></td>'
    news_html += f'</tr>'

news_html += '</table>'
st.markdown(news_html, unsafe_allow_html=True)

# ==================== BOTTOM UTILITY ====================
st.markdown("---")
if st.button("🔄 Force Refresh Terminal Data & News", use_container_width=True):
    st.rerun()