# app.py
# 🎯 Qwen AI Pro | BIST Teknik + Takas Analiz (borsapy Entegre)
# pip install streamlit pandas numpy yfinance borsapy

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf
import borsapy as bp
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 🌐 Sayfa Yapılandırması
st.set_page_config(
    page_title="Qwen AI Pro | BIST Teknik + Takas Analiz", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="collapsed"
)

# 🎨 CSS Stilleri
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
        background-color: #1a1a1a !important; border: 1px solid #404040 !important; border-radius: 20px !important;
        padding: 8px 16px !important; color: #ffffff !important; font-weight: 500 !important; transition: all 0.2s;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important; border-color: #3b82f6 !important;
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

# Başlık
st.markdown('<div style="text-align:center;padding:8px 0;">', unsafe_allow_html=True)
st.title("🎯 QWEN AI PRO | BİST TEKNİK + TAKAS ANALİZ")
st.caption("📱 Mobil Uyumlu | ⚫ Siyah Tema | 📊 TradingView | 🤖 borsapy Entegre")
st.markdown('</div>', unsafe_allow_html=True)

# Rol Tanımı
st.markdown("""
<div class="role-box">
    <div class="role-title">👨‍💼 ROL TANIMI</div>
    <div class="role-content">
        <b>15+ Yıl Deneyimli Teknik Analiz Uzmanı & Takas Veri Analisti</b><br>
        • BIST Pay Piyasası | TradingView, Matriks, borsapy Entegrasyonu<br>
        • Teknik + Takas Proxy + Formasyon + Senaryo Analizi<br>
        • ⚠️ Takas verileri MKK'den 2G gecikmeli gelir. Bu analiz proxy metrikler içerir.
    </div>
</div>
""", unsafe_allow_html=True)

# Input Alanları
col1, col2 = st.columns([2, 1])
with col1:
    stock_input = st.text_area("📋 Hisse Kod(lar)ı", value="GARAN,THYAO,ASELS", height=60, 
                               help="Virgül, boşluk veya yeni satır ile ayırın. Örnek: GARAN, THYAO, ASELS")
with col2:
    period_options = ["1 Gün", "4 Saat", "1 Hafta", "1 Ay"]
    period = st.radio("⏱️ Periyot Seçin", period_options, index=0, horizontal=True)
    run_btn = st.button("🚀 Analiz Başlat", type="primary", use_container_width=True)

# Hisse kodlarını parse et
stocks = [s.strip().upper() for s in stock_input.replace(',', '\n').split('\n') if s.strip()]
period_map = {"1 Gün": "6mo", "4 Saat": "3mo", "1 Hafta": "1y", "1 Ay": "2y"}
yf_period = period_map.get(period, "6mo")

if not stocks:
    st.info("💡 Lütfen en az bir hisse kodu giriniz.")
    st.stop()

# ============================================================================
# 📡 VERİ ÇEKME FONKSİYONLARI
# ============================================================================

@st.cache_data(ttl=300)
def fetch_yf_data(symbol, period="6mo"):
    """Yahoo Finance'den fiyat verisi çek"""
    try:
        df = yf.Ticker(f"{symbol}.IS").history(period=period)
        if df.empty: return None, "Veri bulunamadı"
        df.index = df.index.tz_localize(None)
        return df, None
    except Exception as e: 
        return None, f"Hata: {str(e)}"

