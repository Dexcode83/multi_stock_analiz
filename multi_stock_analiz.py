import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import datetime

# 🌐 Sayfa Yapılandırması
st.set_page_config(page_title="Qwen AI Pro - BIST Terminal", layout="wide", page_icon="🤖")
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stMetric {background-color: #1f2937; padding: 8px; border-radius: 6px; border: 1px solid #374151;}
    .ai-box {
        background: linear-gradient(135deg, #1e222d 0%, #131722 100%);
        border-left: 4px solid #2962ff;
        padding: 15px;
        border-radius: 6px;
        margin: 10px 0 20px 0;
        font-family: 'Segoe UI', sans-serif;
    }
    code {background-color: #1e222d; padding: 4px 6px; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 QWEN AI PRO | BIST TEKNIK ANALİZ TERMINALİ")
st.caption("Gerçek Piyasa Verileri | Yapay Zeka Destekli Dinamik Yorum")

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
    run_btn = st.button("🚀 Analizi Başlat", type="primary", use_container_width=True)

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
        df.index = df.index.tz_localize(None)
        return df, None
    except Exception as e:
        return None, str(e)

# 🧮 Teknik Göstergeler
def calculate_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()
    
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    
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

# 🤖 QWEN AI PRO MOTORU (Dinamik Yorum)
def generate_qwen_insight(symbol, df, pivots):
    price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    macd_val = df['MACD'].iloc[-1]
    macd_sig = df['Signal'].iloc[-1]
    sma20 = df['SMA_20'].iloc[-1]
    
    # 1. Trend Tespiti
    trend = "YÜKSELİŞ" if price > sma20 else "DÜŞÜŞ"
    
    # 2. Momentum
    if rsi > 70: rsi_stat = "Aşırı Alım (Düzeltme Beklenir) ⚠️"
    elif rsi < 30: rsi_stat = "Aşırı Satım (Tepki Yükselişi Olabilir) 🛒"
    else: rsi_stat = "Normal Bölge"
    
    # 3. MACD Sinyali
    signal = "AL" if macd_val > macd_sig else "SAT"
    
    # 4. Seviye Kontrolü
    dist_r1 = (pivots['r1'] - price) / price
    dist_s1 = (price - pivots['s1']) / price
    
    # 📝 Dinamik Metin Üretimi
    text = f"""🤖 <b>QWEN AI PRO ANALİZ ({symbol})</b><br><br>"""
    text += f"📊 <b>Trend:</b> Fiyat SMA20 ({sma20:.2f} TL) seviyesinin {'üzerinde' if price > sma20 else 'altında'}, genel yapı <b>{trend}</b> yönlü.<br>"
    text += f"🚀 <b>Momentum:</b> RSI değeri <b>{rsi:.1f}</b>. Bu, {rsi_stat} bölgesidir.<br>"
    text += f"📡 <b>Sinyal:</b> MACD çizgisi Signal çizgisinin {'üzerinde (POZİTIF)' if signal=='AL' else 'altında (NEGATIF)'}."
    
    # Akıllı Öneri Kısmı
    text += f"<br><br>💡 <b>YAPAY ZEKA DEĞERLENDİRMESİ:</b><br>"
    
    if price > sma20 and rsi < 70 and signal == "AL":
        text += "✅ <b>GÜÇLÜ AL:</b> Trend yükseliş, momentum destekliyor ve kırılım sinyali var. Hedef: R1 ({:.2f} TL).".format(pivots['r1'])
    elif price < sma20 and rsi < 30:
        text += "⚠️ <b>TEMKİLLİ OL:</b> Fiyat düşüş trendinde ancak aşırı satılmış. Kısa vadeli tepki alımı denenebilir ancak ana trend bozucu değil."
    elif price > pivots['r1']:
        text += "🔥 <b>KIRILIM ONAYI:</b> Fiyat R1 direncini ({:.2f} TL) kırmış görünüyor. Yeni hedef R2 ({:.2f} TL).".format(pivots['r1'], pivots['r2'])
    else:
        text += "⏳ <b>BEKLE/GÖR:</b> Net bir sinyal yok. Fiyatın {} bölgesine yaklaşmasını bekle.".format("R1 Direnci" if dist_r1 < dist_s1 else "S1 Desteği")

    return text

# 📈 TradingView Tarzı Grafik
def create_chart(df, symbol, pivots):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                        row_heights=[0.55, 0.22, 0.23],
                        subplot_titles=(f"📊 {symbol} Mum Grafiği", "RSI (14)", "MACD (12,26,9)"))
    
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name='Fiyat',
                                 increasing_line_color='#089981', decreasing_line_color='#f23645'), row=1, col=1)
    
    colors = {'r3':'#ff4444','r2':'#ff6666','r1':'#ff8888','pivot':'#ffff00','s1':'#00ff00','s2':'#00aa00','s3':'#006600'}
    for lv, val in pivots.items():
        fig.add_hline(y=val, line_color=colors.get(lv,'#fff'), line_dash="dash", line_width=1,
                      annotation_text=lv.upper(), annotation_position="top right", row=1, col=1)
        
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#b388ff')), row=2, col=1)
    fig.add_hline(y=70, line_color='red', line_dash='dot', row=2, col=1)
    fig.add_hline(y=30, line_color='green', line_dash='dot', row=2, col=1)
    
    hist_colors = ['#089981' if x > 0 else '#f23645' for x in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name='Histogram', marker_color=hist_colors, opacity=0.6), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#2962ff')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='#ff9800')), row=3, col=1)
    
    fig.update_layout(template='plotly_dark', height=600, margin=dict(l=20,r=20,t=40,b=20),
                      xaxis_rangeslider_visible=False, showlegend=False,
                      title_text="⚠️ Eğitim Amaçlıdır", title_font_size=14)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    return fig

