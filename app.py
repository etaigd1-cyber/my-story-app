import streamlit as st
import google.generativeai as genai

# --- הגדרות בסיסיות ועיצוב ספרותי ---
st.set_page_config(page_title="הסיפור האינטראקטיבי שלי", page_icon="📖", layout="centered")

# עיצוב CSS מתקדם למראה של ספר ויישור לימין
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Assistant', sans-serif;
        background-color: #fdf6e3; /* צבע נייר ישן */
    }
    
    .stChatMessage {
        direction: RTL !important;
    }
    
    div[data-testid="stChatMessageContent"] p {
        font-size: 1.2rem;
        line-height: 1.6;
        color: #2c3e50;
    }

    /* עיצוב תיבת הקלט */
    .stChatInputContainer {
        direction: RTL;
    }
    
    /* כותרות */
    h1 {
        color: #8b4513;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור ל-API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_system_instruction(age, genre):
    base = "אתה מספר סיפורים מקצועי. כתוב בעברית ספרותית עשירה, גוף שלישי בלבד."
    if age < 8:
        style = f"סגנון: ספר ילדים לגילאי {age}. שפה קסומה, ללא סכנה, דגש על דמיון וחברות."
    else:
        styles = {
            "מתח": "אווירה קרירה, משפטים קצרים, דופק גבוה וסכנה מוחשית.",
            "רומנטיקה": "דגש על רגש, כימיה, תיאורי אווירה ודיאלוגים רגישים.",
            "קומדיה": "טון משעשע, אירוניה ומצבים אבסורדיים.",
            "ספר ילדים": "הרפתקה קלאסית עם שפה עשירה."
        }
        style = f"סגנון: {styles.get(genre, 'פרוזה')}. התאם לגיל {age}."
    
    return f"{base} {style} בסוף כל חלק תן שתי אופציות או בקש מהקורא להקליד פעולה. הוסף [IMAGE_PROMPT: description] בסוף."

# --- ניהול מצב האפליקציה ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# --- תפריט צד ---
with st.sidebar:
    st.title("📚 הגדרות")
    age = st.number_input("גיל:", 3, 120, 30)
    genre = st.selectbox("ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    if st.button("🗑️ מחק סיפור והתחל מחדש"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# --- לוגיקת הסיפור ---
if st.session_state.chat is None:
    st.write("### מוכן להתחיל בהרפתקה?")
    if st.button("📖 התחל לקרוא"):
        try:
            # שימוש בשם מודל מעודכן ורחב יותר
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                system_instruction=get_system_instruction(age, genre)
            )
            st.session_state.chat = model.start_chat(history=[])
            prompt = f"התחל סיפור {genre} לגיל {age}. פתח בסצנה ראשונה מרתקת."
            response = st.session_state.chat.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בחיבור למנוע הסיפור: {e}")

# הצגת הסיפור
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# קלט מהמשתמש
if user_input := st.chat_input("מה הדמות תעשה?"):
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