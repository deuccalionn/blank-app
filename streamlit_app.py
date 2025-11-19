import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

# Başlık
st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Sadeleştirmek istediğin hukuki metni yapıştır.")

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
            genai.configure(api_key=api_key)
            
            # DİREKT HEDEF: En stabil ve ücretsiz model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('Yapay zeka inceliyor...'):
                prompt = f"""
                Sen uzman bir hukukçusun. Bu metni halk diline çevir.
                Format:
                1. ÖZET (Tek cümle)
                2. RİSKLER (Varsa kırmızı uyarı ile)
                3. TAVSİYE
                
                Metin: {user_input}
                """
                response = model.generate_content(prompt)
                st.markdown("### 📝 Sonuç:")
                st.markdown(response.text)
                
        except Exception as e:
            # Hata mesajını güzelleştiriyoruz
            if "404" in str(e):
                st.error("Hata: Model bulunamadı. Lütfen requirements.txt dosyanda 'google-generativeai>=0.8.3' yazdığından emin ol.")
            elif "429" in str(e):
                st.error("Hata: Çok fazla istek gönderildi veya kota doldu. Biraz bekle.")
            else:
                st.error(f"Bir hata oluştu: {e}")
