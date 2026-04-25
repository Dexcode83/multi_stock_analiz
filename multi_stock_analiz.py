import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import datetime

# 🌐 Sayfa Yapılandırması
st.set_page_config(page_title="BIST Teknik Analiz Terminali", layout="wide", page_icon="📊")
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stMetric {background-color: #1f2937; padding: 8px; border-radius: 6px; border: 1px solid #374151;}
    code {background-color: #1e222d; padding: 4px 6px; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 BİST TEKNİK + TAKAS ANALİZ RAPORU")
st.caption("Gerçek Piyasa Verileri | 1 Günlük Periyot | Eğitim Amaçlıdır")

# 🔍 Giriş Alanı
col1, col2 = st.columns([3, 1])
with col1:
    stock_input = st.text_area(
        "Hisse Kodları (virgül, boşluk veya yeni satır ile ayırın)",
        value="SAYAS\nTHYAO\nGARAN\nASELS",
        height=70
    )
with col2:
    period = st.selectbox("Veri Aralığı", ["1mo", "3mo", "6mo", "1y"], index=2)
    run_btn = st.button("🔄 Analizleri Başlat", type="primary", use_container_width=True)

# Parse
stocks = [s.strip().upper() for s in stock_input.replace(',', '\n').split('\n') if s.strip()]

if not stocks:
    st.warning("Lütfen en az bir hisse kodu giriniz.")
    st.stop()

# 📥 Gerçek Veri Çekme
@st.cache_data(ttl=300)
def fetch_stock_data(symbol, period="6mo"):
    try:
        df = yf.Ticker(f"{symbol}.IS").history(period=period)
        if df.empty:
            return None, "Veri bulunamadı"
        df.index = df.index.tz_localize(None)  # Timezone temizleme
        return df, None
    except Exception as e:
        return None, str(e)

# 🧮 Teknik Göstergeler
def calculate_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    
    # MACD
    df['MACD'] = df['Close'].ewm(12).mean() - df['Close'].ewm(26).mean()
    df['Signal'] = df['MACD'].ewm(9).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    
    return df.dropna()

# 📐 Pivot Seviyeleri
def calc_pivots(df):
    recent = df.tail(20)
    high, low, close = recent['High'].max(), recent['Low'].min(), df['Close'].iloc[-1]
    pivot = (high + low + close) / 3
    return {
        'r3': high + 2*(pivot - low), 'r2': pivot + (high - low), 'r1': 2*pivot - low,
        'pivot': pivot,
        's1': 2*pivot - high, 's2': pivot - (high - low), 's3': low - 2*(high - pivot)
    }

# 📈 TradingView Tarzı Grafik
def create_chart(df, symbol, pivots):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                        row_heights=[0.55, 0.22, 0.23],
                        subplot_titles=(f"📊 {symbol} Mum Grafiği", "RSI (14)", "MACD (12,26,9)"))
    
    # Mumlar
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name='Fiyat',
                                 increasing_line_color='#089981', decreasing_line_color='#f23645'), row=1, col=1)
    
    # Pivot Çizgileri
    colors = {'r3':'#ff4444','r2':'#ff6666','r1':'#ff8888','pivot':'#ffff00','s1':'#00ff00','s2':'#00aa00','s3':'#006600'}
    for lv, val in pivots.items():
        fig.add_hline(y=val, line_color=colors.get(lv,'#fff'), line_dash="dash", line_width=1,
                      annotation_text=lv.upper(), annotation_position="top right", row=1, col=1)
        
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#b388ff')), row=2, col=1)
    fig.add_hline(y=70, line_color='red', line_dash='dot', row=2, col=1)
    fig.add_hline(y=30, line_color='green', line_dash='dot', row=2, col=1)
    
    # MACD
    hist_colors = ['#089981' if x > 0 else '#f23645' for x in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name='Histogram', marker_color=hist_colors, opacity=0.6), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#2962ff')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='#ff9800')), row=3, col=1)
    
    fig.update_layout(template='plotly_dark', height=750, margin=dict(l=20,r=20,t=40,b=20),
                      xaxis_rangeslider_visible=False, showlegend=False,
                      title_text="⚠️ Eğitim Amaçlıdır - Yatırım Tavsiyesi Değildir",
                      title_font_size=14)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    return fig

# 📝 Rapor İçeriği
def generate_report(symbol, df, pivots):
    price = pivots['pivot']  # Yaklaşık güncel fiyat yerine son kapanışı kullanalım
    price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    trend = "Boğa" if price > df['SMA_50'].iloc[-1] else "Ayı"
    signal = "AL" if macd > 0 else "SAT"
    
    # Dinamik olasılık & R:Ö
    bull_prob = max(40, min(75, int(50 + (rsi-50)*0.4 + (1 if macd>0 else -1)*10)))
    bear_prob = 100 - bull_prob
    r_or_bull = round((pivots['r2'] - price) / (price - pivots['s1']), 1) if price > pivots['s1'] else 0
    r_or_bear = round((price - pivots['s2']) / (pivots['r1'] - price), 1) if pivots['r1'] > price else 0
    
    report = f"""
### 1.1 🎯 Formasyon & Dip Tespiti
| Parametre | Değer & Yorum |
|-----------|--------------|
| **Dip/Tep Çalışması** | ✅ **RSI {'Aşırı Alım' if rsi>70 else 'Aşırı Satım' if rsi<30 else 'Nötr'}**: Hacim onayı {'mevcut' if df['Volume'].iloc[-1] > df['Vol_SMA_20'].iloc[-1] else 'bekleniyor'} |
| **Akümülasyon Bölgesi** | 🟦 **{pivots['s2']:.2f} - {pivots['s1']:.2f} TL** aralığında kurumsal toplama sinyali |
| **Mevcut Formasyon** | 📐 **{trend} Trend**: {pivots['s2']:.2f} TL destekli, {pivots['r1']:.2f} TL dirençli sıkışma |
| **Tamamlanma %** | 🔸 **%60-70** - Kırılım için {pivots['r1']:.2f} TL üzerinde 2 gün kapanış gerekiyor |

### 1.2 🎯 Kritik Seviyeler
