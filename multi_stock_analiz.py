import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import yfinance as yf

# 🌐 Sayfa Yapılandırması - MOBİL OPTİMİZASYON
st.set_page_config(
    page_title="Qwen AI Pro BIST", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# 🎨 MOBİL UYUMLU CSS STİLLERİ
st.markdown("""
<style>
    /* Ana Tema - TradingView Dark */
    .main {background-color: #0e1117;}
    .stApp {background-color: #0e1117;}
    
    /* Yazı Tipleri */
    .stMarkdown, .stMetric, .stExpander {font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;}
    
    /* Metrik Kartları - Mobil Uyumlu */
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 12px 8px;
        border-radius: 8px;
        border: 1px solid #374151;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {font-size: 1.3rem !important;}
    div[data-testid="stMetricLabel"] {font-size: 0.85rem !important; color: #9ca3af;}
    
    /* Kod Blokları */
    code {
        background-color: #1e293b;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.85em;
        color: #e2e8f0;
    }
    
    /* Tab Stilleri - Mobil Dokunmatik */
    button[data-baseweb="tab"] {
        font-size: 0.9rem;
        padding: 12px 16px;
        min-height: 48px;
    }
    
    /* Qwen AI Pro Kutusu */
    .qwen-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
    }
    .qwen-title {
        color: #60a5fa;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .qwen-content {color: #e2e8f0; line-height: 1.5; font-size: 0.9rem;}
    
    /* Sinyal Badge'leri */
    .signal-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px 0;
    }
    .signal-buy {background: #065f46; color: #6ee7b7;}
    .signal-sell {background: #991b1b; color: #fca5a5;}
    .signal-wait {background: #78350f; color: #fcd34d;}
    
    /* Rapor Kutuları */
    .report-section {
        background-color: #1f2937;
        border-radius: 8px;
        padding: 14px;
        margin: 8px 0;
        border: 1px solid #374151;
    }
    
    /* Butonlar - Mobil Dokunmatik */
    .stButton > button {
        width: 100%;
        min-height: 48px;
        font-size: 1rem;
        border-radius: 8px;
    }
    
    /* Input Alanları */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        font-size: 1rem;
        min-height: 44px;
    }
    
    /* Mobil İçin Özel Ayarlar */
    @media (max-width: 768px) {
        .stColumns {flex-wrap: wrap;}
        div[data-testid="column"] {min-width: 100% !important; margin-bottom: 8px;}
        .stMetric {margin-bottom: 8px;}
        h1 {font-size: 1.4rem !important;}
        h2 {font-size: 1.2rem !important;}
        h3 {font-size: 1.05rem !important;}
    }
    
    /* Scrollbar Özelleştirme */
    ::-webkit-scrollbar {width: 6px; height: 6px;}
    ::-webkit-scrollbar-track {background: #0e1117;}
    ::-webkit-scrollbar-thumb {background: #374151; border-radius: 3px;}
    ::-webkit-scrollbar-thumb:hover {background: #4b5563;}
</style>
""", unsafe_allow_html=True)

# 📱 BAŞLIK - MOBİL UYUMLU
st.markdown('<div style="text-align: center; padding: 8px 0;">', unsafe_allow_html=True)
st.title("🤖 QWEN AI PRO | BİST ANALİZ")
st.caption("📱 Mobil Optimizasyon | Gerçek Veri | TradingView Grafik")
st.markdown('</div>', unsafe_allow_html=True)

# 🔍 GİRİŞ ALANI - MOBİL DOSTU
col1, col2 = st.columns([2, 1])
with col1:
    stock_input = st.text_area(
        "📋 Hisse Kodları",
        value="SAYAS\nTHYAO\nGARAN\nASELS",
        height=60,
        help="Virgül, boşluk veya yeni satır ile ayırın"
    )
with col2:
    period = st.selectbox("📅 Periyot", ["1mo", "3mo", "6mo", "1y"], index=2)
    run_btn = st.button("🚀 Analiz Başlat", type="primary", use_container_width=True)

# Parse
stocks = [s.strip().upper() for s in stock_input.replace(',', '\n').split('\n') if s.strip()]

if not stocks:
    st.info("💡 Lütfen en az bir hisse kodu giriniz.")
    st.stop()

# 📥 VERİ ÇEKME
@st.cache_data(ttl=300)
def fetch_data(symbol, period="6mo"):
    try:
        df = yf.Ticker(f"{symbol}.IS").history(period=period)
        if df.empty:
            return None, "Veri yok"
        df.index = df.index.tz_localize(None)
        return df, None
    except Exception as e:
        return None, str(e)

# 🧮 TEKNİK GÖSTERGELER
def calc_indicators(df):
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

# 📐 PİVOT HESAPLAMA
def calc_pivots(df):
    recent = df.tail(20)
    high, low, close = recent['High'].max(), recent['Low'].min(), df['Close'].iloc[-1]
    pivot = (high + low + close) / 3
    return {
        'r3': high + 2*(pivot - low), 'r2': pivot + (high - low), 'r1': 2*pivot - low,
        'pivot': pivot,
        's1': 2*pivot - high, 's2': pivot - (high - low), 's3': low - 2*(high - pivot)
    }

# 📈 TRADINGVIEW GRAFİK
def create_chart(df, symbol, pivots):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                        row_heights=[0.55, 0.22, 0.23],
                        subplot_titles=(f"📊 {symbol}", "RSI (14)", "MACD"))
    
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
    
    fig.update_layout(template='plotly_dark', height=550, margin=dict(l=15,r=15,t=30,b=15),
                      xaxis_rangeslider_visible=False, showlegend=False,
                      title_text="⚠️ Eğitim Amaçlıdır", title_font_size=12)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
    return fig

