import streamlit as st
import google.generativeai as genai

# --- הגדרות בסיסיות ועיצוב (RTL) ---
st.set_page_config(page_title="הספר האינטראקטיבי שלי", page_icon="📖", layout="centered")

# הזרקת CSS כדי שהטקסט ייראה טוב בעברית ויהיה מיושר לימין
st.markdown("""
    <style>
    .stApp {
        direction: RTL;
        text-align: right;
    }
    div[data-testid="stChatMessageContent"] {
        text-align: right;
        direction: RTL;
    }
    </style>
    """, unsafe_allow_name=True)

# --- חיבור ל-API בצורה בטוחה ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("שגיאה: מפתח ה-API לא נמצא ב-Secrets של Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- לוגיקת הפרומפט (המוח) ---
def get_system_instruction(age, genre):
    base = "אתה מנוע סיפור אינטראקטיבי בעברית. כתוב בגוף שלישי בסגנון ספרותי עשיר."
    if age < 8:
        return f"{base} סגנון: ספר ילדים לגילאי {age}. שפה פשוטה וקסומה. ללא אלימות. התמקד בהרפתקה."
    
    styles = {
        "מתח": "אווירה אפלה, מותחת ומציאותית. סכנה מוחשית וכישלון אפשרי.",
        "רומנטיקה": "דגש על רגשות, מתח בין-אישי ותיאורי אווירה.",
        "קומדיה": "סגנון קליל, הומור מצבים ושנינות.",
        "ספר ילדים": "שפה עשירה ומלאת דמיון המותאמת לילדים."
    }
    return f"{base} סגנון: {styles.get(genre, 'פרוזה')}. גיל היעד: {age}."

# --- ניהול הזיכרון (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# --- תפריט צד להגדרות ---
with st.sidebar:
    st.header("⚙️ הגדרות הסיפור")
    user_age = st.number_input("גיל הקורא:", min_value=3, max_value=120, value=30)
    user_genre = st.selectbox("בחר ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    
    if st.button("🔄 התחל סיפור חדש"):
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.rerun()

# --- תחילת המשחק ---
if not st.session_state.chat_started:
    st.info("ברוכים הבאים! הגדירו גיל וג'אנר בתפריט הצד ולחצו על הכפתור למטה כדי להתחיל.")
    if st.button("🚀 התחל את המסע"):
        # אתחול המודל
        instruction = get_system_instruction(user_age, user_genre)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)
        st.session_state.chat = model.start_chat(history=[])
        
        # הודעה ראשונה
        first_prompt = f"התחל סיפור חדש בג'אנר {user_genre} עבור קורא בגיל {user_age}."
        response = st.session_state.chat.send_message(first_prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.session_state.chat_started = True
        st.rerun()

# --- הצגת היסטוריית ההודעות (עיצוב צ'אט) ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- קלט מהמשתמש ---
if user_input := st.chat_input("מה הדמות עושה?"):
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # שליחה ל-AI וקבלת תשובה
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.write(response.text)
    except Exception as e:
        st.error(f"אירעה שגיאה בתקשורת: {e}")