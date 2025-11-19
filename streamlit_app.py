import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Resmi evrakları yapıştır, senin için sadeleştirelim.")

# API Anahtarı
api_key = st.text_input("Google API Anahtarını Gir:", type="password")
user_input = st.text_area("Metni buraya yapıştır:", height=150)

def get_model_and_generate(api_key, prompt):
    """Bu fonksiyon doğru modeli bulana kadar dener."""
    genai.configure(api_key=api_key)
    
    # Denenecek Modeller Listesi (Sırasıyla)
    model_list = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro-latest']
    
    last_error = ""
    
    for model_name in model_list:
        try:
            # Modeli dene
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name # Başarılı olursa sonucu ve model adını döndür
        except Exception as e:
            # Hata alırsan kaydet ve sonraki modele geç
            last_error = e
            continue
            
    # Listettekiler çalışmazsa, sistemdeki rastgele bir modeli dene
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content(prompt)
                return response.text, m.name
    except:
        pass

    # Hiçbiri çalışmazsa hatayı fırlat
    raise Exception(f"Hiçbir model çalışmadı. Son hata: {last_error}")

if st.button("Sadeleştir"):
    if not api_key:
        st.error("Lütfen API anahtarını gir.")
    elif not user_input:
        st.warning("Metin girmelisin.")
    else:
        try:
            with st.spinner('Yapay zeka uygun modeli bulup analiz ediyor...'):
                
                prompt = f"""
                Sen uzman bir hukukçusun. Bu metni halk diline çevir.
                Format:
                1. ÖZET (Tek cümle)
                2. RİSKLER (Varsa kırmızı uyarı ile)
                3. TAVSİYE
                
                Metin: {user_input}
                """
                
                # Fonksiyonu çağır
                result_text, used_model = get_model_and_generate(api_key, prompt)
                
                st.success(f"✅ İşlem Başarılı! (Kullanılan Model: {used_model})")
                st.markdown("### 📝 Sonuç:")
                st.markdown(result_text)
                
        except Exception as e:
            st.error(f"Üzgünüm, bir hata oluştu: {e}")