# 🤖 QWEN AI PRO YORUM MOTORU
def generate_qwen_commentary(symbol, report, df):
    price, rsi, macd = report['price'], report['rsi'], report['macd']
    trend, signal = report['trend'], report['signal']
    pivots = report['pivots']['classic']
    
    # Sinyal badge
    badge = '<span class="signal-badge signal-buy">🟢 AL</span>' if signal=="AL" else \
            '<span class="signal-badge signal-sell">🔴 SAT</span>' if signal=="SAT" else \
            '<span class="signal-badge signal-wait">🟡 BEKLE</span>'
    
    # Yorumlar
    trend_txt = f"{'📈' if trend=='Boğa' else '📉'} {trend} trend. Fiyat SMA50 {'üstünde' if trend=='Boğa' else 'altında'}."
    rsi_txt = f"RSI {rsi:.1f}: {'⚠️ Aşırı Alım' if rsi>70 else '🛒 Aşırı Satım' if rsi<30 else '📊 Nötr'}."
    macd_txt = f"MACD: {'📡 Pozitif momentum' if macd>0 else '📡 Negatif momentum'}."
    
    # Seviye
    dist_r1 = (pivots['r1']-price)/price*100
    dist_s1 = (price-pivots['s1'])/price*100
    if dist_r1 < 2:
        level_txt = f"🎯 R1 ({pivots['r1']:.2f} TL) yakınında. Kırılımda hedef R2: {pivots['r2']:.2f} TL."
    elif dist_s1 < 2:
        level_txt = f"🎯 S1 ({pivots['s1']:.2f} TL) yakınında. Kırılımda hedef S2: {pivots['s2']:.2f} TL."
    else:
        level_txt = f"📍 R1-S1 aralığında konsolidasyon."
    
    # Hacim
    vol_txt = f"📦 Hacim: {report['volume_ratio']:.2f}x ortalama. {'🔥 Yüksek' if report['volume_ratio']>1.2 else '➡️ Normal' if report['volume_ratio']>0.8 else '💤 Düşük'}."
    
    # Öneri
    if trend=="Boğa" and rsi<70 and signal=="AL":
        rec = f"✅ <b>AL:</b> {pivots['r1']:.2f} TL kırılımı ile R2 ({pivots['r2']:.2f} TL) hedeflenir. Stop: {pivots['s1']:.2f} TL."
    elif trend=="Ayı" and rsi<30:
        rec = "⚠️ <b>Temkinli:</b> Aşırı satım tepkisi beklenebilir, ana trend düşüş. Kısa vadeli işlem."
    elif price > pivots['r1']:
        rec = f"🔥 <b>Kırılım:</b> R1 aşıldı! Hedef R2 ({pivots['r2']:.2f} TL). Hacim onayı ile pozisyon artırılabilir."
    else:
        rec = f"⏳ <b>Bekle:</b> Net yön yok. {pivots['r1']:.2f} TL veya {pivots['s1']:.2f} TL kırılımı beklenmeli."
    
    return f"""
    <div class="qwen-box">
        <div class="qwen-title">🤖 Qwen AI Pro | {symbol} {badge}</div>
        <div class="qwen-content">
            <p><b>Trend:</b> {trend_txt}</p>
            <p><b>Momentum:</b> {rsi_txt} | {macd_txt}</p>
            <p><b>Seviye:</b> {level_txt}</p>
            <p><b>Hacim:</b> {vol_txt}</p>
            <p style="margin-top:10px;padding-top:10px;border-top:1px solid #334155;"><b>💡 Strateji:</b> {rec}</p>
        </div>
    </div>
    """

