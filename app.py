import streamlit as st
import google.generativeai as genai

# --- עיצוב "גוגל סטודיו" נקי ויישור לימין ---
st.set_page_config(page_title="הספר האינטראקטיבי שלי", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Assistant', sans-serif;
    }
    
    /* עיצוב בועות הצ'אט שייראה כמו בסטודיו */
    .stChatMessage {
        direction: RTL !important;
        text-align: right;
    }
    
    div[data-testid="stChatMessageContent"] p {
        font-size: 1.1rem;
        line-height: 1.6;
    }

    /* התאמה לנייד */
    .stChatInputContainer {
        direction: RTL;
    }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור מאובטח ל-API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets של Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- לוגיקת המנוע ---
def get_system_instruction(age, genre):
    base = "אתה מספר סיפורים מקצועי. כתוב בעברית ספרותית, גוף שלישי."
    if age < 8:
        style = f"סגנון: ספר ילדים קסום לגיל {age}. שפה פשוטה וחמה, ללא סכנה."
    else:
        styles = {
            "מתח": "אווירה קרירה, מותחת, סכנה מוחשית ודילמות קשות.",
            "רומנטיקה": "דגש על רגשות, כימיה ותיאורי אווירה.",
            "קומדיה": "טון משעשע, מצבים אבסורדיים ושנינות.",
            "ספר ילדים": "הרפתקה מרגשת עם שפה עשירה."
        }
        style = f"סגנון: {styles.get(genre, 'פרוזה')}. התאם לגיל {age}."
    return f"{base} {style} בסוף כל קטע בקש מהקורא להחליט מה הצעד הבא."

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# --- ממשק צד (Sidebar) ---
with st.sidebar:
    st.title("📖 הגדרות הספר")
    user_age = st.number_input("גיל הקורא:", 3, 120, 30)
    user_genre = st.selectbox("ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    if st.button("🔄 התחל סיפור חדש"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

st.title("📝 מספר הסיפורים האינטראקטיבי")

# --- הפעלת המנוע (עם תיקון ל-404) ---
if st.session_state.chat is None:
    if st.button("לחץ כאן כדי להתחיל את הסיפור"):
        try:
            # ניסיון להשתמש בשם המודל הבסיסי ביותר - הכי בטוח למניעת 404
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash', 
                system_instruction=get_system_instruction(user_age, user_genre)
            )
            st.session_state.chat = model.start_chat(history=[])
            # יצירת הפתיחה
            response = st.session_state.chat.send_message(f"פתח בסיפור {user_genre} מרתק שמתאים לגיל {user_age}.")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בחיבור למנוע: {e}")

# הצגת היסטוריית הצ'אט בבועות
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# קלט מהמשתמש
if user_input := st.chat_input("מה הדמות תעשה עכשיו?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"הסיפור נקטע בגלל שגיאה: {e}")
