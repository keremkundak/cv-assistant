import streamlit as st
import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from streamlit_autorefresh import st_autorefresh

# Modülleri içe aktar
from utils.text_assets import get_texts
from utils.helpers import load_css, send_email, load_cv_text, create_transcript

# --- 1. YAPILANDIRMA ---
st.set_page_config(
    page_title="Kerem - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Yükle
load_css("assets/style.css")

# --- 2. AYARLAR VE VERİLER ---
required_secrets = ["GOOGLE_API_KEY", "EMAIL_ADDRESS", "EMAIL_PASSWORD", "TARGET_EMAIL", "CV_ENCRYPTION_KEY"]
for secret in required_secrets:
    if secret in st.secrets:
        os.environ[secret] = st.secrets[secret]

TEXTS = get_texts()

if "language" not in st.session_state: st.session_state.language = "en"
def t(key): return TEXTS[st.session_state.language][key]

# Zamanlayıcı (İnaktiflik kontrolü)
TIMEOUT_SECONDS = 30
st_autorefresh(interval=300, key="inactivity_checker")

# --- 3. OTURUM YÖNETİMİ ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_info" not in st.session_state: st.session_state.user_info = None
if "cv_text" not in st.session_state: st.session_state.cv_text = None
if "last_interaction" not in st.session_state: st.session_state.last_interaction = time.time()
if "kvkk_approved" not in st.session_state: st.session_state.kvkk_approved = False

# CV Metnini Yükle
if st.session_state.cv_text is None: st.session_state.cv_text = load_cv_text()

# --- 4. ZAMAN AŞIMI ---
if st.session_state.user_info and len(st.session_state.chat_history) > 0:
    if time.time() - st.session_state.last_interaction > TIMEOUT_SECONDS:
        transcript = create_transcript("Timeout", st.session_state.user_info, st.session_state.chat_history, st.session_state.language)
        send_email(f"{t('mail_subject_timeout')} - {st.session_state.user_info['name']}", transcript)
        # Oturumu Sıfırla
        st.session_state.chat_history = []
        st.session_state.user_info = None
        st.session_state.kvkk_approved = False
        st.rerun()

# --- 5. KVKK DIALOG ---
@st.dialog("📜 Policy")
def open_kvkk_modal():
    st.markdown(t("kvkk_modal_title"))
    st.markdown(t("kvkk_modal_body"))
    st.write("")
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button(t("kvkk_modal_btn"), type="primary", use_container_width=True):
            st.session_state.kvkk_approved = True
            st.rerun()

# ==========================================
# 🛑 GİRİŞ EKRANI
# ==========================================
if st.session_state.user_info is None:
    
    # DİL SEÇİMİ
    col_lang1, col_lang2, _ = st.columns([0.12, 0.12, 0.76], gap="small")
    with col_lang1:
        if st.button("🇬🇧 EN"): st.session_state.language = "en"; st.rerun()
    with col_lang2:
        if st.button("🇹🇷 TR"): st.session_state.language = "tr"; st.rerun()

    st.write("") # Küçük boşluk
    
    col_left, col_right = st.columns([1, 1.2], gap="large")
    
    with col_left:
        # Sol Profil Kartı
        left_container = st.container()
        left_container.markdown('<span id="login-form-marker"></span>', unsafe_allow_html=True)
        
        if os.path.exists("assets/profil.png"):
            # Resim boyutu kompakt görünüm için küçültüldü (170px)
            left_container.image("assets/profil.png", width=170)
            left_container.markdown('<style>img {border-radius: 50%; display: block; margin: 0 auto;}</style>', unsafe_allow_html=True)
        
        left_container.markdown(f"# {t('profile_title')}")
        left_container.markdown(t('profile_desc'))
        
        left_container.markdown("---")
        left_container.write("")
        # AI Disclaimer (Sol kartın en altı)
        left_container.caption(t('ai_disclaimer'))

    with col_right:
        # Sağ Form Kartı
        form_container = st.container()
        form_container.markdown('<span id="login-form-marker"></span>', unsafe_allow_html=True)
        
        form_container.markdown(f"### {t('welcome_title')}")
        form_container.markdown(t('welcome_subtitle'))
        
        name = form_container.text_input(t('input_name'))
        company = form_container.text_input(t('input_company'))
        email = form_container.text_input(t('input_email'))
        
        form_container.markdown("---")
        
        c1, c2 = form_container.columns([1.5, 1])
        with c1:
            if form_container.button(t('btn_read_kvkk')): open_kvkk_modal()
        with c2:
            if st.session_state.kvkk_approved: form_container.success(t('kvkk_status_ok'))
            else: form_container.caption(t('kvkk_status_wait'))
        
        consent = form_container.checkbox(t('chk_consent'), value=st.session_state.kvkk_approved, disabled=not st.session_state.kvkk_approved)
        form_container.write("")
        
        if form_container.button(t('btn_start'), type="primary", use_container_width=True):
            if not consent: st.error(t('err_kvkk'))
            else:
                user_info = {
                    "name": name.strip() or t('user_anon'),
                    "company": company.strip() or t('user_unknown_company'),
                    "email": email.strip() or t('user_unknown_company')
                }
                st.session_state.user_info = user_info
                st.session_state.last_interaction = time.time()
                try: send_email(f"🔔 Login ({st.session_state.language}): {user_info['name']}", str(user_info))
                except: pass
                st.rerun()
    st.stop()

# ==========================================
# 💬 SOHBET EKRANI
# ==========================================
if st.session_state.user_info:
    st.session_state.last_interaction = time.time()

    with st.sidebar:
        if os.path.exists("assets/profil.png"): st.image("assets/profil.png", width=120)
        st.info(f"👤 **{st.session_state.user_info['name']}**")
        st.caption(f"🏢 {st.session_state.user_info['company']}")
        
        st.divider()
        
        # --- SOSYAL MEDYA BUTONLARI (LOGOLU) ---
        linkedin_url = "https://www.linkedin.com/in/keremkundak/"
        github_url = "https://github.com/keremkundak"
        
        st.markdown(f"""
        <style>
            .social-btn-container {{ display: flex; gap: 10px; justify-content: center; width: 100%; }}
            .social-btn {{
                flex: 1; padding: 10px; border-radius: 12px; text-align: center; text-decoration: none !important;
                display: flex; align-items: center; justify-content: center; gap: 8px;
                font-weight: 600; color: white !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s;
            }}
            .social-btn:hover {{ transform: translateY(-2px); opacity: 0.9; }}
            .linkedin-btn {{ background-color: #0077b5; }}
            .github-btn {{ background-color: #24292e; }}
            .social-icon {{ width: 20px; height: 20px; filter: brightness(0) invert(1); }}
        </style>
        <div class="social-btn-container">
            <a href="{linkedin_url}" target="_blank" class="social-btn linkedin-btn">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class="social-icon"> <span>LinkedIn</span>
            </a>
            <a href="{github_url}" target="_blank" class="social-btn github-btn">
                <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" class="social-icon"> <span>GitHub</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        if st.button(t('btn_exit'), type="primary"):
            if len(st.session_state.chat_history) > 0:
                with st.spinner("..."):
                    transcript = create_transcript("User Exit", st.session_state.user_info, st.session_state.chat_history, st.session_state.language)
                    send_email(f"{t('mail_subject_transcript')} - {st.session_state.user_info['name']}", transcript)
            st.session_state.chat_history = []
            st.session_state.user_info = None
            st.session_state.kvkk_approved = False
            st.rerun()

    st.title(f"🤖 {t('profile_title')}")

    # Geçmişi Göster
    for msg in st.session_state.chat_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(msg.content)

    # --- DISCLAIMER & ÖRNEK SORULAR ---
    st.write("") 
    
    # Disclaimer (Ortalanmış ve soluk renkli)
    st.markdown(f"""
    <div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-bottom: 5px;">
        {t('ai_disclaimer')}
    </div>
    """, unsafe_allow_html=True)

    user_query = None
    # Sadece sohbet boşsa örnek soru butonlarını göster
    if len(st.session_state.chat_history) == 0:
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        if col_ex1.button(t('ex_btn_1'), use_container_width=True): user_query = t('ex_btn_1')
        if col_ex2.button(t('ex_btn_2'), use_container_width=True): user_query = t('ex_btn_2')
        if col_ex3.button(t('ex_btn_3'), use_container_width=True): user_query = t('ex_btn_3')

    # Input Alanı
    chat_input_val = st.chat_input(t('chat_placeholder'))
    if chat_input_val: user_query = chat_input_val

    # Cevap Üretimi
    if user_query:
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        
        # Butonla gelince ekrana manuel bas
        if chat_input_val is None:
             with st.chat_message("user"): st.write(user_query)
        else:
             with st.chat_message("user"): st.write(user_query)
        
        user_name = st.session_state.user_info['name']
        company_name = st.session_state.user_info['company']
        lang_instruction = t('prompt_role')
        
        context_str = f"User: {user_name} from {company_name}."

        system_prompt = f"""
        ROLE: You are Kerem's Digital Twin.
        CONTEXT: {context_str}
        CV DATA: {st.session_state.cv_text}
        
        RULES:
        1. {lang_instruction}
        2. Be professional, friendly and confident.
        3. Do not invent information not in CV.
        4. If user asks in another language, stick to the selected language ({st.session_state.language}).

        Special instructions:
        1. If user asks about salary, answer with "It would be best to discuss salary with Kerem in person."
        2. If user asks about contact information, provide email or LinkedIn.
        """

        messages = [SystemMessage(content=system_prompt)] + st.session_state.chat_history
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        
        with st.chat_message("assistant"):
            try:
                # Streaming Efekti
                stream = llm.stream(messages)
                response_content = st.write_stream(stream)
                st.session_state.chat_history.append(AIMessage(content=response_content))
            except Exception as e:
                st.error("Error generating response.")
        
        # Butona basıldıysa butonları yok etmek için yenile
        if chat_input_val is None:
            st.rerun()