import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Forex Tools", layout="wide")
st.title("🏦 Forex Trading Tools")

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
TICKERS = {p: f"{p}=X" for p in PAIRS}

st.sidebar.title("Settings")
selected = st.sidebar.multiselect("Select Pairs", PAIRS, default=PAIRS[:3])

if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=300)
def get_price(pair):
    try:
        data = yf.download(TICKERS[pair], period="1d", interval="1h", progress=False)
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except:
        pass
    return None

@st.cache_data(ttl=600)
def get_rsi(pair):
    try:
        data = yf.download(TICKERS[pair], period="1mo", interval="1h", progress=False)
        if len(data) > 14:
            close = data["Close"]
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
    except:
        pass
    return 50

tab1, tab2, tab3 = st.tabs(["📊 Signals", "💹 Prices", "ℹ️ Info"])

with tab1:
    st.subheader("Trading Signals")
    if not selected:
        st.info("Select pairs from sidebar")
    else:
        for pair in selected:
            price = get_price(pair)
            rsi = get_rsi(pair)
            if price:
                st.markdown(f"### {pair}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Price", f"{price:.5f}")
                col2.metric("RSI", f"{rsi:.1f}")
                if rsi < 30:
                    col3.metric("Signal", "🟢 BUY")
                elif rsi > 70:
                    col3.metric("Signal", "🔴 SELL")
                else:
                    col3.metric("Signal", "🟡 HOLD")
                st.divider()

with tab2:
    st.subheader("Live Prices")
    prices_data = []
    for pair in selected:
        price = get_price(pair)
        if price:
            prices_data.append({"Pair": pair, "Price": f"{price:.5f}"})
    if prices_data:
        st.dataframe(pd.DataFrame(prices_data), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("""
    ### About
    - Real-time forex quotes
    - RSI indicator (14 period)
    - Simple trading signals
    
    **Signals:**
    - 🟢 BUY: RSI < 30 (Oversold)
    - 🔴 SELL: RSI > 70 (Overbought)
    - 🟡 HOLD: RSI 30-70 (Neutral)
    
    ⚠️ Educational only. Manage risk!
    """)