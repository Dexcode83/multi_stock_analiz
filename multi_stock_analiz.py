import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup

# 🌐 Sayfa Yapılandırması
st.set_page_config(page_title="Qwen AI Pro Trading Terminal", layout="wide", page_icon="🤖")
st.markdown("""
<style>
    /* TradingView Dark Theme Colors */
    :root {
        --bg-color: #131722;
        --card-bg: #1e222d;
        --text-primary: #d1d4dc;
        --accent-blue: #2962ff;
        --accent-green: #089981;
        --accent-red: #f23645;
    }
    .main {background-color: var(--bg-color);}
    .stApp {background-color: var(--bg-color);}
    div[data-testid="stMetric"] {background-color: var(--card-bg); padding: 10px; border-radius: 8px; border: 1px solid #2a2e39;}
    div[data-testid="stMetricValue"] {font-size: 1.5rem;}
    .tv-container {border: 1px solid #2a2e39; border-radius: 8px; padding: 10px; background: var(--card-bg);}
    .qwen-box {
        background: linear-gradient(135deg, #1e222d 0%, #131722 100%);
        border-left: 4px solid #2962ff;
        padding: 15px;
        border-radius: 6px;
        margin-top: 10px;
    }
    /* Dropdown Styling */
    .stMultiSelect [data-baseweb="tag"] {background-color: #2962ff !important;}
</style>
""", unsafe_allow_html=True)

# 📊 QWEN AI PRO ANALİZ MOTORU
def generate_qwen_pro_insight(symbol, df, pivots):
    """
    Teknik verilere dayalı profesyonel yapay zeka yorumu üretir.
    """
    price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    signal_line = df['Signal'].iloc[-1]
    sma20 = df['SMA_20'].iloc[-1]
    sma50 = df['SMA_50'].iloc[-1]
    
    # Momentum ve Trend Analizi
    trend = "GÜÇLÜ YÜKSELİŞ" if price > sma20 > sma50 else ("YÜKSELİŞ" if price > sma20 else ("YATAY" if abs(price - sma20)/price < 0.02 else "DÜŞÜŞ"))
    
    # RSI Durumu
    rsi_status = "AŞIRI ALIM BÖLGESİ" if rsi > 70 else ("AŞIRI SATIM BÖLGESİ" if rsi < 30 else "NÖTR BÖLGE")
    
    # MACD Sinyali
    macd_signal = "AL SİNYALİ" if macd > signal_line else "SAT SİNYALİ"
    
    # Kritik Seviye Yakınlığı
    r1_dist = abs(pivots['r1'] - price) / price
    s1_dist = abs(pivots['s1'] - price) / price
    proximity = "DİRENÇE YAKIN" if r1_dist < 0.02 else ("DESTEĞE YAKIN" if s1_dist < 0.02 else "ORTA BÖLGE")

    # Yorum Oluşturma
    comment = f"📈 **QWEN AI PRO DEĞERLENDİRMESİ ({symbol})**\n\n"
    comment += f"• **Genel Görünüm:** {trend} trendinde. Fiyat, {sma20:.2f} TL (SMA20) seviyesinin {'üzerinde' if price > sma20 else 'altında'} işlem görüyor.\n"
    comment += f"• **Momentum:** RSI(14) {rsi:.2f} ile {rsi_status}. MACD {macd_signal} üretiyor.\n"
    comment += f"• **Seviye Analizi:** {proximity}. Kırılım hedefi {pivots['r1']:.2f} TL, destek bölgesi {pivots['s1']:.2f} TL.\n\n"
    
    if "GÜÇLÜ YÜKSELİŞ" in trend and "AL" in macd_signal:
        comment += " **ÖNERİ:** Trend güçlü, kırılım onayı beklenerek uzun pozisyon değerlendirilebilir. Stop-loss {s1:.2f} TL altında tutulmalı.".format(s1=pivots['s1'])
    elif "AŞIRI SATIM" in rsi_status and "SAT" in macd_signal:
        comment += "⚠️ **UYARI:** Aşırı satım bölgesinde olası tepki yükselişi beklenebilir, ancak trend zayıf. Dikkatli olunmalı."
    else:
        comment += "⏳ **ÖNERİ:** Belirsizlik yüksek, volatilite artışı bekleniyor. İşlem yapmadan önce {r1:.2f} TL direnç kırılımı veya {s1:.2f} TL desteği test edilmeli.".format(r1=pivots['r1'], s1=pivots['s1'])
        
    return comment

