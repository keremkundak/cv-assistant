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
import json
import uuid
import pytz

def load_css(file_name):
    """Reads CSS file and injects it into the page"""
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

def create_transcript(trigger, user_info, chat_history, language):
    """Creates a formatted transcript of the chat"""
    timestamp = datetime.now(pytz.timezone('Europe/Istanbul')).strftime("%Y-%m-%d %H:%M:%S")
    transcript = f"Chat Transcript - {trigger}\n"
    transcript += f"Date: {timestamp}\n"
    transcript += f"User: {user_info['name']} ({user_info['company']})\n"
    transcript += f"Email: {user_info['email']}\n"
    transcript += "-" * 30 + "\n\n"
    
    for msg in chat_history:
        role = "User" if isinstance(msg, HumanMessage) else "AI"
        transcript += f"{role}: {msg.content}\n"
    return transcript

def save_chat_log(session_id, user_info, chat_history, language):
    """Saves chat history incrementally to a JSON file"""
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        tz = pytz.timezone('Europe/Istanbul')
        current_time = datetime.now(tz).isoformat()
            
        log_data = {
            "session_id": str(session_id),
            "timestamp": current_time,
            "user_info": user_info,
            "language": language,
            "messages": []
        }
        
        for msg in chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            log_data["messages"].append({
                "role": role,
                "content": msg.content,
                "timestamp": current_time # Using current save time for simplicity, or could track msg time
            })
            
        filename = f"logs/{session_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Log Save Error: {e}")
        return False

@st.cache_data
def load_cv_text():
    # Encrypted file is in assets folder
    encrypted_filename = "assets/cv.locked"
    
    if not os.path.exists(encrypted_filename):
        st.error(f"⚠️ Error: {encrypted_filename} not found!")
        return None
    if "CV_ENCRYPTION_KEY" not in os.environ:
        st.error("⚠️ Error: Encryption Key missing!")
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
        st.error(f"CV Loading Error: {e}")
        return None