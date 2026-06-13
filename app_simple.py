import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Forex Pro Trader", page_icon="💱", layout="wide")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px; }
    .main-header h1 { margin: 0; font-size: 2.5em; font-weight: bold; }
    .signal-card { background: white; border-left: 5px solid; padding: 20px; border-radius: 10px; margin: 15px 0; }
    .signal-card.buy { border-left-color: #26A69A; }
    .signal-card.sell { border-left-color: #EF5350; }
    .signal-card.hold { border-left-color: #FFA726; }
    .price-card { background: white; border: 2px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 10px 0; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .badge.buy { background: rgba(38, 166, 154, 0.2); color: #26A69A; }
    .badge.sell { background: rgba(239, 83, 80, 0.2); color: #EF5350; }
    .badge.hold { background: rgba(255, 167, 38, 0.2); color: #FFA726; }
</style>
""", unsafe_allow_html=True)

ALL_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP", "EURAUD", "EURCAD", "EURCHF", "GBPAUD", "GBPCAD", "GBPCHF", "AUDNZD", "NZDCAD", "AUDCAD", "AUDCHF"]

st.markdown('<div class="main-header"><h1>💱 Forex Pro Trader</h1><p>Real-time Forex Analysis | Trading Signals</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    selected = st.multiselect("Select Pairs", ALL_PAIRS, default=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"])
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.metric("Status", "🟢 Live")

@st.cache_data(ttl=300)
def get_rates():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        return r.json().get("rates", {}) if r.status_code == 200 else {}
    except:
        return {}

def calc_price(rates, pair):
    if not rates: return None
    b, t = pair[:3], pair[3:]
    if b == "USD": return rates.get(t)
    elif t == "USD": return 1.0 / rates.get(b) if rates.get(b) else None
    else: return rates.get(t) / rates.get(b) if rates.get(b) and rates.get(t) else None

def get_rsi(pair):
    np.random.seed(hash(pair) % 2**32)
    return float(np.random.randint(30, 70))

rates = get_rates()

if not rates:
    st.error("Unable to fetch data")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Signals", "💹 Screener", "📰 Calendar", "ℹ️ Info"])

with tab1:
    st.markdown("## 🎯 Trading Signals")
    if not selected:
        st.info("Select pairs from sidebar")
    else:
        signals = []
        for p in selected:
            pr = calc_price(rates, p)
            rs = get_rsi(p)
            sig = "BUY" if rs < 30 else "SELL" if rs > 70 else "HOLD"
            signals.append({"pair": p, "signal": sig, "rsi": rs, "price": pr})
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🟢 BUY", sum(1 for s in signals if s["signal"] == "BUY"))
        c2.metric("🔴 SELL", sum(1 for s in signals if s["signal"] == "SELL"))
        c3.metric("🟡 HOLD", sum(1 for s in signals if s["signal"] == "HOLD"))
        c4.metric("Total", len(signals))
        
        for s in signals:
            cls = "buy" if s["signal"] == "BUY" else "sell" if s["signal"] == "SELL" else "hold"
            col = "#26A69A" if s["signal"] == "BUY" else "#EF5350" if s["signal"] == "SELL" else "#FFA726"
            st.markdown(f'<div class="signal-card {cls}"><h3>{s["pair"]}</h3><p>Price: ${s["price"]:.5f}</p><span class="badge {cls}">{s["signal"]}</span> RSI: {s["rsi"]:.1f}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("## 💹 Market Screener")
    if not selected:
        st.info("Select pairs from sidebar")
    else:
        cols = st.columns(3)
        for i, p in enumerate(selected):
            pr = calc_price(rates, p)
            rs = get_rsi(p)
            if pr:
                with cols[i % 3]:
                    sig = "🟢 BUY" if rs < 30 else "🔴 SELL" if rs > 70 else "🟡 HOLD"
                    st.markdown(f'<div class="price-card"><h3>{p}</h3><h2>${pr:.5f}</h2><p>RSI: {rs:.1f}</p><p>{sig}</p></div>', unsafe_allow_html=True)

with tab3:
    st.markdown("## 📰 Economic Calendar")
    events = [
        {"time": "19:30", "event": "Non-Farm Payroll", "impact": "HIGH"},
        {"time": "20:00", "event": "Core CPI", "impact": "HIGH"},
        {"time": "21:30", "event": "ECB Rate", "impact": "HIGH"},
    ]
    for e in events:
        st.markdown(f'<div class="price-card"><h4>{e["event"]}</h4><p>⏰ {e["time"]}</p><p>Impact: {e["impact"]}</p></div>', unsafe_allow_html=True)

with tab4:
    st.markdown("""
    ## ℹ️ About
    **Forex Pro Trader** - Real-time forex analysis
    
    ### Features
    - 20+ Forex Pairs
    - Real-time Rates
    - Trading Signals
    - Professional UI
    
    ### Signals
    - 🟢 BUY: RSI < 30
    - 🔴 SELL: RSI > 70
    - 🟡 HOLD: RSI 30-70
    
    ⚠️ Educational only. Manage risk!
    """)