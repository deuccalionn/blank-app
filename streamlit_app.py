import streamlit as st
import google.generativeai as genai
import io
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="Vatandaş Dili Çevirmeni", page_icon="⚖️")

st.title("⚖️ Vatandaş Dili Çevirmeni")
st.write("Sadeleştirmek istediğin hukuki metni veya fotoğrafını yükle.")

# 1. API Anahtarı Girişi
api_key = st.text_input("Google API Anahtarını Gir:", type="password")

# 2. Model Listesini Getir (Otomatik ve Kullanıcı Seçimi)
selected_model = None
vision_model_name = None # Görsel işleme için ayrı model adı
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        text_models = []
        vision_models = [] # Görsel işleme yapabilen modeller
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'vision' in m.name: # Görsel yeteneği olan modelleri bul
                    vision_models.append(m.name)
                else:
                    text_models.append(m.name)
        
        if text_models:
            st.success(f"✅ Bağlantı Başarılı! {len(text_models)} adet metin modeli bulundu.")
            selected_model = st.selectbox("Metin İşleme için Yapay Zekayı Seç:", text_models, index=text_models.index('gemini-1.5-flash') if 'gemini-1.5-flash' in text_models else 0)
        else:
            st.error("⚠️ Anahtar doğru ama hiç metin işleme modeli bulunamadı.")
            
        if vision_models:
            # Görsel için varsayılan olarak en popülerini seçiyoruz
            vision_model_name = 'gemini-pro-vision' if 'gemini-pro-vision' in vision_models else vision_models[0]
            st.info(f"📸 Görsel işleme için '{vision_model_name}' modeli kullanılacak.")

            # Test amaçlı manuel seçim de eklenebilir
            # vision_model_name = st.selectbox("Görsel İşleme için Yapay Zekayı Seç:", vision_models) # Debug için
        else:
            st.warning("Görsel işleme yapabilen model bulunamadı. Fotoğraf yükleme çalışmayabilir.")
            
    except Exception as e:
        st.error(f"API Anahtarı veya Model Listeleme Hatası: {e}")

# 3. Metin veya Fotoğraf Girişi (Tablar ile)
tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📸 Fotoğraf Yükle"])

user_input = ""
uploaded_file = None

with tab1:
    user_input = st.text_area("Sadeleştirilecek Metni Buraya Yapıştır:", height=150)

with tab2:
    uploaded_file = st.file_uploader("Evrak veya sözleşmenin fotoğrafını/PDF'ini yükle:", type=["jpg", "png", "jpeg", "pdf"])

# 4. Sadeleştir Butonu
if st.button("Sadeleştir"):
    if not api_key:
        st.error("Önce API anahtarını girmelisin.")
    elif not selected_model:
        st.error("Bir metin işleme modeli seçmelisin.")
    elif not user_input and not uploaded_file:
        st.warning("Lütfen metin yapıştır veya bir dosya yükle.")
    else:
        try:
            processed_content = ""
            
            with st.spinner(f'İçerik analiz ediliyor...'):
                if uploaded_file:
                    if uploaded_file.type == "application/pdf":
                        st.info("PDF dosyaları için OCR şu an doğrudan desteklenmiyor. Lütfen PDF'i görsel olarak kaydetmeyi dene.")
                        # PDF için farklı bir yaklaşıma ihtiyaç var (gelecek aşamalarda bakılabilir)
                        st.stop()
                    else:
                        # Görsel işleme kısmı
                        if not vision_model_name:
                            st.error("Görsel işleme yapabilen bir model bulunamadı.")
                            st.stop()
                            
                        # Resmi Image objesine dönüştür
                        image = Image.open(uploaded_file)
                        
                        st.info(f"📸 Fotoğraf '{vision_model_name}' modeli ile okunuyor...")
                        vision_model = genai.GenerativeModel(vision_model_name)
                        
                        # Görseldeki metni alma prompt'u
                        vision_prompt = "Bu görseldeki tüm yazıları, paragraf yapılarını ve önemli detayları eksiksiz bir şekilde metin olarak çıkar. Formatlama kurallarına uy."
                        
                        image_response = vision_model.generate_content([vision_prompt, image])
                        processed_content = image_response.text
                        st.text_area("Okunan Metin (Kontrol edebilirsin):", processed_content, height=150)
                        if not processed_content.strip():
                            st.error("Görselden metin çıkarılamadı veya çok az metin bulundu. Daha net bir fotoğraf dene.")
                            st.stop()
                else:
                    processed_content = user_input # Metin sekmesinden gelen içerik

                # Şimdi bu metni sadeleştirme modeli ile işleyelim
                model = genai.GenerativeModel(selected_model)
                
                final_prompt = f"""
                Sen uzman bir hukukçusun. Bu metni herkesin anlayacağı dilde özetle.
                Format:
                1. ÖZET
                2. RİSKLER (Varsa, madde madde ve kırmızı uyarı gibi)
                3. TAVSİYE (Ne yapması gerektiği hakkında kısa öneri)
                
                Metin: {processed_content}
                """
                
                response = model.generate_content(final_prompt)
                
                st.markdown("### 📝 Sonuç:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"İşlem Hatası: {e}")
            st.info("💡 İpucu: Model listelemede veya seçimde bir hata olmuş olabilir. Sayfayı yenileyip tekrar dene.")