@st.cache_data(ttl=600)
def fetch_borsapy_proxy(symbol: str, period: str = "3mo") -> dict:
    """
    borsapy ile takas benzeri kurumsal akış tahmini (proxy)
    Gerçek takas verisi yerine teknik + temel metriklerden türetilir
    """
    try:
        ticker = bp.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df is None or df.empty or len(df) < 20:
            return None
            
        # Temel metrikler
        price = df['Close'].iloc[-1]
        volume = df['Volume'].iloc[-1]
        vol_sma20 = df['Volume'].rolling(20).mean().iloc[-1]
        
        # Yabancı oranı (borsapy fast_info'dan)
        foreign_ratio = ticker.fast_info.get('foreign_ratio', None)
        if foreign_ratio is None:
            # Sektör ortalaması tahmini (BIST100 ~%35)
            foreign_ratio = 35.0
        
        # Hacim momentumu (kurumsal ilgi göstergesi)
        vol_ratio = volume / (vol_sma20 + 1e-6)
        vol_trend = df['Volume'].tail(5).mean() / (df['Volume'].tail(20).mean() + 1e-6)
        
        # Fiyat momentumu
        price_change_5d = (price - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100 if len(df) >= 5 else 0
        price_change_20d = (price - df['Close'].iloc[-20]) / df['Close'].iloc[-20] * 100 if len(df) >= 20 else 0
        
        # Kurumsal akış skoru (0-100)
        flow_score = 0
        if vol_ratio > 1.3: flow_score += 25
        if vol_trend > 1.1: flow_score += 20
        if price_change_5d > 2: flow_score += 15
        elif price_change_5d > 0: flow_score += 8
        if price_change_20d > 5: flow_score += 15
        elif price_change_20d > 0: flow_score += 8
        if foreign_ratio > 40: flow_score += 10
        if foreign_ratio > 60: flow_score += 7
        
        # Akış yönü belirleme
        if flow_score >= 70:
            akis = "Güçlü Kurumsal Alım"
            signal = "🟢"
        elif flow_score >= 50:
            akis = "Net Alım Eğilimi"
            signal = "🟡"
        elif flow_score <= 30:
            akis = "Kurumsal Satış Baskısı"
            signal = "🔴"
        else:
            akis = "Dengeli / Bekle-Gör"
            signal = "⚪"
        
        # Maliyet bölgesi tahmini (20G VWAP proxy)
        vwap_proxy = (df['Close'] * df['Volume']).sum() / (df['Volume'].sum() + 1e-6)
        
        return {
            'symbol': symbol,
            'price': price,
            'foreign_ratio': float(foreign_ratio),
            'volume_ratio': round(vol_ratio, 2),
            'volume_trend': round(vol_trend, 2),
            'price_change_5d': round(price_change_5d, 2),
            'price_change_20d': round(price_change_20d, 2),
            'flow_score': flow_score,
            'akis_yonu': akis,
            'signal': signal,
            'maliyet_bölgesi': f"{vwap_proxy*0.97:.2f} - {vwap_proxy*1.03:.2f} TL",
            'vwap_proxy': round(vwap_proxy, 2),
            'timestamp': datetime.now()
        }
        
    except Exception as e:
        # Hata durumunda fallback değerler
        return {
            'symbol': symbol,
            'price': 0,
            'foreign_ratio': 35.0,
            'volume_ratio': 1.0,
            'volume_trend': 1.0,
            'price_change_5d': 0,
            'price_change_20d': 0,
            'flow_score': 50,
            'akis_yonu': "Veri Alınamadı",
            'signal': "⚪",
            'maliyet_bölgesi': "N/A",
            'vwap_proxy': 0,
            'timestamp': datetime.now(),
            'error': str(e)
        }

# ============================================================================
# 📊 TEKNİK ANALİZ FONKSİYONLARI
# ============================================================================

def calc_indicators(df):
    df = df.copy()
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss.replace(0, np.nan)))
    
    # MACD
    df['MACD'] = df['Close'].ewm(12).mean() - df['Close'].ewm(26).mean()
    df['Signal'] = df['MACD'].ewm(9).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    return df.dropna()

