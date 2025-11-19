import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Vatandaş Dili Çevirmeni",
    page_icon="⚖️",
    layout="wide"
)

# --- HAFIZA (SESSION STATE) BAŞLATMA ---
# Belgeyi ve sohbet geçmişini burada tutacağız
if "analyzed_text" not in st.session_state:
    st.session_state.analyzed_text = "" # Okunan metin burada saklanacak

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # Soru-cevap geçmişi

# --- GİZLİ ANAHTAR ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("API Anahtarı bulunamadı.")
        st.stop()
except:
    st.stop()

# --- YAN MENÜ ---
with st.sidebar:
    st.title("⚖️ Hukuk Asistanı")
    st.success("🟢 Sistem Aktif")
    
    # Temizle Butonu
    if st.button("🗑️ Yeni Belge Yükle / Temizle"):
        st.session_state.analyzed_text = ""
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # Model Seçimi
    with st.expander("⚙️ Model Ayarları"):
        try:
            genai.configure(api_key=api_key)
            model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and '1.5' in m.name and 'exp' not in m.name]
            if not model_list: model_list = ['gemini-1.5-flash']
            selected_model = st.selectbox("Yapay Zeka:", model_list)
        except:
            st.error("Bağlantı sorunu.")

# --- ANA EKRAN ---
st.title("📄 Belgenle Sohbet Et")
st.markdown("Belgeni yükle, önce özetleyelim, sonra **aklın takılanları sor.**")

# Eğer hafızada metin yoksa yükleme ekranını göster
if not st.session_state.analyzed_text:
    tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📂 PDF/Foto Yükle"])
    
    raw_text = ""
    
    with tab1:
        text_input = st.text_area("Metni buraya yapıştır:", height=200)
        if st.button("Metni Analiz Et"):
            raw_text = text_input

    with tab2:
        uploaded_file = st.file_uploader("Belge yükle (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"])
        if uploaded_file and st.button("Dosyayı Analiz Et"):
            with st.spinner("Okunuyor..."):
                if "pdf" in uploaded_file.type:
                    try:
                        reader = pypdf.PdfReader(uploaded_file)
                        for page in reader.pages:
                            raw_text += page.extract_text() + "\n"
                    except: st.error("PDF okunamadı.")
                else: # Görsel
                    try:
                        img = Image.open(uploaded_file)
                        model = genai.GenerativeModel(selected_model)
                        response = model.generate_content(["Bu görseldeki metni aynen çıkar:", img])
                        raw_text = response.text
                    except: st.error("Görsel okunamadı.")

    # Eğer metin alındıysa hafızaya at ve sayfayı yenile
    if raw_text:
        st.session_state.analyzed_text = raw_text
        st.rerun()

# --- ANALİZ VE SOHBET EKRANI ---
else:
    # 1. Önce Ana Özeti Göster (Eğer henüz sohbet başlamadıysa)
    if not st.session_state.chat_history:
        with st.spinner("Avukatınız belgeyi inceliyor..."):
            try:
                model = genai.GenerativeModel(selected_model)
                summary_prompt = f"""
                Bu hukuki metni analiz et.
                1. ÖZET (1 cümle)
                2. RİSKLER (Varsa)
                3. TAVSİYE
                Metin: {st.session_state.analyzed_text[:10000]}
                """
                summary = model.generate_content(summary_prompt).text
                st.info("📊 **Hızlı Analiz Raporu**")
                st.markdown(summary)
                # İlk analizi de geçmişe ekle
                st.session_state.chat_history.append({"role": "assistant", "content": summary})
            except Exception as e:
                st.error(f"Hata: {e}")

    st.divider()
    st.subheader("💬 Bu belge hakkında bir soru sor:")

    # 2. Sohbet Geçmişini Göster
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    # 3. Yeni Soru Girişi
    if prompt := st.chat_input("Örn: Depozito maddesi ne diyor?"):
        # Kullanıcı mesajını ekle
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Yapay Zeka Cevabı
        with st.chat_message("assistant"):
            with st.spinner("Cevap hazırlanıyor..."):
                try:
                    model = genai.GenerativeModel(selected_model)
                    full_prompt = f"""
                    Sen bir hukuk asistanısın. Aşağıdaki BELGE METNİNE dayanarak kullanıcının sorusunu cevapla.
                    Uydurma, sadece belgede yazanı söyle.
                    
                    BELGE METNİ: {st.session_state.analyzed_text[:10000]}
                    
                    KULLANICI SORUSU: {prompt}
                    """
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Hata: {e}")
