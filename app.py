import streamlit as st
import google.generativeai as genai

# --- הגדרות עיצוב RTL וספרותי ---
st.set_page_config(page_title="הסיפור שלי", page_icon="📖")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Assistant', sans-serif;
        background-color: #fdf6e3;
    }
    .stChatMessage { direction: RTL !important; }
    div[data-testid="stChatMessageContent"] p { font-size: 1.15rem; line-height: 1.6; color: #2c3e50; }
    .stChatInputContainer { direction: RTL; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור ל-API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("מפתח API חסר ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_system_instruction(age, genre):
    base = "אתה מספר סיפורים מקצועי. כתוב בעברית עשירה, גוף שלישי."
    if age < 8:
        style = f"סגנון: ספר ילדים לגילאי {age}. שפה קסומה ופשוטה."
    else:
        styles = {"מתח": "מתח גבוה.", "רומנטיקה": "רגשות וכימיה.", "קומדיה": "הומור ושנינות.", "ספר ילדים": "הרפתקה."}
        style = f"סגנון: {styles.get(genre, 'פרוזה')}. התאם לגיל {age}."
    return f"{base} {style} בסוף כל חלק בקש מהקורא להחליט מה לעשות."

# --- ניהול הזיכרון ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# --- תפריט צד ---
with st.sidebar:
    st.title("📚 הגדרות")
    age = st.number_input("גיל הקורא:", 3, 120, 30)
    genre = st.selectbox("ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    if st.button("🔄 אתחל סיפור"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# --- לוגיקת הסיפור ---
if st.session_state.chat is None:
    if st.button("🚀 התחל את הסיפור"):
        try:
            # שימוש בשם המודל הכי נפוץ וסטנדרטי
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=get_system_instruction(age, genre)
            )
            st.session_state.chat = model.start_chat(history=[])
            prompt = f"התחל סיפור {genre} לגיל {age}. פתח בסצנה ראשונה."
            response = st.session_state.chat.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            # אם flash לא עובד, נסה pro כגיבוי
            try:
                model = genai.GenerativeModel(model_name='gemini-1.5-pro', system_instruction=get_system_instruction(age, genre))
                st.session_state.chat = model.start_chat(history=[])
                response = st.session_state.chat.send_message(f"התחל סיפור {genre} לגיל {age}.")
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except:
                st.error(f"שגיאה בחיבור למנוע: {e}")

# תצוגה
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("מה לעשות?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.write(response.text)
    except Exception as e:
        st.error(f"שגיאה: {e}")