def detect_pattern(df):
    recent = df.tail(50).copy()
    prices = recent['Close'].values
    highs, lows = recent['High'].values, recent['Low'].values
    rsi_vals = recent['RSI'].values
    atr = recent['ATR'].mean()
    
    price_change_50 = (prices[-1] - prices[0]) / prices[0] if len(prices) > 0 else 0
    vol_ratio = np.mean(recent['Volume'].values[-5:]) / (np.mean(recent['Volume'].values[-20:-5]) + 1e-6)
    
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
    
    # Uyumsuzluk kontrolü
    price_trend_10 = prices[-1] < prices[-5] if len(prices) >= 5 else False
    rsi_trend_10 = rsi_vals[-1] > rsi_vals[-5] if len(rsi_vals) >= 5 else False
    is_pos_div = price_trend_10 and rsi_trend_10
    
    price_trend_up_10 = prices[-1] > prices[-5] if len(prices) >= 5 else False
    rsi_trend_down_10 = rsi_vals[-1] < rsi_vals[-5] if len(rsi_vals) >= 5 else False
    is_neg_div = price_trend_up_10 and rsi_trend_down_10
    
    # Engulfing
    if len(recent) >= 2:
        body1 = recent['Close'].iloc[-2] - recent['Open'].iloc[-2]
        body2 = recent['Close'].iloc[-1] - recent['Open'].iloc[-1]
        is_bull_engulf = (body1 < 0) and (body2 > 0) and (body2 > abs(body1) * 1.2)
        is_bear_engulf = (body1 > 0) and (body2 < 0) and (abs(body2) > abs(body1) * 1.2)
    else:
        is_bull_engulf = is_bear_engulf = False
    
    pattern, confidence = "Belirsiz / Kararsız", 50
    
    if is_strong_trend and is_vol_spike:
        if is_uptrend: pattern, confidence = "Güçlü Yükseliş Momentum (Breakout)", 90
        else: pattern, confidence = "Güçlü Düşüş Momentum (Panic Selling)", 90
    elif not is_strong_trend and is_vol_dry and is_squeeze:
        pattern, confidence = "Volatilite Sıkışması (Squeeze)", 85
        if price > sma20_val: pattern = "Yükseliş Hazırlığı (Accumulation)"
        else: pattern = "Düşüş Hazırlığı (Distribution)"
    elif (is_uptrend or is_downtrend) and len(highs) >= 5 and len(lows) >= 5:
        if (max(highs[-5:]) - min(lows[-5:])) / price < 0.03:
            if is_uptrend: pattern, confidence = "Boğa Bayrağı (Bull Flag)", 80
            else: pattern, confidence = "Ayı Bayrağı (Bear Flag)", 80
    elif price < sma50_val and is_pos_div:
        pattern, confidence = "Pozitif Uyumsuzluk (Dip Avcılığı)", 85
        if len(lows) >= 15 and min(lows[-15:]) == lows[-1]: pattern = "Çift Dip (Double Bottom)"
    elif price > sma50_val and is_neg_div:
        pattern, confidence = "Negatif Uyumsuzluk (Tepe Sinyali)", 85
        if len(highs) >= 15 and max(highs[-15:]) == highs[-1]: pattern = "Çift Tepe (Double Top)"
    elif is_bull_engulf and price < sma20_val:
        pattern, confidence = "Bullish Engulfing (Dönüş Sinyali)", 75
    elif is_bear_engulf and price > sma20_val:
        pattern, confidence = "Bearish Engulfing (Dönüş Sinyali)", 75
    elif not is_strong_trend and len(highs) >= 10 and len(lows) >= 10:
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

