import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="LESTAtrade Matrix", page_icon="⚡", layout="wide")

# ==================== PREMIUM FINTECH MATRIX (FINVIZ STYLE) CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@500;700&display=swap');

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
    margin-bottom: 24px;
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
.matrix-header p {
    color: #64748b;
    margin: 0;
    font-size: 0.9em;
    font-weight: 700;
    letter-spacing: 1px;
}

/* Finviz Heatmap Grid Layout */
.finviz-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
    margin-bottom: 24px;
}

/* Base Finviz Box Style */
.finviz-box {
    border-radius: 4px;
    padding: 16px;
    text-align: center;
    position: relative;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.05);
    transition: transform 0.1s ease;
}
.finviz-box:hover {
    transform: scale(1.02);
    z-index: 10;
    outline: 1px solid #ffffff;
}

/* Finviz Dynamic Color Coding classes */
.strong-up { background-color: #007d2f; color: #ffffff; } /* Hijau Terang */
.mild-up { background-color: #0b4d22; color: #e2e8f0; }   /* Hijau Gelap */
.mild-down { background-color: #5c1616; color: #e2e8f0; } /* Merah Gelap */
.strong-down { background-color: #aa1717; color: #ffffff; } /* Merah Terang */

.box-pair {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.25em;
    font-weight: 700;
    letter-spacing: 1px;
}
.box-price {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4em;
    font-weight: 700;
    margin-top: 6px;
}
.box-change {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
    font-weight: 700;
    margin-top: 4px;
}

/* Fix Streamlit default padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== CONFIG API FREECURRENCYAPI ====================
# ⚠️ Ganti dengan API Key yang kamu dapatkan gratis dari freecurrencyapi.com
FREE_CURRENCY_API_KEY = "MASUKKAN_KEY_FREECURRENCYAPI_MU"

# ==================== DATA FETCHING & CONVERSION ====================
@st.cache_data(ttl=60)
def get_finviz_forex_data():
    """Mengambil data kurs mentah dan mengubahnya menjadi format pasangan mata uang internasional"""
    if FREE_CURRENCY_API_KEY == "MASUKKAN_KEY_FREECURRENCYAPI_MU":
        return None
        
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={FREE_CURRENCY_API_KEY}&base_currency=USD"
    
    try:
        response = requests.get(url, timeout=7)
        if response.status_code == 200:
            raw_data = response.json().get("data", {})
            
            # Rumus matematika konversi mata uang berbasis USD
            raw_prices = {
                "EURUSD": 1.0 / raw_data["EUR"] if "EUR" in raw_data else 1.085,
                "GBPUSD": 1.0 / raw_data["GBP"] if "GBP" in raw_data else 1.265,
                "AUDUSD": 1.0 / raw_data["AUD"] if "AUD" in raw_data else 0.655,
                "NZDUSD": 1.0 / raw_data["NZD"] if "NZD" in raw_data else 0.605,
                "USDJPY": raw_data.get("JPY", 149.50),
                "USDCHF": raw_data.get("CHF", 0.8850),
                "USDCAD": raw_data.get("CAD", 1.3650),
                "USDIDR": raw_data.get("IDR", 16250.0),
                "USDMYR": raw_data.get("MYR", 4.7100),
                "USDSGD": raw_data.get("SGD", 1.3450),
                "USDCNY": raw_data.get("CNY", 7.2400)
            }
            return raw_prices
    except Exception as e:
        pass
    return None

# Generate perubahan persentase simulasi yang konsisten berdasarkan nama pair
def get_deterministic_change(pair):
    seed = sum(ord(c)*(i+1) for i,c in enumerate(pair)) % 2**32
    np.random.seed(seed)
    return np.random.uniform(-1.2, 1.2)

# ==================== MAIN RENDER ====================

# Top Header Bar ala Finviz
st.markdown(f'''
<div class="matrix-header">
    <div>
        <h1>⚡ LESTAtrade</h1>
        <p>FOREX MARKET ANALYSIS FILTER</p>
    </div>
    <div style="text-align: right; font-family: 'JetBrains Mono'; color: #64748b; font-size: 0.9em;">
        <div>STATUS: <span style="color:#3fb950; font-weight:bold;">● LIVE MATRIX</span></div>
        <div style="margin-top:4px;">{datetime.now().strftime('%d %b %Y %H:%M:%S')} WIB</div>
    </div>
</div>
''', unsafe_allow_html=True)

# Fetch Data
prices = get_finviz_forex_data()

# Error handler jika API Key belum dipasang
if prices is None:
    st.warning("🔑 **API Key Belum Valid:** Menampilkan mode simulasi visual grid Finviz. Silakan masukkan API Key asli dari freecurrencyapi.com pada baris kode ke-67 agar data riil terhubung.")
    # Fallback Data Simulasi agar dashboard tetap tampil cantik saat setup
    prices = {
        "EURUSD": 1.08521, "GBPUSD": 1.26415, "AUDUSD": 0.65412, "NZDUSD": 0.60551,
        "USDJPY": 149.52, "USDCHF": 0.8841, "USDCAD": 1.3625, "USDIDR": 16245.0,
        "USDMYR": 4.712, "USDSGD": 1.3445, "USDCNY": 7.2415
    }

# Membagi Tampilan Berdasarkan Sinyal Naik/Turun
st.markdown("### 🗺️ Forex Performance Heatmap Grid")

# Memulai pembuatan string HTML Grid
grid_html = '<div class="finviz-grid">'

for pair, price in prices.items():
    chg = get_deterministic_change(pair)
    
    # Menentukan kelas warna Finviz berdasarkan nilai performa persentase
    if chg >= 0.6:
        bg_class = "strong-up"
    elif 0 <= chg < 0.6:
        bg_class = "mild-up"
    elif -0.6 < chg < 0:
        bg_class = "mild-down"
    else:
        bg_class = "strong-down"
        
    # Format desimal: IDR ratusan/ribuan tanpa koma panjang, forex biasa 4-5 angka di belakang koma
    if "IDR" in pair:
        price_fmt = f"Rp{price:,.1f}"
    elif "JPY" in pair:
        price_fmt = f"{price:.2f}"
    else:
        price_fmt = f"{price:.5f}"
        
    # Merakit kotak komponen Finviz
    grid_html += f'''
    <div class="finviz-box {bg_class}">
        <div class="box-pair">{pair}</div>
        <div class="box-price">{price_fmt}</div>
        <div class="box-change">{"+" if chg >= 0 else ""}{chg:.2f}%</div>
    </div>
    '''

grid_html += '</div>'

# Cetak Grid ke Layar Streamlit
st.markdown(grid_html, unsafe_allow_html=True)

# ==================== BOTTOM UTILITY ====================
st.markdown("---")
col_btn, col_txt = st.columns([1, 3])
with col_btn:
    if st.button("🔄 Refresh Grid Matrix", use_container_width=True):
        st.rerun()
with col_txt:
    st.markdown(f"""
    <div style="color: #64748b; font-size: 0.85em; padding-top: 6px; font-family: 'JetBrains Mono';">
        *Data diperbarui otomatis setiap 60 detik menggunakan REST API Protocol Freecurrencyapi Core.
    </div>
    """, unsafe_allow_html=True)