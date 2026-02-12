import streamlit as st
import google.generativeai as genai

# --- עיצוב האפליקציה (RTL) ---
st.set_page_config(page_title="הסיפור שלי", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Assistant', sans-serif;
    }
    .stChatMessage { direction: RTL !important; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    </style>
    """, unsafe_allow_html=True)

# --- הגדרת המפתח ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("אנא הגדר מפתח API ב-Secrets.")
    st.stop()

# --- לוגיקה ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

with st.sidebar:
    st.title("הגדרות")
    age = st.number_input("גיל הקורא:", 3, 120, 30)
    genre = st.selectbox("ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    if st.button("מחק הכל"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

st.title("📖 מספר הסיפורים")

# --- הפעלת הסיפור ---
if st.session_state.chat is None:
    if st.button("התחל את ההרפתקה"):
        try:
            # שימוש בשם המודל הפשוט ביותר למניעת 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.session_state.chat = model.start_chat(history=[])
            
            sys_msg = f"אתה מספר סיפורים. כתוב בעברית, גוף שלישי. ג'אנר: {genre}, גיל: {age}. פתח את הסיפור בתיאור מרתק וסיים בשאלה לקורא."
            response = st.session_state.chat.send_message(sys_msg)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

# הצגת ההודעות
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# קלט משתמש
if user_input := st.chat_input("מה הדמות תעשה?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
    except Exception as e:
        st.error(f"שגיאה: {e}")
