import streamlit as st
import google.generativeai as genai

# --- עיצוב "סטודיו" משופר ---
st.set_page_config(page_title="מספר הסיפורים", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Assistant', sans-serif;
        background-color: #ffffff;
    }
    
    /* בועות צ'אט בסגנון מודרני */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        direction: RTL !important;
    }
    
    /* יישור טקסט בתוך ההודעות */
    div[data-testid="stChatMessageContent"] {
        text-align: right;
        direction: RTL;
    }

    /* כותרת מעוצבת */
    h1 {
        color: #1a73e8;
        font-weight: 600;
        border-bottom: 2px solid #e8eaed;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור למנוע ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("אנא הגדר את מפתח ה-API ב-Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_system_instruction(age, genre):
    return f"אתה מספר סיפורים מקצועי. כתוב בעברית עשירה, גוף שלישי. ג'אנר: {genre}, גיל: {age}. סיים כל קטע בדילמה או שתי אפשרויות."

# --- ניהול הזיכרון ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# --- ממשק צד ---
with st.sidebar:
    st.title("הגדרות ספר")
    age = st.number_input("גיל הקורא:", 3, 120, 30)
    genre = st.selectbox("ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    if st.button("🗑️ נקה סיפור"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

st.title("📝 הספר האינטראקטיבי שלי")

# --- הפעלת המנוע ---
if st.session_state.chat is None:
    if st.button("התחל לקרוא עכשיו"):
        try:
            # שימוש בנתיב המלא של המודל כדי למנוע 404
            model = genai.GenerativeModel(
                model_name='models/gemini-1.5-flash',
                system_instruction=get_system_instruction(age, genre)
            )
            st.session_state.chat = model.start_chat(history=[])
            res = st.session_state.chat.send_message(f"פתח בסיפור {genre} מרתק לגיל {age}.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

# הצגת הצ'אט
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# קלט משתמש
if user_input := st.chat_input("מה לעשות?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"שגיאה: {e}")