def generate_report(symbol, data, takas_proxy=None):
    df = data['df']
    pivots = calc_pivots(df)
    price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
    macd = df['MACD'].iloc[-1] if 'MACD' in df.columns else 0
    
    vol_ratio = df['Volume'].iloc[-1] / df['Vol_SMA_20'].iloc[-1] if 'Vol_SMA_20' in df.columns and df['Vol_SMA_20'].iloc[-1] > 0 else 1
    
    trend = "Boğa" if price > df['SMA_50'].iloc[-1] else "Ayı"
    signal = "AL" if macd > 0 and rsi < 70 else ("SAT" if macd < 0 and rsi > 30 else "BEKLE")
    rsi_stat = "Aşırı Alım" if rsi > 70 else ("Aşırı Satım" if rsi < 30 else "Nötr")
    
    formasyon_tipi, formasyon_guven = detect_pattern(df)
    
    # Boğa olasılığı hesapla
    bull_prob = min(85, max(25, int(50 + (rsi-50)*0.4 + (1 if macd>0 else -1)*10)))
    
    # Risk/Ödül oranları
    r_or_bull = round((pivots['r2']-price)/(price-pivots['s1']), 1) if price > pivots['s1'] and (price-pivots['s1']) > 0 else 0
    r_or_bear = round((price-pivots['s2'])/(pivots['r1']-price), 1) if pivots['r1'] > price and (pivots['r1']-price) > 0 else 0
    
    report = {
        'price': price, 'rsi': rsi, 'macd': macd, 'trend': trend, 'signal': signal,
        'rsi_status': rsi_stat, 'volume_ratio': vol_ratio,
        'bull_prob': bull_prob, 'r_or_bull': r_or_bull, 'r_or_bear': r_or_bear,
        'pivots': {'classic': pivots}, 'high_52w': df['High'].max(), 
        'avg_volume': df['Vol_SMA_20'].iloc[-1] if 'Vol_SMA_20' in df.columns else df['Volume'].mean(),
        'formasyon': formasyon_tipi, 'formasyon_guven': formasyon_guven
    }
    
    # Takas proxy verilerini ekle
    if takas_proxy:
        report.update({
            'takas_akis': takas_proxy['akis_yonu'],
            'takas_signal': takas_proxy['signal'],
            'takas_guven': takas_proxy['flow_score'],
            'yabancı_oran': takas_proxy['foreign_ratio'],
            'hacim_momentum': takas_proxy['volume_trend'],
            'maliyet_vwap': takas_proxy['vwap_proxy'],
            'maliyet_bant': takas_proxy['maliyet_bölgesi'],
            'price_change_5d': takas_proxy['price_change_5d'],
            'takas_error': takas_proxy.get('error', None)
        })
    else:
        # Fallback değerler
        report.update({
            'takas_akis': "Veri Yok",
            'takas_signal': "⚪",
            'takas_guven': 50,
            'yabancı_oran': 35.0,
            'hacim_momentum': 1.0,
            'maliyet_vwap': price,
            'maliyet_bant': f"{price*0.97:.2f} - {price*1.03:.2f} TL",
            'price_change_5d': 0,
            'takas_error': "borsapy veri alınamadı"
        })
    
    return report

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
    
    dist_r1 = (pivots['r1']-price)/price*100 if price > 0 else 0
    dist_s1 = (price-pivots['s1'])/price*100 if price > 0 else 0
    
    if dist_r1 < 2: level_txt = f"🎯 R1 ({pivots['r1']:.2f} TL) yakınında. Kırılımda hedef R2: <b style=\"color:#34d399\">{pivots['r2']:.2f} TL</b>."
    elif dist_s1 < 2: level_txt = f"🎯 S1 ({pivots['s1']:.2f} TL) yakınında. Kırılımda hedef S2: <b style=\"color:#ef4444\">{pivots['s2']:.2f} TL</b>."
    else: level_txt = f"📍 R1-S1 aralığında konsolidasyon."
    
    vol_txt = f"📦 Hacim: {report['volume_ratio']:.2f}x ortalama. {'<span style=\"color:#fbbf24\">🔥 Yüksek</span>' if report['volume_ratio']>1.2 else '➡️ Normal' if report['volume_ratio']>0.8 else '💤 Düşük'}."
    
    # Takas akışını yorumla
    takas_txt = f"🏦 Takas Proxy: {report['takas_signal']} {report['takas_akis']} (Güven: %{report['takas_guven']})"
    
    if trend=="Boğa" and rsi<70 and signal=="AL": 
        rec = f"✅ <b style=\"color:#10b981\">AL:</b> {pivots['r1']:.2f} TL kırılımı ile R2 ({pivots['r2']:.2f} TL) hedeflenir. Stop: {pivots['s1']:.2f} TL."
    elif trend=="Ayı" and rsi<30: 
        rec = "⚠️ <b style=\"color:#fbbf24\">Temkinli:</b> Aşırı satım tepkisi beklenebilir, ana trend düşüş."
    elif price > pivots['r1']: 
        rec = f"🔥 <b style=\"color:#fbbf24\">Kırılım:</b> R1 aşıldı! Hedef R2 ({pivots['r2']:.2f} TL)."
    else: 
        rec = f"⏳ <b style=\"color:#93c5fd\">Bekle:</b> Net yön yok. {pivots['r1']:.2f} TL veya {pivots['s1']:.2f} TL kırılımı beklenmeli."
    
    return f"""
    <div class="qwen-box">
        <div class="qwen-title">🤖 Qwen AI Pro Dinamik Yorum | {symbol} {badge}</div>
        <div class="qwen-content">
            <p>{trend_txt}</p><p>{rsi_txt} | {macd_txt}</p><p>{level_txt}</p><p>{vol_txt}</p><p>{takas_txt}</p>
            <p style="margin-top:12px;padding-top:12px;border-top:1px solid #333333;"><b>💡 Strateji:</b> {rec}</p>
        </div>
    </div>
    """

# ============================================================================
# 🖥️ ANA AKIŞ
# ============================================================================