# 📈 TRADINGVIEW PRO GRAFİK
def create_tradingview_chart(df, symbol, pivots):
    """
    TradingView Pro tarzı profesyonel grafik oluşturur.
    """
    # Subplot: Fiyat (55%), RSI (15%), MACD (15%), Hacim (15%)
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        row_heights=[0.55, 0.15, 0.15, 0.15],
        subplot_titles=(f"📊 {symbol} - BIST", "RSI (14)", "MACD (12,26,9)", "HACİM")
    )
    
    # === ANA GRAFİK (MUM + ORTALAMALAR + BB) ===
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Fiyat', increasing_line_color='#089981', decreasing_line_color='#f23645',
        increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
    ), row=1, col=1)
    
    # Hareketli Ortalamalar
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='#2962ff', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='#ff6d00', width=1.5)), row=1, col=1)
    
    # Pivot Seviyeleri
    colors = {'r3':'#ff1744','r2':'#ff5252','r1':'#ff8a80','pivot':'#ffd600','s1':'#69f0ae','s2':'#00e676','s3':'#00c853'}
    for lv, val in pivots.items():
        c = colors.get(lv, '#fff')
        fig.add_hline(y=val, line_color=c, line_dash="dash", line_width=1, row=1, col=1,
                      annotation_text=lv.upper(), annotation_position="top right")
    
    # === RSI ===
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9c27b0', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_color='#f23645', line_dash='dash', line_width=1, row=2, col=1)
    fig.add_hline(y=30, line_color='#089981', line_dash='dash', line_width=1, row=2, col=1)
    fig.add_shape(type="rect", x0=df.index.min(), x1=df.index.max(), y0=70, y1=100, fillcolor="rgba(242, 54, 69, 0.1)", line_width=0, row=2, col=1)
    fig.add_shape(type="rect", x0=df.index.min(), x1=df.index.max(), y0=0, y1=30, fillcolor="rgba(8, 153, 129, 0.1)", line_width=0, row=2, col=1)

    # === MACD ===
    hist_colors = ['#089981' if v > 0 else '#f23645' for v in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name='Histogram', marker_color=hist_colors, opacity=0.5), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#2962ff', width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='#ff6d00', width=2)), row=3, col=1)
    fig.add_hline(y=0, line_color='#787b86', line_dash='dot', line_width=1, row=3, col=1)

    # === HACİM ===
    vol_colors = ['#089981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#f23645' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Hacim', marker_color=vol_colors, opacity=0.6), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Vol_SMA_20'], name='Vol SMA20', line=dict(color='#2962ff', width=1.5, dash='dash')), row=4, col=1)

    # Layout
    fig.update_layout(
        template='plotly_dark', height=900, margin=dict(l=40, r=40, t=50, b=20),
        xaxis_rangeslider_visible=False, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='#131722', paper_bgcolor='#131722',
        font=dict(color='#d1d4dc'),
        hovermode='x unified'
    )
    fig.update_xaxes(showgrid=True, gridcolor='#2a2e39')
    fig.update_yaxes(showgrid=True, gridcolor='#2a2e39')
    
    return fig

# 🔍 HİSSE LİSTESİ YÜKLEME
@st.cache_data(ttl=86400)
def get_bist_tickers():
    try:
        # Wikipedia'dan BIST 100 veya BIST 30 listesini çekmek yerine sabit bir popüler liste kullanalım (Daha hızlı ve stabil)
        # Gerçek bir API yerine, yfinance'ın desteklediği yaygın BIST hisselerini manuel ekliyoruz.
        return ["SAYAS", "THYAO", "GARAN", "AKBNK", "ASELS", "EREGL", "BIMAS", "KCHOL", "SAHOL", "TUPRS", "SISE", "TAVHL", "PGSUS", "HEKTS", "DOHOL", "TOASO", "FROTO", "ARCLK", "MGROS", "YKBNK"]
    except Exception:
        return ["THYAO", "GARAN", "ASELS"]

