import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Aşağıdan çalışan modeli kendin seç ve metni sadeleştir.")

# 1. API Anahtarı Girişi
api_key = st.text_input("Google API Anahtarını Gir:", type="password")

# 2. Model Listesini Getir (Otomatik)
selected_model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Google'dan "Metin üretebilen" modelleri istiyoruz
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if model_list:
            st.success(f"✅ Bağlantı Başarılı! {len(model_list)} adet model bulundu.")
            # Kullanıcıya listeden seçtiriyoruz
            selected_model = st.selectbox("Kullanılacak Yapay Zekayı Seç:", model_list)
        else:
            st.error("⚠️ Anahtar doğru ama hiç model bulunamadı. Yeni bir API anahtarı almayı dene.")
            
    except Exception as e:
        st.error(f"API Anahtarı Hatası: {e}")

# 3. Metin Girişi ve İşlem
user_input = st.text_area("Sadeleştirilecek Metni Yapıştır:", height=150)

if st.button("Sadeleştir"):
    if not api_key:
        st.error("Önce API anahtarı girmelisin.")
    elif not selected_model:
        st.error("Bir model seçmelisin.")
    elif not user_input:
        st.warning("Metin boş olamaz.")
    else:
        try:
            # Seçilen modeli kullanıyoruz
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner(f'{selected_model} düşünüyor...'):
                prompt = f"""
                Sen uzman bir hukukçusun. Bu metni herkesin anlayacağı dilde özetle.
                Format:
                1. ÖZET
                2. RİSKLER (Varsa)
                3. TAVSİYE
                
                Metin: {user_input}
                """
                response = model.generate_content(prompt)
                st.markdown("### 📝 Sonuç:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Seçilen model ({selected_model}) hata verdi: {e}")
            st.info("💡 İpucu: Yukarıdaki kutudan 'gemini-1.5-flash' veya 'gemini-pro' içeren başka bir model seçip tekrar dene.")