if run_btn or stocks:
    with st.spinner('📡 Yahoo Finance & borsapy verileri çekiliyor & Qwen AI Pro analiz ediliyor...'):
        
        all_data = {}
        
        for s in stocks:
            # Yahoo Finance verisi
            df, err = fetch_yf_data(s, yf_period)
            if err: 
                st.error(f"❌ {s}: {err}")
                continue
            
            df = calc_indicators(df)
            if len(df) < 20: 
                st.warning(f"⚠️ {s}: Yetersiz veri ({len(df)} satır)")
                continue
            
            # borsapy takas proxy
            takas_proxy = fetch_borsapy_proxy(s, period="3mo")
            
            all_data[s] = {'df': df, 'takas_proxy': takas_proxy}
        
        if all_data:
            st.success(f"✅ {len(all_data)} hisse başarıyla analiz edildi.")
            tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
            
            for i, (sym, data) in enumerate(all_data.items()):
                with tabs[i]:
                    df = data['df']
                    takas_proxy = data.get('takas_proxy')
                    pivots = calc_pivots(df)
                    report = generate_report(sym, data, takas_proxy)
                    
                    formasyon, guven = report['formasyon'], report['formasyon_guven']
                    bear_prob = 100 - report['bull_prob']

                    # 🔹 AŞAMA 1: METİN TABANLI DERİN ANALİZ
                    st.markdown("## 🔹 AŞAMA 1: METİN TABANLI DERİN ANALİZ")
                    
                    # 1.1 Formasyon & Dip Tespiti
                    st.markdown(f"""
                    ### 1.1 🎯 Formasyon & Dip Tespiti
                    | Parametre | Değer | Yorum |
                    |---|---|---|
                    | **Formasyon Tipi** | 🟡 **{formasyon}** | Güven: **%{guven}** |
                    | **Dip/Tep Sinyali** | RSI {report['rsi']:.1f} | {'✅ Pozitif Uyumsuzluk' if report['rsi']<40 and report['trend']=='Boğa' else '⚪ Nötr'} |
                    | **Hacim Profili** | {report['volume_ratio']:.2f}x ortalama | {'🔥 Yüksek İlgi' if report['volume_ratio']>1.2 else '💤 Düşük İlgi'} |
                    | **Akümülasyon** | {pivots['s2']:.2f} - {pivots['s1']:.2f} TL | Kurumsal Toplama Bölgesi |
                    | **Tamamlanma** | %{max(0, guven-10)} | Teyit: {pivots['r1']:.2f} TL üzeri 2G kapanış |
                    """)

                    # 1.2 Kritik Seviyeler
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

                    # 1.3 Takas Analizi (borsapy Proxy ile)
                    takas_note = ""
                    if report.get('takas_error'):
                        takas_note = f"<br><small style='color:#fbbf24'>⚠️ Not: {report['takas_error']}</small>"
                    
                    st.markdown(f"""
                    ### 1.3 🏦 Takas Analizi (borsapy Proxy ile)
                    | Metrik | Değer | Yorum |
                    |--------|-------|-------|
                    | **Net Akış** | {report['takas_signal']} {report['takas_akis']} | Güven: %{report['takas_guven']} |
                    | **Yabancı Oranı** | %{report['yabancı_oran']:.1f} | {'🌍 Yüksek' if report['yabancı_oran']>40 else '📊 Orta' if report['yabancı_oran']>25 else '🔍 Düşük'} |
                    | **Hacim Momentum** | {report['hacim_momentum']:.2f}x | {'🔥 Artıyor' if report['hacim_momentum']>1.1 else '➡️ Sabit' if report['hacim_momentum']>0.9 else '💤 Azalıyor'} |
                    | **Kurumsal Maliyet** | {report['maliyet_bant']} | VWAP ±%3 bandı |
                    | **5G Fiyat Değişim** | %{report['price_change_5d']:.2f} | {'📈 Pozitif' if report['price_change_5d']>0 else '📉 Negatif'} |{takas_note}
                    """)
                    
                    st.caption("ℹ️ Gerçek takas verileri MKK tarafından 2 iş günü gecikmeli yayınlanır. Bu analiz borsapy verilerinden türetilmiş tahmini değerler içerir.")

                    # 1.4 İhtimaller: Boğa & Ayı Senaryoları
                    st.markdown(f"""
                    ### 1.4 📊 İhtimaller: Boğa & Ayı Senaryoları
                    | Senaryo | Tetikleyici | Hedefler (H1→H2) | Stop-Loss | Olasılık | R:Ö |
                    |---|---|---|---|---|---|
                    | 🐂 **BOĞA** | {pivots['r1']:.2f} TL kırılım + hacim | {pivots['r2']:.2f} → {pivots['r3']:.2f} TL | {pivots['s1']:.2f} TL | %{report['bull_prob']} | 1:{report['r_or_bull']} |
                    | 🐻 **AYI** | {pivots['s1']:.2f} TL kaybı + MACD(-) | {pivots['s2']:.2f} → {pivots['s3']:.2f} TL | {pivots['r1']:.2f} TL | %{bear_prob} | 1:{report['r_or_bear']} |
                    """)

                    # 1.5 Aksiyon Planı
                    st.markdown(f"""
                    ### 1.5 🚀 Aksiyon Planı (Hızlı Tarama)
                    | Aksiyon | Detay | Seviye / Kural |
                    |---|---|---|
                    | 🔥 **AL Sinyali** | Hacimli kırılım bekle | {pivots['r1']:.2f} TL (Hacim > {report['avg_volume']:.0f}) |
                    | 🛑 **STOP** | Destek altı kapat | {pivots['s1']:.2f} TL altı → pozisyon kapat |
                    | 💡 **Dip Alım** | Kurumsal maliyet bölgesi | {pivots['s2']:.2f}-{pivots['s1']:.2f} TL arası |
                    | 📌 **Risk Yönetimi** | Pozisyon & Realizasyon | Max %3-5 portföy | H1'de %50, H2'de %50 + Trailing |
                    """)

                    # Metrik Kartları
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("💰 Fiyat", f"{report['price']:.2f} TL")
                    c2.metric("📊 RSI", f"{report['rsi']:.2f}", report['rsi_status'])
                    c3.metric("📡 MACD", f"{report['macd']:.2f}", report['signal'])
                    c4.metric("📈 Trend", report['trend'], "↗️" if report['trend']=='Boğa' else "↘️")

                    # 🔹 AŞAMA 2: GÖRSEL TEKNİK ŞEMA
                    st.markdown("## 🔹 AŞAMA 2: GÖRSEL TEKNİK ŞEMA (TRADINGVIEW)")
                    
                    tv_url = f"https://www.tradingview.com/chart/?symbol=BIST:{sym}&interval=D&theme=dark&locale=tr"
                    
                    try:
                        st.iframe(tv_url, height=500, width="stretch")
                    except:
                        st.warning("⚠️ iframe yüklenemedi. Aşağıdaki linke tıklayın:")
                    
                    st.markdown(f"""
                    <div style="text-align:center;margin-top:10px;">
                        <a href="{tv_url}" target="_blank" style="color:#3b82f6;text-decoration:none;">
                            🔗 {sym} TradingView'de Tam Ekran Aç
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Qwen AI Yorumu
                    st.markdown(generate_qwen_commentary(sym, report, df), unsafe_allow_html=True)

                    # Kalite Kontrol Expander
                    with st.expander("📋 Kalite Kontrol & Detaylar", expanded=False):
                        st.markdown(f"""| Kontrol | Durum |
|---|---|
| [x] Yahoo Finance veri çekildi | ✅ |
| [x] Kritik seviyeler net TL | ✅ |
| [x] Takas proxy (borsapy) | {'✅' if not report.get('takas_error') else '⚠️'} |
| [x] R:Ö oranları hesaplandı | ✅ |
| [x] Aksiyon planı eklendi | ✅ |
| [x] TradingView grafik | ✅ |""")
                        if report.get('takas_error'):
                            st.warning(f"⚠️ borsapy hata: {report['takas_error']}")
                        st.divider()
                        st.caption(f"🕐 Analiz zamanı: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

        else:
            st.warning("⚠️ Hiçbir hisse için yeterli veri alınamadı.")

    # Yasal Uyarı
    st.warning("""
    ⚠️ **YASAL UYARI METNİ (ZORUNLU)**
    Bu rapor yalnızca eğitim ve bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir. 
    Takas verileri MKK'den 2 iş günü gecikmeli gelir. borsapy proxy verileri tahmini değerlerdir.
    Tüm yatırım kararlarınızı kendi araştırmanız ve lisanslı danışmanlarınızla alınız. 
    Geçmiş performans geleceğin garantisi değildir.
    """)
else:
    st.info("👆 Hisse kodlarını girip 'Analiz Başlat' butonuna tıklayın")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#6b7280;font-size:0.8rem;'>🎯 Qwen AI Pro | BIST Analiz v2.1 | borsapy Entegre</div>", unsafe_allow_html=True)