#  ANA UYGULAMA
def main():
    st.title("🤖 QWEN AI PRO TRADING TERMINAL")
    st.caption("Yapay Zeka Destekli Teknik Analiz & Takas Simülasyonu")

    # Hisse Seçimi
    all_tickers = get_bist_tickers()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # Kullanıcı hem listeden seçebilir hem de manuel giriş yapabilir
        selected_stocks = st.multiselect(
            " Hisse Ara ve Seç (Çoklu Seçim Destekli)",
            options=all_tickers,
            default=["SAYAS"],
            help="Yazmaya başlayarak filtreleme yapabilirsiniz"
        )
    with col2:
        period = st.selectbox(" Periyot", ["1mo", "3mo", "6mo", "1y"], index=2)
        btn_load = st.button("🔄 Analiz Başlat", type="primary", use_container_width=True)

    if not selected_stocks:
        st.info("Lütfen analiz edilecek en az bir hisse seçiniz.")
        return

    # Tablar
    if selected_stocks:
        tabs = st.tabs([f"📈 {s}" for s in selected_stocks])
        
        for i, symbol in enumerate(selected_stocks):
            with tabs[i]:
                # Loading State
                with st.spinner(f'📡 {symbol} verileri ve Qwen AI analizi yükleniyor...'):
                    try:
                        # Veri Çekme
                        ticker = yf.Ticker(f"{symbol}.IS")
                        df = ticker.history(period=period)
                        
                        if df.empty:
                            st.error(f" {symbol} için veri bulunamadı.")
                            continue
                        
                        # Teknik Hesaplamalar
                        df['SMA_20'] = df['Close'].rolling(20).mean()
                        df['SMA_50'] = df['Close'].rolling(50).mean()
                        delta = df['Close'].diff()
                        gain = delta.where(delta > 0, 0).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        df['RSI'] = 100 - (100 / (1 + gain/loss))
                        df['MACD'] = df['Close'].ewm(12).mean() - df['Close'].ewm(26).mean()
                        df['Signal'] = df['MACD'].ewm(9).mean()
                        df['Hist'] = df['MACD'] - df['Signal']
                        df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()
                        
                        # Pivot Hesaplama
                        last_close = df['Close'].iloc[-1]
                        high = df['High'].tail(20).max()
                        low = df['Low'].tail(20).min()
                        pivot = (high + low + last_close) / 3
                        pivots = {
                            'r3': high + 2*(pivot - low), 'r2': pivot + (high - low), 'r1': 2*pivot - low,
                            'pivot': pivot,
                            's1': 2*pivot - high, 's2': pivot - (high - low), 's3': low - 2*(high - pivot)
                        }
                        
                        # UI Bileşenleri
                        st.markdown(f'<div class="tv-container">', unsafe_allow_html=True)
                        
                        # Üst Metrikler
                        c1, c2, c3, c4 = st.columns(4)
                        trend = "BOĞA 🐂" if last_close > df['SMA_20'].iloc[-1] else "AYI 🐻"
                        c1.metric("Fiyat", f"{last_close:.2f} TL")
                        c2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
                        c3.metric("Trend", trend)
                        c4.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")
                        
                        # TradingView Grafik
                        fig = create_tradingview_chart(df, symbol, pivots)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Qwen AI Pro Yorumu
                        insight = generate_qwen_pro_insight(symbol, df, pivots)
                        st.markdown('<div class="qwen-box">', unsafe_allow_html=True)
                        st.markdown(insight)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Yasal Uyarı
                        st.caption("⚠️ Bu analiz eğitim amaçlıdır. Yatırım tavsiyesi değildir. Qwen AI Pro simülasyonu teknik verilerle otomatik oluşturulmuştur.")
                        
                    except Exception as e:
                        st.error(f"⚠️ {symbol} analiz edilirken hata oluştu: {e}")

if __name__ == "__main__":
    main()
