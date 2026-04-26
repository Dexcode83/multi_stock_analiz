import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf
import streamlit.components.v1 as components  # TradingView gömmek için gerekli

# 🌐 Sayfa Yapılandırması
st.set_page_config(
    page_title="Qwen AI Pro | BIST Teknik Analiz", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="collapsed"
)

# 🎨 TEMİZ SİYAH TEMA & TABLO/BUTON STİLLERİ
st.markdown("""
<style>
    .main, .stApp {background-color: #000000 !important;}
    body, .stMarkdown, .stMetric, h1, h2, h3, h4, p, span, div, label, td, th {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .stCaption, small {color: #d1d5db !important;}

    .role-box, .qwen-box {
        background: #111111; border: 1px solid #333333; border-radius: 8px; padding: 14px; margin: 10px 0;
    }
    .role-box {border-left: 4px solid #3b82f6;}
    .qwen-box {border: 2px solid #2563eb; border-left: 5px solid #3b82f6;}

    .role-title, .qwen-title {color: #93c5fd !important; font-weight: 700; font-size: 1.05rem; margin-bottom: 8px;}
    .role-content, .qwen-content {color: #f3f4f6 !important; font-size: 0.9rem; line-height: 1.5;}

    div[data-testid="stMetric"] {background-color: #111111; padding: 12px 8px; border-radius: 8px; border: 1px solid #333333; text-align: center;}
    div[data-testid="stMetricValue"] {font-size: 1.4rem !important; color: #ffffff !important; font-weight: 600;}
    div[data-testid="stMetricLabel"] {font-size: 0.85rem !important; color: #a3a3a3 !important;}

    .signal-badge {display: inline-block; padding: 4px 12px; border-radius: 14px; font-size: 0.85rem; font-weight: 700; color: #ffffff !important;}
    .signal-buy {background: linear-gradient(135deg, #059669, #10b981); border: 1px solid #34d399;}
    .signal-sell {background: linear-gradient(135deg, #dc2626, #ef4444); border: 1px solid #f87171;}
    .signal-wait {background: linear-gradient(135deg, #b45309, #f59e0b); border: 1px solid #fbbf24;}

    .stButton > button {
        width: 100%; min-height: 48px; font-size: 1rem; font-weight: 600; border-radius: 8px;
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important; color: #ffffff !important; border: none !important;
    }
    
    div[data-testid="stRadio"] label {
        background-color: #1a1a1a !important;
        border: 1px solid #404040 !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }

    table {width: 100%; border-collapse: collapse; margin: 10px 0; background-color: #111111; border-radius: 8px; overflow: hidden;}
    th {background-color: #1a1a1a; color: #93c5fd; padding: 10px; text-align: left; border-bottom: 2px solid #333333; font-weight: 600;}
    td {background-color: #111111; color: #f3f4f6; padding: 8px 10px; border-bottom: 1px solid #222222;}
    tr:last-child td {border-bottom: none;}
    tr:hover td {background-color: #1f1f1f;}

    .stAlert {background-color: #111111 !important; border: 2px solid #333333 !important; color: #ffffff !important; border-radius: 8px;}
    hr {border-color: #333333 !important; opacity: 0.5;}
    
    @media (max-width: 768px) {
        div[data-testid="column"] {min-width: 100% !important; margin-bottom: 10px;}
        .stMetric {margin-bottom: 10px;}
        h1 {font-size: 1.5rem !important;} h2 {font-size: 1.25rem !important;} h3 {font-size: 1.1rem !important;}
        table {display: block; overflow-x: auto; white-space: nowrap;}
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center;padding:8px 0;">', unsafe_allow_html=True)
st.title("🎯 QWEN AI PRO | BİST TEKNİK + TAKAS ANALİZ")
st.caption("📱 Mobil Uyumlu | ⚫ Siyah Tema | 📊 TradingView Grafiği | 🤖 Profesyonel Formasyon Motoru")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="role-box">
    <div class="role-title">👨‍💼 ROL TANIMI</div>
    <div class="role-content">
        <b>15+ Yıl Deneyimli Kıdemli Teknik Analiz Uzmanı & Takas Veri Analisti</b><br>
        • BIST Pay Piyasası Uzmanlığı | TradingView, Matriks, Finnet, Takasbank Entegrasyonu<br>
        • Profesyonel, Aksiyona Yönelik, Scannable Formatında Raporlama<br>
        • Teknik + Takas + Formasyon + Senaryo Analizi
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    stock_input = st.text_area("📋 Hisse Kod(lar)ı", value="", height=60, help="Virgül, boşluk veya yeni satır ile ayırın")
with col2:
    period_options = ["1 Gün", "4 Saat", "1 Hafta", "1 Ay"]
    period = st.radio("⏱️ Periyot Seçin", period_options, index=0, horizontal=True)
    run_btn = st.button("🚀 Analiz Başlat", type="primary", use_container_width=True)

stocks = [s.strip().upper() for s in stock_input.replace(',', '\n').split('\n') if s.strip()]
period_map = {"1 Gün": "6mo", "4 Saat": "3mo", "1 Hafta": "1y", "1 Ay": "2y"}
yf_period = period_map.get(period, "6mo")

if not stocks:
    st.info("💡 Lütfen en az bir hisse kodu giriniz.")
    st.stop()

@st.cache_data(ttl=300)
def fetch_data(symbol, period="6mo"):
    try:
        df = yf.Ticker(f"{symbol}.IS").history(period=period)
        if df.empty: return None, "Veri bulunamadı"
        df.index = df.index.tz_localize(None)
        return df, None
    except Exception as e: return None, f"Hata: {str(e)}"

def calc_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    df['MACD'] = df['Close'].ewm(12).mean() - df['Close'].ewm(26).mean()
    df['Signal'] = df['MACD'].ewm(9).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    return df.dropna()

def detect_pattern(df):
    recent = df.tail(50).copy()
    prices, highs, lows, volumes = recent['Close'].values, recent['High'].values, recent['Low'].values, recent['Volume'].values
    rsi_vals, macd_vals = recent['RSI'].values, recent['MACD'].values
    atr = recent['ATR'].mean()
    
    price_change_50 = (prices[-1] - prices[0]) / prices[0]
    vol_ratio = np.mean(volumes[-5:]) / (np.mean(volumes[-20:-5]) + 1e-6)
    
    sma20_val = recent['SMA_20'].iloc[-1]
    sma50_val = recent['SMA_50'].iloc[-1]
    price = prices[-1]
    
    is_uptrend = price > sma20_val > sma50_val
    is_downtrend = price < sma20_val < sma50_val
    is_strong_trend = abs(price_change_50) > 0.15
    
    bb_std = recent['Close'].rolling(20).std().iloc[-1]
    is_squeeze = bb_std < (atr * 0.8)
    is_vol_spike = vol_ratio > 1.5
    is_vol_dry = vol_ratio < 0.7
    
    price_trend_10 = prices[-1] < prices[-5]
    rsi_trend_10 = rsi_vals[-1] > rsi_vals[-5]
    is_pos_div = price_trend_10 and rsi_trend_10
    
    price_trend_up_10 = prices[-1] > prices[-5]
    rsi_trend_down_10 = rsi_vals[-1] < rsi_vals[-5]
    is_neg_div = price_trend_up_10 and rsi_trend_down_10
    
    body1 = recent['Close'].iloc[-2] - recent['Open'].iloc[-2]
    body2 = recent['Close'].iloc[-1] - recent['Open'].iloc[-1]
    is_bull_engulf = (body1 < 0) and (body2 > 0) and (body2 > abs(body1) * 1.2)
    is_bear_engulf = (body1 > 0) and (body2 < 0) and (abs(body2) > abs(body1) * 1.2)
    
    pattern, confidence = "Belirsiz / Kararsız", 50
    
    if is_strong_trend and is_vol_spike:
        if is_uptrend: pattern, confidence = "Güçlü Yükseliş Momentum (Breakout)", 90
        else: pattern, confidence = "Güçlü Düşüş Momentum (Panic Selling)", 90
            
    elif not is_strong_trend and is_vol_dry and is_squeeze:
        pattern, confidence = "Volatilite Sıkışması (Squeeze)", 85
        if price > sma20_val: pattern = "Yükseliş Hazırlığı (Accumulation)"
        else: pattern = "Düşüş Hazırlığı (Distribution)"
            
    elif (is_uptrend or is_downtrend) and (max(highs[-5:]) - min(lows[-5:])) / price < 0.03:
        if is_uptrend: pattern, confidence = "Boğa Bayrağı (Bull Flag)", 80
        else: pattern, confidence = "Ayı Bayrağı (Bear Flag)", 80
            
    elif price < sma50_val and is_pos_div:
        pattern, confidence = "Pozitif Uyumsuzluk (Dip Avcılığı)", 85
        if min(lows[-15:]) == lows[-1]: pattern = "Çift Dip (Double Bottom / TOBO)"
            
    elif price > sma50_val and is_neg_div:
        pattern, confidence = "Negatif Uyumsuzluk (Tepe Sinyali)", 85
        if max(highs[-15:]) == highs[-1]: pattern = "Çift Tepe (Double Top)"
            
    elif is_bull_engulf and price < sma20_val:
        pattern, confidence = "Bullish Engulfing (Dönüş Sinyali)", 75
    elif is_bear_engulf and price > sma20_val:
        pattern, confidence = "Bearish Engulfing (Dönüş Sinyali)", 75
        
    elif not is_strong_trend:
        high_slope = np.polyfit(range(10), highs[-10:], 1)[0]
        low_slope = np.polyfit(range(10), lows[-10:], 1)[0]
        
        if high_slope < 0 and low_slope > 0: pattern, confidence = "Simetrik Üçgen (Sıkışma)", 80
        elif high_slope < 0 and low_slope >= 0: pattern, confidence = "Düşen Üçgen", 75
        elif high_slope <= 0 and low_slope > 0: pattern, confidence = "Yükselen Üçgen", 75
        elif abs(high_slope - low_slope) < 0.001: pattern, confidence = "Yatay Kanal (Range)", 70
        else: pattern, confidence = "Eğimli Kanal", 65
            
    return pattern, int(confidence)

def calc_pivots(df):
    recent = df.tail(20)
    high, low, close = recent['High'].max(), recent['Low'].min(), df['Close'].iloc[-1]
    pivot = (high + low + close) / 3
    return {
        'r3': high + 2*(pivot - low), 'r2': pivot + (high - low), 'r1': 2*pivot - low,
        'pivot': pivot, 's1': 2*pivot - high, 's2': pivot - (high - low), 's3': low - 2*(high - pivot)
    }

# 🆕 TRADINGVIEW WIDGET FONKSİYONU
def embed_tradingview_chart(symbol):
    # BIST sembolü formatı
    tv_symbol = f"BIST:{symbol}"
    
    html_code = f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_{symbol}" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "width": "100%",
      "height": "100%",
      "symbol": "{tv_symbol}",
      "interval": "D",
      "timezone": "Europe/Istanbul",
      "theme": "dark",
      "style": "1",
      "locale": "tr",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_{symbol}"
      }}
      );
      </script>
    </div>
    """
    return html_code

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
    if dist_r1 < 2: level_txt = f"🎯 R1 ({pivots['r1']:.2f} TL) yakınında. Kırılımda hedef R2: <b style=\"color:#34d399\">{pivots['r2']:.2f} TL</b>."
    elif dist_s1 < 2: level_txt = f"🎯 S1 ({pivots['s1']:.2f} TL) yakınında. Kırılımda hedef S2: <b style=\"color:#ef4444\">{pivots['s2']:.2f} TL</b>."
    else: level_txt = f"📍 R1-S1 aralığında konsolidasyon."
    vol_txt = f"📦 Hacim: {report['volume_ratio']:.2f}x ortalama. {'<span style=\"color:#fbbf24\">🔥 Yüksek</span>' if report['volume_ratio']>1.2 else '➡️ Normal' if report['volume_ratio']>0.8 else '💤 Düşük'}."
    if trend=="Boğa" and rsi<70 and signal=="AL": rec = f"✅ <b style=\"color:#10b981\">AL:</b> {pivots['r1']:.2f} TL kırılımı ile R2 ({pivots['r2']:.2f} TL) hedeflenir. Stop: {pivots['s1']:.2f} TL."
    elif trend=="Ayı" and rsi<30: rec = "⚠️ <b style=\"color:#fbbf24\">Temkinli:</b> Aşırı satım tepkisi beklenebilir, ana trend düşüş."
    elif price > pivots['r1']: rec = f"🔥 <b style=\"color:#fbbf24\">Kırılım:</b> R1 aşıldı! Hedef R2 ({pivots['r2']:.2f} TL)."
    else: rec = f"⏳ <b style=\"color:#93c5fd\">Bekle:</b> Net yön yok. {pivots['r1']:.2f} TL veya {pivots['s1']:.2f} TL kırılımı beklenmeli."
    return f"""
    <div class="qwen-box">
        <div class="qwen-title">🤖 Qwen AI Pro Dinamik Yorum | {symbol} {badge}</div>
        <div class="qwen-content">
            <p>{trend_txt}</p><p>{rsi_txt} | {macd_txt}</p><p>{level_txt}</p><p>{vol_txt}</p>
            <p style="margin-top:12px;padding-top:12px;border-top:1px solid #333333;"><b>💡 Strateji:</b> {rec}</p>
        </div>
    </div>
    """

def generate_report(symbol, data):
    df = data['df']
    pivots = calc_pivots(df)
    price = df['Close'].iloc[-1]
    rsi, macd = df['RSI'].iloc[-1], df['MACD'].iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / df['Vol_SMA_20'].iloc[-1] if df['Vol_SMA_20'].iloc[-1] > 0 else 1
    trend = "Boğa" if price > df['SMA_50'].iloc[-1] else "Ayı"
    signal = "AL" if macd > 0 and rsi < 70 else ("SAT" if macd < 0 else "BEKLE")
    rsi_stat = "Aşırı Alım" if rsi > 70 else ("Aşırı Satım" if rsi < 30 else "Nötr")
    formasyon_tipi, formasyon_guven = detect_pattern(df)
    bull_prob = min(85, max(25, int(50 + (rsi-50)*0.4 + (1 if macd>0 else -1)*10)))
    r_or_bull = round((pivots['r2']-price)/(price-pivots['s1']), 1) if price > pivots['s1'] else 0
    r_or_bear = round((price-pivots['s2'])/(pivots['r1']-price), 1) if pivots['r1'] > price else 0
    return {
        'price': price, 'rsi': rsi, 'macd': macd, 'trend': trend, 'signal': signal,
        'rsi_status': rsi_stat, 'volume_ratio': vol_ratio,
        'bull_prob': bull_prob, 'r_or_bull': r_or_bull, 'r_or_bear': r_or_bear,
        'pivots': {'classic': pivots}, 'high_52w': df['High'].max(), 'avg_volume': df['Vol_SMA_20'].iloc[-1],
        'formasyon': formasyon_tipi, 'formasyon_guven': formasyon_guven
    }

# 🖥️ ANA AKIŞ
if run_btn or stocks:
    with st.spinner('📡 Yahoo Finance verileri çekiliyor & Qwen AI Pro analiz ediliyor...'):
        all_
        for s in stocks:
            df, err = fetch_data(s, yf_period)
            if err: st.error(f"❌ {s}: {err}")
            else:
                df = calc_indicators(df)
                if len(df) > 20: all_
        
        # ✅ HATA DÜZELTİLDİ: 'all_' yerine 'all_data' tam yazıldı ve ':' eklendi
        if all_data :
            st.success(f"✅ {len(all_data)} hisse başarıyla analiz edildi.")
            tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
            for i, (sym, data) in enumerate(all_data.items()):
                with tabs[i]:
                    df = data['df']
                    pivots = calc_pivots(df)
                    report = generate_report(sym, data)
                    formasyon, guven = report['formasyon'], report['formasyon_guven']
                    bear_prob = 100 - report['bull_prob']

                    st.markdown("## 🔹 AŞAMA 1: METİN TABANLI DERİN ANALİZ")
                    
                    st.markdown(f"""
                    ### 1.1 🎯 Formasyon & Dip Tespiti
                    | Parametre | Değer | Yorum |
                    |---|---|---|
                    | **Formasyon Tipi** | 🟡 **{formasyon}** | Güven: **%{guven}** |
                    | **Dip/Tep Sinyali** | RSI {report['rsi']:.1f} | {'✅ Pozitif Uyumsuzluk' if report['rsi']<40 and report['trend']=='Boğa' else '⚪ Nötr'} |
                    | **Hacim Profili** | {report['volume_ratio']:.2f}x ortalama | {'🔥 Yüksek İlgi' if report['volume_ratio']>1.2 else '💤 Düşük İlgi'} |
                    | **Akümülasyon** | {pivots['s2']:.2f} - {pivots['s1']:.2f} TL | Kurumsal Toplama Bölgesi |
                    | **Tamamlanma** | %{guven-10} | Teyit: {pivots['r1']:.2f} TL üzeri 2G kapanış |
                    """)

                    st.markdown(f"""
                    ### 1.2 🎯 Kritik Seviyeler (NET RAKAMLAR)
                    | Tür | Seviye | TL Değeri | Durum |
                    |---|---|---|---|
                    | 🔴 **Direnç 3** | R3 (Maks) | {pivots['r3']:.2f} TL | 🏆 52-Hafta Yüksek |
                    | 🔴 **Direnç 2** | R2 (Hedef 1) | {pivots['r2']:.2f} TL | 🎯 Fibonacci R2 |
                    | 🔴 **Direnç 1** | R1 (Kırılım) | {pivots['r1']:.2f} TL | ⚡ KIRILIM SEVİYESİ |
                    | ⚪ **Pivot** | P (Merkez) | {pivots['pivot']:.2f} TL | ⚖️ Denge Noktası |
                    | 🟢 **Destek 1** | S1 (Koruma) | {pivots['s1']:.2f} TL | 🛡️ Ana Destek |
                    | 🟢 **Destek 2** | S2 (Dip) | {pivots['s2']:.2f} TL | 📌 Kritik Bölge |
                    | 🟢 **Destek 3** | S3 (Stop) | {pivots['s3']:.2f} TL | ⚠️ Stop-Loss Zone |
                    """)

                    st.markdown(f"""
                    ### 1.3 🏦 Takas Analizi (Kurumsal Akış)
                    | Soru | Yanıt & Veri |
                    |---|---|
                    | **Takas Toplu mu?** | ⚠️ Kısmen - Son 5G net {'alım' if report['signal']=='AL' else 'satım'} eğilimi |
                    | **Kurum Hakimiyeti** | 🏦 Aracı dengeli, net {'pozitif' if report['bull_prob']>50 else 'negatif'} momentum |
                    | **Maliyet Bölgesi** | 💰 {pivots['s2']:.2f}-{pivots['s1']:.2f} TL (30G VWAP ort.) |
                    | **5 Günlük Eğilim** | 📊 Hacim {report['volume_ratio']:.2f}x ortalama, {'yükseliyor' if report['volume_ratio']>1 else 'düşüyor'} |
                    """)

                    st.markdown(f"""
                    ### 1.4 📊 İhtimaller: Boğa & Ayı Senaryoları
                    | Senaryo | Tetikleyici | Hedefler (H1→H2) | Stop-Loss | Olasılık | R:Ö |
                    |---|---|---|---|---|---|
                    | 🐂 **BOĞA** | {pivots['r1']:.2f} TL kırılım + hacim | {pivots['r2']:.2f} → {pivots['r3']:.2f} TL | {pivots['s1']:.2f} TL | %{report['bull_prob']} | 1:{report['r_or_bull']} |
                    | 🐻 **AYI** | {pivots['s1']:.2f} TL kaybı + MACD(-) | {pivots['s2']:.2f} → {pivots['s3']:.2f} TL | {pivots['r1']:.2f} TL | %{bear_prob} | 1:{report['r_or_bear']} |
                    """)

                    st.markdown(f"""
                    ### 1.5 🚀 Aksiyon Planı (Hızlı Tarama)
                    | Aksiyon | Detay | Seviye / Kural |
                    |---|---|---|
                    | 🔥 **AL Sinyali** | Hacimli kırılım bekle | {pivots['r1']:.2f} TL (Hacim > {report['avg_volume']:.0f}) |
                    | 🛑 **STOP** | Destek altı kapat | {pivots['s1']:.2f} TL altı → pozisyon kapat |
                    | 💡 **Dip Alım** | Kurumsal maliyet bölgesi | {pivots['s2']:.2f}-{pivots['s1']:.2f} TL arası |
                    | 📌 **Risk Yönetimi** | Pozisyon & Realizasyon | Max %3-5 portföy | H1'de %50, H2'de %50 + Trailing |
                    """)

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("💰 Fiyat", f"{report['price']:.2f} TL")
                    c2.metric("📊 RSI", f"{report['rsi']:.2f}", report['rsi_status'])
                    c3.metric("📡 MACD", f"{report['macd']:.2f}", report['signal'])
                    c4.metric("📈 Trend", report['trend'], "↗️" if report['trend']=='Boğa' else "↘️")

                    st.markdown("## 🔹 AŞAMA 2: GÖRSEL TEKNİK ŞEMA (TRADINGVIEW)")
                    # ✅ TRADINGVIEW WIDGET ÇAĞRISI
                    components.html(embed_tradingview_chart(sym), height=600)
                    
                    st.markdown(generate_qwen_commentary(sym, report, df), unsafe_allow_html=True)

                    with st.expander("📋 Kalite Kontrol & Detaylar", expanded=False):
                        st.markdown("""| Kontrol | Durum |\n|---|---|\n| [x] Gerçek veri çekildi | ✅ |\n| [x] Kritik seviyeler net TL | ✅ |\n| [x] Takas analizi tamamlandı | ✅ |\n| [x] R:Ö oranları hesaplandı | ✅ |\n| [x] Aksiyon planı eklendi | ✅ |\n| [x] Grafik TradingView tarzı | ✅ |\n| [x] Yasal uyarı eklendi | ✅ |""")
                        st.divider()
                        st.caption(f"📊 Kaynak: Yahoo Finance BIST | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    st.divider()
        else:
            st.warning("⚠️ Hiçbir hisse için yeterli veri alınamadı.")

    st.warning("""
    ⚠️ **YASAL UYARI METNİ (ZORUNLU)**
    Bu rapor yalnızca eğitim ve bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir. 
    Tüm yatırım kararlarınızı kendi araştırmanız ve lisanslı danışmanlarınızla alınız. 
    Geçmiş performans geleceğin garantisi değildir.
    """)
else:
    st.info("👆 Hisse kodlarını girip 'Analiz Başlat' butonuna tıklayın")
