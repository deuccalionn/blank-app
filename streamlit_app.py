import streamlit as st
import google.generativeai as genai
import sys

st.title("🔍 Hata Dedektifi")

# 1. Kütüphane Versiyonunu Kontrol Et
try:
    version = genai.__version__
    st.info(f"Yüklü Olan Kütüphane Sürümü: {version}")
    
    # Eğer sürüm 0.8.3'ten küçükse sorun buradadır!
    if version < "0.8.3":
        st.error("❌ HATA BULUNDU: Kütüphane çok eski! requirements.txt dosyan okunmuyor.")
    else:
        st.success("✅ Kütüphane sürümü güncel.")
except:
    st.warning("Versiyon okunamadı.")

# 2. API Anahtarı Testi
api_key = st.text_input("API Anahtarını Yapıştır (Sonunda boşluk olmasın!)", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        st.write("Modeller aranıyor...")
        
        # Google'a bağlanıp hangi modelleri verdiğine bakalım
        found_any = False
        for m in genai.list_models():
            st.write(f"- {m.name}")
            found_any = True
            
        if not found_any:
            st.error("⚠️ Bağlantı kuruldu ama hiç model bulunamadı. API Key hatalı olabilir.")
    except Exception as e:
        st.error(f"💥 Büyük Hata: {e}")
