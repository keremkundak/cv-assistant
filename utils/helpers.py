import os
import smtplib
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from cryptography.fernet import Fernet
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage
import streamlit as st

def load_css(file_name):
    """CSS dosyasını okur ve sayfaya inject eder"""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def send_email(subject, body):
    try:
        if "EMAIL_ADDRESS" not in os.environ: return False
        
        sender_email = os.environ["EMAIL_ADDRESS"]
        sender_password = os.environ["EMAIL_PASSWORD"]
        receiver_email = os.environ["TARGET_EMAIL"]

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except: return False

def create_transcript(reason, user_info, chat_history, language):
    if not user_info: return None
    transcript = f"Reason: {reason}\nLanguage: {language}\n"
    transcript += f"Visitor: {user_info['name']}\nEmail: {user_info['email']}\n\n"
    for msg in chat_history:
        role = "Visitor" if isinstance(msg, HumanMessage) else "Kerem AI"
        transcript += f"{role}: {msg.content}\n"
    return transcript

@st.cache_data
def load_cv_text():
    # Şifreli dosya assets klasöründe
    encrypted_filename = "assets/cv.locked"
    
    if not os.path.exists(encrypted_filename):
        st.error(f"⚠️ Hata: {encrypted_filename} bulunamadı!")
        return None
    if "CV_ENCRYPTION_KEY" not in os.environ:
        st.error("⚠️ Hata: Encryption Key eksik!")
        return None

    try:
        with open(encrypted_filename, "rb") as f:
            encrypted_data = f.read()
            
        key = os.environ["CV_ENCRYPTION_KEY"]
        cipher = Fernet(key.encode())
        decrypted_data = cipher.decrypt(encrypted_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(decrypted_data)
            tmp_pdf_path = tmp_pdf.name
            
        loader = PyPDFLoader(tmp_pdf_path)
        docs = loader.load()
        full_text = "\n\n".join([page.page_content for page in docs])
        
        os.remove(tmp_pdf_path)
        return full_text
    except Exception as e:
        st.error(f"CV Yükleme Hatası: {e}")
        return None