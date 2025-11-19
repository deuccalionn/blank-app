import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Vatandaş Dili Çevirmeni",
    page_icon="⚖️",
    layout="wide"
)

# --- GİZLİ ANAHTARI ALMA ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("Sistem Hatası: API Anahtarı bulunamadı. Secrets ayarlarını kontrol et.")
        st.stop()
except Exception as e:
    st.error(f"Anahtar okuma hatası: {e}")
    st.stop()

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9252/9252103.png", width=80)
    st.title("Hukuk Asistanı")
    st.success("🟢 Sistem Çevrimiçi")
    
    st.divider()
    
    # GÜVENLİ MODEL SEÇİMİ (FİLTRELİ)
    with st.expander("⚙️ Model Ayarı", expanded=True): # Açık gelsin ki kullanıcı görsün
        selected_model = None
        try:
            genai.configure(api_key=api_key)
            model_list = []
            
            # BURASI YENİ: Sadece güvenli modelleri listele
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # 'exp' (deneysel) olanları VE 'vision' olmayan eski modelleri ele
                    # Sadece kararlı (1.5) sürümleri al
                    if 'exp' not in m.name and '1.5' in m.name:
                        model_list.append(m.name)
            
            # Listeyi bulamazsa manuel ekle (Garanti Yöntem)
            if not model_list:
                model_list = ['gemini-1.5-flash', 'gemini-1.5-pro']

            # En hızlısı (Flash) varsayılan olsun
            default_idx = 0
            for i, m_name in enumerate(model_list):
                if 'flash' in m_name:
                    default_idx = i
                    break
            
            selected_model = st.selectbox("Yapay Zeka:", model_list, index=default_idx)
            st.caption("✅ Sadece ücretsiz kotası olan modeller listeleniyor.")
            
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")

    st.info("""
    **Nasıl Kullanılır?**
    1. Sözleşmenin fotoğrafını çek veya metni yapıştır.
    2. 'Analiz Et' butonuna bas.
    """)

# --- ANA EKRAN ---
st.title("⚖️ Vatandaş Dili Çevirmeni")
st.markdown("""
**Hoş Geldiniz.** Karmaşık hukuk dilinden kurtulun. 
Resmi evrakları yükleyin; **sizin dilinize, riskleri vurgulayarak çevirelim.**
""")

# Sekmeler
tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📸 Fotoğraf Yükle"])
user_input = ""
uploaded_file = None
input_type = "text"

with tab1:
    user_input = st.text_area("Metni buraya yapıştırın:", height=200, placeholder="Örn: Kiracı, mecuru tahliye ederken...")

with tab2:
    uploaded_file = st.file_uploader("Belge fotoğrafı yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        input_type = "image"
        st.image(uploaded_file, caption="İncelenecek Belge", width=400)

# İşlem Butonu
if st.button("🚀 Analiz Et ve Sadeleştir", type="primary"):
    if not user_input and not uploaded_file:
        st.warning("Lütfen önce analiz edilecek bir içerik sağlayın.")
    else:
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner('Yapay zeka avukatınız belgeyi inceliyor... 🧐'):
                
                base_prompt = """
                Sen tarafsız, zeki ve halkın dostu bir hukukçusun. Bu içeriği analiz et.
                Çıktıyı çok net, okunaklı ve şu başlıklar altında ver:
                
                1. 📄 ÖZET (Belge ne anlatıyor? 1-2 cümle)
                2. ⚠️ RİSKLER ve TUZAKLAR (Beni zora sokacak, para kaybettirecek maddeler var mı? Varsa kırmızı ile vurgula)
                3. ✅ LEHİME OLANLAR (Benim yararıma olan maddeler)
                4. 💡 SONUÇ TAVSİYESİ (İmzalamalı mıyım? Hangi maddeye itiraz etmeliyim?)
                
                Analiz edilecek içerik:
                """
                
                response = None
                if input_type == "image" and uploaded_file:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([base_prompt, image])
                else:
                    response = model.generate_content(base_prompt + user_input)
                
                # SONUÇLARI GÖSTER
                st.success("Analiz Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            # Hata mesajını daha anlaşılır hale getirelim
            if "429" in str(e):
                st.error("⚠️ Çok hızlı işlem yaptınız veya ücretsiz kota doldu. Lütfen 30 saniye bekleyip tekrar deneyin.")
            else:
                st.error(f"Hata: {e}")

# Footer
st.markdown("---")
st.warning("⚠️ **Yasal Uyarı:** Bu sonuçlar yapay zeka tarafından üretilmiştir ve hukuki tavsiye yerine geçmez.")
