# 🖥️ ANA AKIŞ - KESİN DÜZELTİLMİŞ
if run_btn or stocks:
    with st.spinner('📡 Yahoo Finance verileri çekiliyor & Qwen AI Pro analiz ediliyor...'):
        # ✅ 1. Düzeltme: all_ yerine boş bir sözlük tanımladık
        all_data = {}
        
        for s in stocks:
            df, err = fetch_data(s, yf_period)
            if err: 
                st.error(f"❌ {s}: {err}")
            else:
                df = calc_indicators(df)
                if len(df) > 20: 
                    # ✅ 2. Düzeltme: Veriyi sözlüğe kaydettik
                    all_data[s] = {'df': df}
        
        # ✅ 3. Düzeltme: Kontrol ifadesi ve değişken adı düzeltildi
        if all_data:
            st.success(f"✅ {len(all_data)} hisse başarıyla analiz edildi.")
            tabs = st.tabs([f"📈 {s}" for s in all_data.keys()])
            
            for i, (sym, data) in enumerate(all_data.items()):
                with tabs[i]:
                    df = data['df']
                    pivots = calc_pivots(df)
                    report = generate_report(sym, data)
                    formasyon, guven = report['formasyon'], report['formasyon_guven']
                    
                    # ✅ 4. Düzeltme: Yarım kalan satır tamamlandı
                    bear_prob = 100 - report['bull_prob']
                    
                    # --- Buradan sonrası normal devam edecektir ---
                    st.markdown(f"### {sym} - Analiz Sonuçları")
                    st.write(f"**Formasyon:** {formasyon} (Güven: %{guven})")
                    # ...
