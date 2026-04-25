import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import yfinance as yf
import time

# 🌐 Sayfa Yapılandırması
st.set_page_config(
    page_title="TradingView Pro - BIST Analiz", 
    layout="wide", 
    page_icon="📊"
)

st.markdown("""
<style>
    .main {background-color: #131722;}
    .stMarkdown {font-family: 'Segoe UI', sans-serif;}
    code {background-color: #1E222D; padding: 3px 6px; border-radius: 4px;}
    .tradingview-header {
        background: linear-gradient(90deg, #131722 0%, #1E222D 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2962FF;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.title("📊 TRADINGVIEW PRO - BIST TEKNİK ANALİZ PLATFORMU")
st.markdown('<div class="tradingview-header">Gerçek Piyasa Verileri | Profesyonel İndikatörler | 5 Panel Grafik</div>', unsafe_allow_html=True)

# Giriş kontrolleri
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    stock_input = st.text_area(
        "Hisse Kodları",
        value="SAYAS\nTHYAO\nGARAN\nASELS",
        height=60
    )
with col2:
    period = st.selectbox("Periyot", ["1mo", "3mo", "6mo", "1y"], index=2)
with col3:
    interval = st.selectbox("Aralık", ["1d", "1wk"], index=0)
with col4:
    refresh = st.button("🔄 Yenile", type="primary")

stocks = [s.strip().upper() for s in stock_input.replace(',', '\n').split('\n') if s.strip()]

# Veri çekme fonksiyonu
@st.cache_data(ttl=300)
def fetch_data(symbol, period="6mo", interval="1d"):
    try:
        ticker = yf.Ticker(f"{symbol}.IS")
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None, "Veri yok"
        return df, None
    except Exception as e:
        return None, str(e)

# Teknik indikatörler
def calculate_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    
    # Bollinger
    df['BB_middle'] = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    df['Volume_SMA_20'] = df['Volume'].rolling(20).mean()
    return df

# Pivot hesaplama
def calc_pivots(df):
    recent = df.tail(20)
    high, low, close = recent['High'].max(), recent['Low'].min(), df['Close'].iloc[-1]
    pivot = (high + low + close) / 3
    return {
        'classic': {
            'pivot': pivot,
            'r1': 2*pivot - low,
            's1': 2*pivot - high,
            'r2': pivot + (high - low),
            's2': pivot - (high - low),
            'r3': high + 2*(pivot - low),
            's3': low - 2*(high - pivot)
        }
    }

# TradingView grafik fonksiyonu (yukarıdaki kodu buraya yapıştırın)
def create_tradingview_chart(df, symbol, pivots):
    # ... yukarıdaki create_tradingview_chart fonksiyonu ...
    pass

# Ana uygulama
if stocks:
    with st.spinner('Veriler yükleniyor...'):
        all_data = {}
        for stock in stocks:
            df, error = fetch_data(stock, period, interval)
            if error is None:
                df = calculate_indicators(df)
                pivots = calc_pivots(df)
                all_data[stock] = {'df': df, 'pivots': pivots}
        
        if not all_data:
            st.error("Veri çekilemedi!")
            st.stop()
    
    # Tab yapısı
    tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
    
    for i, (symbol, data) in enumerate(all_data.items()):
        with tabs[i]:
            st.subheader(f"🎯 {symbol} - TRADINGVIEW PRO ANALİZ")
            
            # Metrikler
            c1, c2, c3, c4, c5 = st.columns(5)
            price = data['df']['Close'].iloc[-1]
            rsi = data['df']['RSI'].iloc[-1]
            macd = data['df']['MACD'].iloc[-1]
            
            c1.metric("Fiyat", f"{price:.2f} TL")
            c2.metric("RSI", f"{rsi:.2f}")
            c3.metric("MACD", f"{macd:.2f}")
            c4.metric("Trend", "Boğa" if price > data['df']['SMA_50'].iloc[-1] else "Ayı")
            c5.metric("Hacim", f"{data['df']['Volume'].iloc[-1]/1e6:.2f}M")
            
            # TradingView grafik
            fig = create_tradingview_chart(data['df'], symbol, data['pivots'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analiz raporu
            st.markdown("### 📋 Analiz Raporu")
            st.code(f"""
Pivot: {data['pivots']['classic']['pivot']:.2f} TL
Dirençler: R1={data['pivots']['classic']['r1']:.2f} | R2={data['pivots']['classic']['r2']:.2f}
Destekler: S1={data['pivots']['classic']['s1']:.2f} | S2={data['pivots']['classic']['s2']:.2f}
            """)

st.warning("⚠️ Eğitim Amaçlıdır - Yatırım Tavsiyesi Değildir")
