import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

# Başlık
st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Resmi evrakları veya karmaşık metinleri yapıştır, senin için sadeleştirelim.")

# API Anahtarı Girişi
api_key = st.text_input("Google AI Studio'dan aldığın API Anahtarını buraya gir:", type="password")

# Metin Giriş Alanı
user_input = st.text_area("Sözleşme veya resmi yazıyı buraya yapıştır:", height=200)

# Buton
if st.button("Bunu Benim İçin Sadeleştir"):
    if not api_key:
        st.error("Lütfen önce API anahtarını gir.")
    elif not user_input:
        st.warning("Lütfen bir metin yapıştır.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner('Yapay zeka metni inceliyor...'):
                prompt = f"""
                Sen uzman bir hukuk danışmanısın ama 5 yaşındaki bir çocuğa anlatır gibi konuşuyorsun.
                Aşağıdaki metni analiz et ve şu formatta Türkçe çıktı ver:
                1. ÖZET: Bu belge ne hakkında? (Tek cümle)
                2. RİSKLER: İmzalamadan önce dikkat edilmesi gereken tehlikeli maddeler (Varsa).
                3. SONUÇ: Ne yapmalıyım?
                
                Metin: {user_input}
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
