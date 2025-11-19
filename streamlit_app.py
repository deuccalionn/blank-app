import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

# Başlık
st.title("⚖️ Vatandaş Dili Çevirmeni (Otomatik Mod)")
st.write("Resmi evrakları yapıştır, sistem en uygun yapay zekayı bulup sadeleştirsin.")

# API Anahtarı
api_key = st.text_input("Google API Anahtarını Gir:", type="password")

# Giriş Alanı
user_input = st.text_area("Metni buraya yapıştır:", height=150)

if st.button("Sadeleştir"):
    if not api_key:
        st.error("Lütfen API anahtarını gir.")
    elif not user_input:
        st.warning("Metin girmelisin.")
    else:
        try:
            # 1. Bağlantıyı Kur
            genai.configure(api_key=api_key)
            
            # 2. ÇALIŞAN MODELİ OTOMATİK BUL (Sihirli Kısım Burası)
            available_model = None
            status_msg = st.empty()
            status_msg.info("Uygun yapay zeka modeli aranıyor...")
            
            try:
                # Google'a sor: Hangi modellerin var?
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # İlk bulduğun metin üretebilen modeli seç
                        available_model = m.name
                        break
            except Exception as list_error:
                st.error(f"Modeller listelenemedi. API Anahtarı hatalı olabilir mi? Hata: {list_error}")
                st.stop()

            if available_model:
                status_msg.success(f"✅ Bulunan Model: {available_model} kullanılıyor.")
                
                # 3. Analizi Yap
                model = genai.GenerativeModel(available_model)
                prompt = f"""
                Sen uzman bir hukukçusun. Bu metni halk diline çevir.
                Format:
                1. ÖZET (Tek cümle)
                2. RİSKLER (Varsa)
                3. TAVSİYE
                
                Metin: {user_input}
                """
                response = model.generate_content(prompt)
                st.markdown("### 📝 Sonuç:")
                st.markdown(response.text)
            else:
                st.error("❌ Hiçbir uygun model bulunamadı. API Key yetkilerini kontrol et.")
                
        except Exception as e:
            st.error(f"Büyük Hata: {e}")
