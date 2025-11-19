import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Vatandaş Dili Çevirmeni",
    page_icon="⚖️",
    layout="wide"
)

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2643/2643496.png", width=80)
    st.title("Ayarlar")
    
    st.info("🔑 Önce Anahtarını Gir")
    api_key = st.text_input("Google API Anahtarı", type="password", help="Google AI Studio'dan aldığın şifre.")
    
    st.divider()
    
    # Gelişmiş Ayarlar (Model Seçimi)
    with st.expander("⚙️ Teknik Ayarlar (Model Seçimi)"):
        selected_model = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model_list = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        model_list.append(m.name)
                
                if model_list:
                    # Flash modelini öne çıkar
                    default_idx = 0
                    for i, m_name in enumerate(model_list):
                        if 'flash' in m_name and '1.5' in m_name:
                            default_idx = i
                            break
                    selected_model = st.selectbox("Yapay Zeka Modeli:", model_list, index=default_idx)
                else:
                    st.error("Model bulunamadı.")
            except:
                st.error("API Anahtarı hatalı.")
        else:
            st.warning("Model seçmek için önce API anahtarı girin.")

    st.markdown("---")
    st.caption("© 2025 Vatandaş Dili Çevirmeni\nYapay Zeka Destekli Hukuk Asistanı")

# --- ANA EKRAN ---
st.title("⚖️ Vatandaş Dili Çevirmeni")
st.markdown("""
**Hoş Geldiniz.** Karmaşık hukuk dilinden kurtulun. 
Sözleşmeleri, resmi evrakları veya banka yazılarını yükleyin; **sizin dilinize çevirelim.**
""")

if not api_key:
    st.warning("⬅️ Lütfen sol menüden API Anahtarınızı girerek başlayın.")
    st.stop()

# Sekmeler
tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📸 Fotoğraf Yükle"])
user_input = ""
uploaded_file = None
input_type = "text"

with tab1:
    user_input = st.text_area("Metni buraya yapıştırın:", height=250, placeholder="Örn: Kiracı, mecuru tahliye ederken...")

with tab2:
    uploaded_file = st.file_uploader("Belge fotoğrafı yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        input_type = "image"
        st.image(uploaded_file, caption="Yüklenen Belge", width=400)

# Buton ve İşlem
if st.button("🚀 Analiz Et ve Sadeleştir", type="primary"): # Primary butonu daha dikkat çekici yapar
    if not selected_model:
        st.error("Lütfen yan menüden model seçildiğine emin olun.")
    elif not user_input and not uploaded_file:
        st.warning("Lütfen analiz edilecek bir içerik sağlayın.")
    else:
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner('Hukuk asistanınız belgeyi inceliyor... 🧐'):
                
                base_prompt = """
                Sen tarafsız ve uzman bir hukukçusun. Bu içeriği vatandaşın anlayacağı sade bir Türkçe ile analiz et.
                Çıktıyı şu başlıklar altında ver:
                
                1. 📄 ÖZET (Belge ne anlatıyor, tek cümle)
                2. ⚠️ RİSKLER VE TUZAKLAR (Beni zora sokacak maddeler var mı? Varsa kırmızı uyarı işaretiyle belirt)
                3. ✅ İYİ YANLAR (Benim lehime olan kısımlar)
                4. 💡 SONUÇ TAVSİYESİ (İmzalamalı mıyım? Pazarlık mı etmeliyim?)
                
                İçerik:
                """
                
                response = None
                if input_type == "image" and uploaded_file:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([base_prompt, image])
                else:
                    response = model.generate_content(base_prompt + user_input)
                
                # SONUÇ EKRANI
                st.success("Analiz Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# Yasal Uyarı (Footer)
st.markdown("---")
st.info("⚠️ **Yasal Uyarı:** Bu uygulama yapay zeka ile bilgilendirme amaçlıdır. Hukuki tavsiye yerine geçmez. Kesin kararlar için mutlaka bir avukata danışınız.")
