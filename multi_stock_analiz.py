import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import yfinance as yf

# 🌐 Sayfa Yapılandırması
st.set_page_config(
    page_title="Qwen AI Pro BIST", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# 🎨 YÜKSEK KONTRASTLI CSS - OKUNABİLİR YAZILAR
st.markdown("""
<style>
    /* ===== ANA TEMA - SİYAH ARKA, BEYAZ YAZI ===== */
    .main {background-color: #000000 !important;}
    .stApp {background-color: #000000 !important;}
    
    /* ===== METİN RENKLERİ - YÜKSEK KONTRAST ===== */
    body, .stMarkdown, .stMetric, .stExpander, .stTabs, 
    .stButton, .stTextInput, .stTextArea, .stSelectbox,
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* İkincil metinler (açık gri) */
    .stCaption, .stHelp, small, .stMarkdown p {
        color: #d1d5db !important;
    }
    
    /* ===== METRİK KARTLARI ===== */
    div[data-testid="stMetric"] {
        background-color: #1a1a1a;
        padding: 12px 8px;
        border-radius: 8px;
        border: 1px solid #404040;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #a3a3a3 !important;
    }
    
    /* ===== KOD BLOKLARI - OKUNABİLİR ===== */
    pre, code, .stCode {
        background-color: #1a1a1a !important;
        color: #e5e7eb !important;
        border: 1px solid #404040 !important;
    }
    code {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    /* ===== TAB STİLLERİ ===== */
    button[data-baseweb="tab"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        font-size: 0.9rem;
        padding: 12px 16px;
        min-height: 48px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
    }
    
    /* ===== QWEN AI PRO KUTUSU - YÜKSEK KONTRAST ===== */
    .qwen-box {
        background: #1a1a1a;
        border: 2px solid #3b82f6;
        border-left: 5px solid #60a5fa;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
    }
    .qwen-title {
        color: #93c5fd !important;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .qwen-content {
        color: #ffffff !important;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .qwen-content p {
        color: #f3f4f6 !important;
        margin: 6px 0;
    }
    .qwen-content b, .qwen-content strong {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* ===== SİNYAL BADGE'LERİ - PARLAK RENKLER ===== */
    .signal-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 2px 0;
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .signal-buy {
        background: linear-gradient(135deg, #059669, #10b981);
        border: 1px solid #34d399;
    }
    .signal-sell {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        border: 1px solid #f87171;
    }
    .signal-wait {
        background: linear-gradient(135deg, #b45309, #f59e0b);
        border: 1px solid #fbbf24;
    }
    
    /* ===== RAPOR KUTULARI ===== */
    .report-section {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 14px;
        margin: 8px 0;
        border: 1px solid #404040;
        color: #ffffff !important;
    }
    .report-section b, .report-section strong {
        color: #60a5fa !important;
    }
    
    /* ===== BUTONLAR - MOBİL DOKUNMATİK ===== */
    .stButton > button {
        width: 100%;
        min-height: 48px;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5);
    }
    
    /* ===== INPUT ALANLARI ===== */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        font-size: 1rem;
        min-height: 44px;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #9ca3af !important;
    }
    
    /* ===== EXPANDER (AÇILIR KUTU) ===== */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
    }
    .streamlit-expanderContent {
        background-color: #0f0f0f !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* ===== TABLOLAR ===== */
    table {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
    }
    th {
        background-color: #252525 !important;
        color: #93c5fd !important;
        border: 1px solid #404040 !important;
    }
    td {
        background-color: #1a1a1a !important;
        color: #f3f4f6 !important;
        border: 1px solid #404040 !important;
    }
    
    /* ===== ALERT / WARNING / INFO BOX ===== */
    .stAlert {
        background-color: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stAlert h4 {
        color: #fbbf24 !important;
    }
    .stAlert p {
        color: #f3f4f6 !important;
    }
    
    /* ===== SUCCESS BOX ===== */
    .success-box {
        background-color: #064e3b !important;
        border: 2px solid #10b981 !important;
        border-left: 5px solid #34d399 !important;
        color: #ffffff !important;
        padding: 12px;
        border-radius: 8px;
    }
    
    /* ===== ERROR BOX ===== */
    .error-box {
        background-color: #7f1d1d !important;
        border: 2px solid #ef4444 !important;
        border-left: 5px solid #f87171 !important;
        color: #ffffff !important;
        padding: 12px;
        border-radius: 8px;
    }
    
    /* ===== MOBİL ÖZEL AYARLAR ===== */
    @media (max-width: 768px) {
        .stColumns {flex-wrap: wrap;}
        div[data-testid="column"] {min-width: 100% !important; margin-bottom: 10px;}
        .stMetric {margin-bottom: 10px;}
        h1 {font-size: 1.5rem !important;}
        h2 {font-size: 1.25rem !important;}
        h3 {font-size: 1.1rem !important;}
        .qwen-title {font-size: 1rem !important;}
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {width: 8px; height: 8px;}
    ::-webkit-scrollbar-track {background: #000000;}
    ::-webkit-scrollbar-thumb {background: #404040; border-radius: 4px;}
    ::-webkit-scrollbar-thumb:hover {background: #60a5fa;}
    
    /* ===== DIVIDER ÇİZGİSİ ===== */
    hr {
        border-color: #404040 !important;
        opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)

# 📱 BAŞLIK
st.markdown('<div style="text-align: center; padding: 10px 0;">', unsafe_allow_html=True)
st.title("🤖 QWEN AI PRO | BİST ANALİZ")
st.caption("📱 Mobil Uyumlu | ⚫ Siyah Tema | 📊 Gerçek Veri")
st.markdown('</div>', unsafe_allow_html=True)

# 🔍 GİRİŞ ALANI
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
            return None, "Veri bulunamadı"
        df.index = df.index.tz_localize(None)
        return df, None
    except Exception as e:
        return None, f"Hata: {str(e)}"

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
                                 increasing_line_color='#10b981', decreasing_line_color='#ef4444'), row=1, col=1)
    
    colors = {'r3':'#ef4444','r2':'#f87171','r1':'#fca5a5','pivot':'#fbbf24','s1':'#34d399','s2':'#10b981','s3':'#059669'}
    for lv, val in pivots.items():
        fig.add_hline(y=val, line_color=colors.get(lv,'#9ca3af'), line_dash="dash", line_width=1.5,
                      annotation_text=lv.upper(), annotation_position="top right", 
                      annotation_font_color='#ffffff', annotation_font_size=9, row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a78bfa', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_color='#ef4444', line_dash='dot', line_width=1.5, row=2, col=1)
    fig.add_hline(y=30, line_color='#10b981', line_dash='dot', line_width=1.5, row=2, col=1)
    fig.add_hline(y=50, line_color='#6b7280', line_dash='dash', line_width=1, row=2, col=1)
    
    hist_colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name='Histogram', marker_color=hist_colors, opacity=0.7), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#60a5fa', width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='#fbbf24', width=2)), row=3, col=1)
    fig.add_hline(y=0, line_color='#6b7280', line_dash='dot', line_width=1, row=3, col=1)
    
    fig.update_layout(
        template='plotly_dark', height=500, margin=dict(l=10,r=10,t=25,b=10),
        xaxis_rangeslider_visible=False, showlegend=False,
        title_text="⚠️ Eğitim Amaçlıdır", title_font_size=11, title_font_color='#9ca3af',
        plot_bgcolor='#000000', paper_bgcolor='#000000',
        font=dict(color='#ffffff', size=10)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#333333', linecolor='#666666')
    fig.update_yaxes(showgrid=True, gridcolor='#333333', linecolor='#666666')
    return fig

# 🤖 QWEN AI PRO YORUM MOTORU
def generate_qwen_commentary(symbol, report, df):
    price, rsi, macd = report['price'], report['rsi'], report['macd']
    trend, signal = report['trend'], report['signal']
    pivots = report['pivots']['classic']
    
    badge = '<span class="signal-badge signal-buy">🟢 AL</span>' if signal=="AL" else \
            '<span class="signal-badge signal-sell">🔴 SAT</span>' if signal=="SAT" else \
            '<span class="signal-badge signal-wait">🟡 BEKLE</span>'
    
    trend_txt = f"{'📈' if trend=='Boğa' else '📉'} <b>{trend}</b> trend. Fiyat SMA50 {'<span style=\"color:#10b981\">üstünde</span>' if trend=='Boğa' else '<span style=\"color:#ef4444\">altında</span>'}."
    rsi_txt = f"RSI {rsi:.1f}: {'<span style=\"color:#fbbf24\">⚠️ Aşırı Alım</span>' if rsi>70 else '<span style=\"color:#34d399\">🛒 Aşırı Satım</span>' if rsi<30 else '📊 Nötr'}."
    macd_txt = f"MACD: {'<span style=\"color:#10b981\">📡 Pozitif</span>' if macd>0 else '<span style=\"color:#ef4444\">📡 Negatif</span>'} momentum."
    
    dist_r1 = (pivots['r1']-price)/price*100
    dist_s1 = (price-pivots['s1'])/price*100
    if dist_r1 < 2:
        level_txt = f"🎯 R1 ({pivots['r1']:.2f} TL) yakınında. Kırılımda hedef R2: <b style=\"color:#34d399\">{pivots['r2']:.2f} TL</b>."
    elif dist_s1 < 2:
        level_txt = f"🎯 S1 ({pivots['s1']:.2f} TL) yakınında. Kırılımda hedef S2: <b style=\"color:#ef4444\">{pivots['s2']:.2f} TL</b>."
    else:
        level_txt = f"📍 R1-S1 aralığında konsolidasyon."
    
    vol_txt = f"📦 Hacim: {report['volume_ratio']:.2f}x ortalama. {'<span style=\"color:#fbbf24\">🔥 Yüksek</span>' if report['volume_ratio']>1.2 else '➡️ Normal' if report['volume_ratio']>0.8 else '💤 Düşük'}."
    
    if trend=="Boğa" and rsi<70 and signal=="AL":
        rec = f"✅ <b style=\"color:#10b981\">AL:</b> {pivots['r1']:.2f} TL kırılımı ile R2 ({pivots['r2']:.2f} TL) hedeflenir. Stop: {pivots['s1']:.2f} TL."
    elif trend=="Ayı" and rsi<30:
        rec = "⚠️ <b style=\"color:#fbbf24\">Temkinli:</b> Aşırı satım tepkisi beklenebilir, ana trend düşüş. Kısa vadeli işlem."
    elif price > pivots['r1']:
        rec = f"🔥 <b style=\"color:#fbbf24\">Kırılım:</b> R1 aşıldı! Hedef R2 ({pivots['r2']:.2f} TL). Hacim onayı ile pozisyon artırılabilir."
    else:
        rec = f"⏳ <b style=\"color:#93c5fd\">Bekle:</b> Net yön yok. {pivots['r1']:.2f} TL veya {pivots['s1']:.2f} TL kırılımı beklenmeli."
    
    return f"""
    <div class="qwen-box">
        <div class="qwen-title">🤖 Qwen AI Pro | {symbol} {badge}</div>
        <div class="qwen-content">
            <p>{trend_txt}</p>
            <p>{rsi_txt} | {macd_txt}</p>
            <p>{level_txt}</p>
            <p>{vol_txt}</p>
            <p style="margin-top:12px;padding-top:12px;border-top:1px solid #404040;"><b>💡 Strateji:</b> {rec}</p>
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
    
    if all_
        st.success(f"✅ {len(all_data)} hisse yüklendi")
        
        tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
        
        for i, (sym, data) in enumerate(all_data.items()):
            with tabs[i]:
                df = data['df']
                pivots = calc_pivots(df)
                report = generate_report(sym, data)
                
                # METRİKLER
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Fiyat", f"{report['price']:.2f} TL")
                c2.metric("📊 RSI", f"{report['rsi']:.2f}", report['rsi_status'])
                c3.metric("📡 MACD", f"{report['macd']:.2f}", report['signal'])
                c4.metric("📈 Trend", report['trend'], "↗️" if report['trend']=='Boğa' else "↘️")
                
                # GRAFİK
                st.plotly_chart(create_chart(df, sym, pivots), use_container_width=True)
                
                # QWEN AI PRO YORUM
                st.markdown(generate_qwen_commentary(sym, report, df), unsafe_allow_html=True)
                
                # DETAYLI RAPOR
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
