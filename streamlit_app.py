import streamlit as st
import google.generativeai as genai
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Metni yapıştır veya fotoğrafını çek, sadeleştirelim.")

# 1. API Anahtarı
api_key = st.text_input("Google API Anahtarını Gir:", type="password")

# 2. Model Seçimi (Filtresiz - Özgür Mod)
selected_model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Tüm metin üretebilen modelleri getiriyoruz (Ayrım yapmaksızın)
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if model_list:
            st.success(f"✅ {len(model_list)} adet model bulundu.")
            # Listeden "flash" içerenleri öne çıkarmaya çalışalım, yoksa ilkini seçelim
            default_index = 0
            for i, m_name in enumerate(model_list):
                if 'flash' in m_name and '1.5' in m_name:
                    default_index = i
                    break
            
            selected_model = st.selectbox("Kullanılacak Yapay Zekayı Seç:", model_list, index=default_index)
            st.caption("💡 İpucu: 'gemini-1.5-flash' veya 'gemini-2.5' gibi modeller hem metin hem fotoğraf okuyabilir.")
        else:
            st.error("⚠️ Hiç model bulunamadı. API anahtarını kontrol et.")
            
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")

# 3. Sekmeler (Metin vs Fotoğraf)
tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📸 Fotoğraf Yükle"])

user_input = ""
uploaded_file = None
input_type = "text" # Hangi modu kullandığımızı takip etmek için

with tab1:
    user_input = st.text_area("Sözleşme metnini buraya yapıştır:", height=150)
    if user_input:
        input_type = "text"

with tab2:
    uploaded_file = st.file_uploader("Sözleşme fotoğrafını yükle:", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        input_type = "image"
        st.image(uploaded_file, caption="Yüklenen Belge", width=300)

# 4. Sadeleştir Butonu
if st.button("Analiz Et ve Sadeleştir"):
    if not api_key or not selected_model:
        st.error("Lütfen API anahtarı gir ve bir model seç.")
    elif not user_input and not uploaded_file:
        st.warning("Lütfen metin veya fotoğraf yükle.")
    else:
        try:
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner('Yapay zeka avukatınız inceliyor...'):
                
                # Ortak Prompt (İstek)
                base_prompt = """
                Sen uzman bir hukukçusun. Bu içeriği analiz et.
                Lütfen şu formatta çıktı ver:
                1. 📄 ÖZET: Bu belge ne hakkında? (Tek cümle)
                2. ⚠️ RİSKLER: İmzalamadan önce dikkat edilmesi gereken tehlikeli maddeler.
                3. ✅ TAVSİYE: Ne yapmalıyım?
                
                Analiz edilecek içerik aşağıdadır:
                """
                
                response = None
                
                # Duruma göre işlem yap
                if input_type == "image" and uploaded_file:
                    # Görseli aç
                    image = Image.open(uploaded_file)
                    # Prompt + Görseli aynı anda gönderiyoruz (Yeni modeller bunu sever)
                    response = model.generate_content([base_prompt, image])
                else:
                    # Sadece metin gönderiyoruz
                    response = model.generate_content(base_prompt + user_input)
                
                # Sonucu Yazdır
                st.markdown("---")
                st.success("İşlem Tamamlandı!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            if "image" in str(e) or "vision" in str(e) or "support" in str(e):
                st.warning("⚠️ Seçtiğin model fotoğraf desteklemiyor olabilir. Lütfen yukarıdan 'gemini-1.5-flash' veya 'pro' içeren başka bir model seçip tekrar dene.")
