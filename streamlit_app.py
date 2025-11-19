import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import io

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Vatandaş Dili Çevirmeni",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS İLE GÜZELLEŞTİRME (İsteğe Bağlı) ---
st.markdown("""
<style>
    .stChatMessage {border-radius: 10px; padding: 10px;}
    .stButton button {border-radius: 20px;}
</style>
""", unsafe_allow_html=True)

# --- HAFIZA BAŞLATMA ---
if "analyzed_text" not in st.session_state:
    st.session_state.analyzed_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary_report" not in st.session_state:
    st.session_state.summary_report = ""

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
    st.image("https://cdn-icons-png.flaticon.com/512/9252/9252103.png", width=80)
    st.title("Hukuk Asistanı")
    
    # Temizle Butonu
    if st.button("🗑️ Yeni Belge / Temizle", use_container_width=True):
        st.session_state.analyzed_text = ""
        st.session_state.chat_history = []
        st.session_state.summary_report = ""
        st.rerun()
    
    st.divider()
    
    with st.expander("⚙️ Model Ayarları"):
        try:
            genai.configure(api_key=api_key)
            model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and '1.5' in m.name and 'exp' not in m.name]
            if not model_list: model_list = ['gemini-1.5-flash']
            selected_model = st.selectbox("Yapay Zeka:", model_list)
        except:
            st.error("Bağlantı sorunu.")
            
    st.info("💡 **İpucu:** Kira sözleşmesi, banka kredisi veya ihtarname yükleyebilirsiniz.")

# --- FONKSİYONLAR ---
def get_gemini_response(prompt_text):
    model = genai.GenerativeModel(selected_model)
    full_prompt = f"""
    Sen bir hukuk asistanısın. Aşağıdaki BELGE METNİNE dayanarak cevap ver.
    
    BELGE METNİ: {st.session_state.analyzed_text[:15000]}
    
    SORU/İSTEK: {prompt_text}
    """
    return model.generate_content(full_prompt).text

# --- ANA EKRAN ---
st.title("📄 Belgenle Sohbet Et")

# 1. YÜKLEME EKRANI
if not st.session_state.analyzed_text:
    st.markdown("Belgeni yükle, **gizli riskleri bulalım** ve **aklın takılanları cevaplayalım.**")
    
    tab1, tab2 = st.tabs(["📄 Metin Yapıştır", "📂 PDF/Foto Yükle"])
    raw_text = ""
    
    with tab1:
        text_input = st.text_area("Metni buraya yapıştır:", height=200)
        if st.button("Metni Analiz Et", type="primary"):
            raw_text = text_input

    with tab2:
        uploaded_file = st.file_uploader("Dosya seç (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"])
        if uploaded_file and st.button("Dosyayı Analiz Et", type="primary"):
            with st.spinner("Belge taranıyor..."):
                if "pdf" in uploaded_file.type:
                    try:
                        reader = pypdf.PdfReader(uploaded_file)
                        for page in reader.pages:
                            raw_text += page.extract_text() + "\n"
                    except: st.error("PDF okunamadı.")
                else:
                    try:
                        img = Image.open(uploaded_file)
                        model = genai.GenerativeModel(selected_model)
                        response = model.generate_content(["Bu görseldeki metni formatını koruyarak çıkar:", img])
                        raw_text = response.text
                    except: st.error("Görsel okunamadı.")

    if raw_text:
        st.session_state.analyzed_text = raw_text
        st.rerun()

# 2. ANALİZ VE SOHBET EKRANI
else:
    # Otomatik Özet (Sadece ilk seferde)
    if not st.session_state.chat_history:
        with st.spinner("Yapay zeka avukatınız belgeyi inceliyor..."):
            try:
                summary_prompt = """
                Bu hukuki metni analiz et. Çıktı formatı:
                ## 📊 Belge Özeti
                **Konu:** ...
                **Riskler:** (Madde madde, varsa ⚠️ ikonu ile)
                **Tavsiye:** ...
                """
                summary = get_gemini_response(summary_prompt)
                st.session_state.summary_report = summary # İndirmek için sakla
                st.session_state.chat_history.append({"role": "assistant", "content": summary})
            except Exception as e:
                st.error(f"Analiz hatası: {e}")

    # Rapor İndirme Butonu (Sağ üst köşe gibi)
    col1, col2 = st.columns([3, 1])
    with col2:
        st.download_button(
            label="📥 Analizi İndir (TXT)",
            data=st.session_state.summary_report,
            file_name="hukuk_analizi.txt",
            mime="text/plain"
        )

    # Sohbet Geçmişini Göster
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # HIZLI SORU BUTONLARI
    st.write("")
    st.markdown("##### ⚡ Hızlı Sorular:")
    b1, b2, b3, b4 = st.columns(4)
    
    prompt_trigger = None
    
    if b1.button("Para/Ceza Var mı? 💰"): prompt_trigger = "Bu belgede para cezası, tazminat veya ekstra ödeme gerektiren maddeler var mı?"
    if b2.button("Ne Zaman Biter? 📅"): prompt_trigger = "Sözleşme süresi ne kadar, fesih tarihleri ve koşulları neler?"
    if b3.button("Riskli Madde? ⚠️"): prompt_trigger = "İmzalamadan önce dikkat etmem gereken en tehlikeli madde hangisi?"
    if b4.button("Hakkım Nedir? ⚖️"): prompt_trigger = "Bu belgeye göre yasal haklarım ve avantajlarım neler?"

    # Chat Girişi
    user_input = st.chat_input("Veya kendi sorunu yaz...")

    # İşlem Mantığı (Buton veya Yazı)
    prompt = prompt_trigger if prompt_trigger else user_input

    if prompt:
        # Kullanıcı mesajını ekle
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Cevap Üret
        with st.chat_message("assistant"):
            with st.spinner("Cevap yazılıyor..."):
                response_text = get_gemini_response(prompt)
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