# 🖥️ ANA AKIŞ
if run_btn or stocks:
    with st.spinner('🤖 Qwen AI Pro Verileri işliyor...'):
        all_data = {}
        for s in stocks:
            df, err = fetch_stock_data(s, period)
            if err:
                st.error(f"❌ {s}: {err}")
            else:
                df = calculate_indicators(df)
                if len(df) > 20:
                    all_data[s] = {'df': df, 'pivots': calc_pivots(df)}
    
    if all_
        tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
        for i, (sym, data) in enumerate(all_data.items()):
            with tabs[i]:
                df, pivots = data['df'], data['pivots']
                price = df['Close'].iloc[-1]
                
                # Metrikler
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Fiyat", f"{price:.2f} TL")
                c2.metric("RSI(14)", f"{df['RSI'].iloc[-1]:.2f}")
                c3.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")
                c4.metric("Trend", "Boğa 🐂" if price > df['SMA_50'].iloc[-1] else "Ayı 🐻")
                
                # 1. TradingView Grafik
                st.plotly_chart(create_chart(df, sym, pivots), use_container_width=True)
                
                # 2. QWEN AI PRO YORUMU (Yeni Eklenen Kısım)
                ai_comment = generate_qwen_insight(sym, df, pivots)
                st.markdown(f'<div class="ai-box">{ai_comment}</div>', unsafe_allow_html=True)
                
                # 3. Detaylı Rapor (Eski Halinden Sadeliği Korunmuş)
                st.markdown("### 📋 Detaylı Veriler")
                st.code(f"""
🔴 DİRENÇLER: R1({pivots['r1']:.2f}) | R2({pivots['r2']:.2f}) | R3({pivots['r3']:.2f})
🟢 DESTEKLER: S1({pivots['s1']:.2f}) | S2({pivots['s2']:.2f}) | S3({pivots['s3']:.2f})
⚪ PIVOT: {pivots['pivot']:.2f} TL
                """)
                
                st.divider()
                
        st.warning("⚠️ **YASAL UYARI:** Bu rapor yalnızca eğitim amaçlıdır. Qwen AI Pro otomatik algoritma ile oluşturulmuştur.")
        st.caption(f"📊 Kaynak: Yahoo Finance BIST | Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
