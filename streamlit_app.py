import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf # PDF okumak için yeni kütüphanemiz

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Vatandaş Dili Çevirmeni",
    page_icon="⚖️",
    layout="wide"
)

# --- GİZLİ ANAHTAR KONTROLÜ ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("Sistem Hatası: API Anahtarı bulunamadı.")
        st.stop()
except Exception as e:
    st.error(f"Anahtar hatası: {e}")
    st.stop()

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9252/9252103.png", width=80)
    st.title("Hukuk Asistanı")
    st.success("🟢 Sistem Aktif")
    st.divider()
    
    # Model Seçimi
    with st.expander("⚙️ Model Ayarları", expanded=True):
        selected_model = None
        try:
            genai.configure(api_key=api_key)
            model_list = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'exp' not in m.name and '1.5' in m.name:
                        model_list.append(m.name)
            
            if not model_list: model_list = ['gemini-1.5-flash']
            
            # Varsayılan: Flash
            def_idx = 0
            for i, n in enumerate(model_list):
                if 'flash' in n: def_idx = i; break
                
            selected_model = st.selectbox("Yapay Zeka:", model_list, index=def_idx)
            st.caption("✅ PDF ve Görsel Destekli")
        except:
            st.error("Bağlantı hatası.")

# --- ANA EKRAN ---
st.title("⚖️ Vatandaş Dili Çevirmeni")
st.markdown("""
**Hoş Geldiniz.** Elinizdeki **PDF sözleşmeleri, fotoğrafları veya metinleri** yükleyin.
Hukuk dilini sizin için sadeleştirelim, riskleri bulalım.
""")

# Sekmeler
tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📂 Dosya Yükle (PDF/Foto)"])

user_input = ""
uploaded_file = None
input_type = "text"
extracted_text = "" # PDF'ten çıkan metin için

with tab1:
    user_input = st.text_area("Metni buraya yapıştırın:", height=200, placeholder="Kopyaladığınız metni buraya yapıştırın...")

with tab2:
    # Artık PDF de kabul ediyoruz
    uploaded_file = st.file_uploader("Belge yükleyin:", type=["jpg", "png", "jpeg", "pdf"])
    
    if uploaded_file:
        file_type = uploaded_file.type
        
        # GÖRSEL İSE
        if "image" in file_type:
            input_type = "image"
            st.image(uploaded_file, caption="İncelenecek Görsel", width=400)
            
        # PDF İSE (YENİ ÖZELLİK)
        elif "pdf" in file_type:
            input_type = "pdf"
            st.info(f"📄 PDF Yüklendi: {uploaded_file.name}")
            
            # PDF'ten metin ayıklama işlemi
            try:
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                
                if extracted_text.strip():
                    with st.expander("🔍 PDF'ten Okunan Metni Gör"):
                        st.text(extracted_text[:1000] + "...") # İlk 1000 karakteri göster
                else:
                    st.warning("⚠️ Bu PDF resimlerden oluşuyor olabilir (Taranmış belge). Metin okunamadı. Lütfen fotoğrafını çekip yüklemeyi deneyin.")
            except Exception as e:
                st.error(f"PDF okuma hatası: {e}")

# Buton
if st.button("🚀 Analiz Et ve Sadeleştir", type="primary"):
    if not user_input and not uploaded_file:
        st.warning("Lütfen önce bir içerik yükleyin.")
    else:
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner('Belge inceleniyor, riskler taranıyor... 🧐'):
                
                base_prompt = """
                Sen uzman bir hukukçusun. Bu içeriği analiz et.
                Çıktıyı şu başlıklar altında ver:
                
                1. 📄 ÖZET (Belge ne anlatıyor? 1-2 cümle)
                2. ⚠️ RİSKLER ve TUZAKLAR (Beni zora sokacak maddeler neler? Kırmızı ile vurgula)
                3. ✅ LEHİME OLANLAR (Benim yararıma olan maddeler)
                4. 💡 SONUÇ TAVSİYESİ (İmzalamalı mıyım?)
                
                Analiz edilecek içerik:
                """
                
                response = None
                
                # 1. PDF Modu (Metne çevrilmiş hali)
                if input_type == "pdf" and extracted_text:
                    response = model.generate_content(base_prompt + extracted_text)
                
                # 2. Görsel Modu
                elif input_type == "image" and uploaded_file:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([base_prompt, image])
                
                # 3. Düz Metin Modu
                else:
                    # Eğer PDF metni boşsa ve kullanıcı metin yapıştırmışsa onu kullan
                    text_to_send = user_input if user_input else extracted_text
                    if text_to_send:
                         response = model.generate_content(base_prompt + text_to_send)
                    else:
                        st.error("İçerik okunamadı.")
                        st.stop()

                # SONUÇ
                st.success("İşlem Başarılı!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
            st.info("İpucu: PDF çok büyükse veya şifreliyse okunamayabilir.")

# Footer
st.markdown("---")
st.caption("Bu uygulama yapay zeka desteklidir.")