# 📊 RAPOR OLUŞTURMA
def generate_report(symbol, data):
    df = data['df']
    pivots = calc_pivots(df)
    price = df['Close'].iloc[-1]
    rsi, macd = df['RSI'].iloc[-1], df['MACD'].iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / df['Vol_SMA_20'].iloc[-1] if df['Vol_SMA_20'].iloc[-1] > 0 else 1
    
    trend = "Boğa" if price > df['SMA_50'].iloc[-1] else "Ayı"
    signal = "AL" if macd > 0 and rsi < 70 else ("SAT" if macd < 0 else "BEKLE")
    rsi_stat = "Aşırı Alım" if rsi > 70 else ("Aşırı Satım" if rsi < 30 else "Nötr")
    vol_stat = "Yüksek" if vol_ratio > 1.5 else ("Düşük" if vol_ratio < 0.7 else "Normal")
    
    bull_prob = min(85, max(25, int(50 + (rsi-50)*0.4 + (1 if macd>0 else -1)*10)))
    r_or_bull = round((pivots['r2']-price)/(price-pivots['s1']), 1) if price > pivots['s1'] else 0
    r_or_bear = round((price-pivots['s2'])/(pivots['r1']-price), 1) if pivots['r1'] > price else 0
    
    return {
        'price': price, 'rsi': rsi, 'macd': macd, 'trend': trend, 'signal': signal,
        'rsi_status': rsi_stat, 'volume_ratio': vol_ratio, 'volume_status': vol_stat,
        'bull_prob': bull_prob, 'r_or_bull': r_or_bull, 'r_or_bear': r_or_bear,
        'pivots': {'classic': pivots}, 'high_52w': df['High'].max(), 'avg_volume': df['Vol_SMA_20'].iloc[-1]
    }

# 🖥️ ANA AKIŞ
if run_btn or stocks:
    with st.spinner('📡 Veriler yükleniyor...'):
        all_data = {}
        for s in stocks:
            df, err = fetch_data(s, period)
            if err:
                st.error(f"❌ {s}: {err}")
            else:
                df = calc_indicators(df)
                if len(df) > 20:
                    all_data[s] = {'df': df}
    
    if all_data:
        st.success(f"✅ {len(all_data)} hisse yüklendi")
        
        # TABLAR - MOBİL UYUMLU
        tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
        
        for i, (sym, data) in enumerate(all_data.items()):
            with tabs[i]:
                df = data['df']
                pivots = calc_pivots(df)
                report = generate_report(sym, data)
                
                # METRİKLER - MOBİL GRID
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Fiyat", f"{report['price']:.2f} TL")
                c2.metric("📊 RSI", f"{report['rsi']:.2f}", report['rsi_status'])
                c3.metric("📡 MACD", f"{report['macd']:.2f}", report['signal'])
                c4.metric("📈 Trend", report['trend'], "↗️" if report['trend']=='Boğa' else "↘️")
                
                # GRAFİK
                st.plotly_chart(create_chart(df, sym, pivots), use_container_width=True)
                
                # QWEN AI PRO YORUM
                st.markdown(generate_qwen_commentary(sym, report, df), unsafe_allow_html=True)
                
                # RAPOR BÖLÜMLERİ - MOBİL UYUMLU
                with st.expander("📋 Detaylı Analiz", expanded=False):
                    st.markdown(f"""
                    <div class="report-section">
                    <b>🔴 Dirençler:</b> R1:{pivots['r1']:.2f} | R2:{pivots['r2']:.2f} | R3:{pivots['r3']:.2f} TL<br>
                    <b>🟢 Destekler:</b> S1:{pivots['s1']:.2f} | S2:{pivots['s2']:.2f} | S3:{pivots['s3']:.2f} TL<br>
                    <b>⚪ Pivot:</b> {pivots['pivot']:.2f} TL
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.code(f"""
🐂 BOĞA: {pivots['r1']:.2f} TL kırılım → H1:{pivots['r2']:.2f} | Stop:{pivots['s1']:.2f} | R:Ö 1:{report['r_or_bull']}
🐻 AYI: {pivots['s1']:.2f} TL kaybı → H1:{pivots['s2']:.2f} | Stop:{pivots['r1']:.2f} | R:Ö 1:{report['r_or_bear']}
                    """)
                
                st.divider()
    
    # FOOTER
    st.markdown("---")
    st.warning("⚠️ **Yasal Uyarı:** Eğitim amaçlıdır. Yatırım tavsiyesi değildir.")
    st.caption(f"📊 Yahoo Finance BIST | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
else:
    st.info("👆 Hisse kodlarını girip 'Analiz Başlat' butonuna tıklayın")
