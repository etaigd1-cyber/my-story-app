import streamlit as st
import google.generativeai as genai

# --- הגדרות בסיסיות ועיצוב (RTL) ---
st.set_page_config(page_title="הספר האינטראקטיבי שלי", page_icon="📖", layout="centered")

# הזרקת CSS כדי שהטקסט ייראה טוב בעברית ויהיה מיושר לימין
# שים לב: כאן תיקנתי ל-unsafe_allow_html=True
st.markdown("""
    <style>
    .stApp {
        direction: RTL;
        text-align: right;
    }
    div[data-testid="stChatMessageContent"] {
        text-align: right;
        direction: RTL;
        font-size: 1.1rem;
    }
    /* התאמה לתיבת הקלט */
    input {
        direction: RTL;
    }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור ל-API בצורה בטוחה ---
# וודא שהגדרת ב-Secrets את השם GOOGLE_API_KEY
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("שגיאה: מפתח ה-API לא נמצא ב-Secrets של Streamlit. אנא הגדר אותו ב-Settings.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- לוגיקת הפרומפט (המוח) ---
def get_system_instruction(age, genre):
    base = "אתה מנוע סיפור אינטראקטיבי בעברית. כתוב בגוף שלישי בסגנון ספרותי עשיר."
    
    if age < 8:
        style_desc = f"סגנון: ספר ילדים לגילאי {age}. שפה פשוטה, קסומה ומנוקדת חלקית. ללא אלימות או פחד. התמקד בהרפתקה חיובית."
    else:
        styles = {
            "מתח": "אווירה אפלה, מותחת ומציאותית. סכנה מוחשית וכישלון אפשרי (כולל סוף טרגי).",
            "רומנטיקה": "התמקד ברגשות, מתח בין-אישי, תיאורי אווירה ודיאלוגים.",
            "קומדיה": "סגנון קליל, הומור מצבים, אירוניה ושנינות.",
            "ספר ילדים": "שפה עשירה ומלאת דמיון המותאמת לילדים בוגרים."
        }
        style_desc = f"סגנון: {styles.get(genre, 'פרוזה')}. גיל היעד: {age}."
    
    return f"{base} {style_desc}. בסוף כל פסקה, הוסף תיאור תמונה קצר באנגלית בסוגריים מרובעים."

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
    
    st.divider()
    if st.button("🔄 התחל סיפור חדש מחדש"):
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.rerun()

# --- תחילת המשחק ---
if not st.session_state.chat_started:
    st.info("שלום איתי! הגדר גיל וג'אנר בתפריט הצד ולחץ על הכפתור כדי להתחיל את הספר שלך.")
    if st.button("🚀 התחל את המסע"):
        try:
            # אתחול המודל עם הוראות מערכת
            instruction = get_system_instruction(user_age, user_genre)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)
            st.session_state.chat = model.start_chat(history=[])
            
            # הודעה ראשונה שיוצרת את תחילת הסיפור
            first_prompt = f"התחל סיפור חדש ומסקרן בג'אנר {user_genre} עבור קורא בגיל {user_age}. הצג את הגיבור ואת הדילמה הראשונה."
            response = st.session_state.chat.send_message(first_prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.session_state.chat_started = True
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה באתחול הסיפור: {e}")

# --- הצגת היסטוריית ההודעות ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- קלט מהמשתמש ---
if user_input := st.chat_input("מה הדמות תעשה עכשיו?"):
    # הוספת הודעת המשתמש למסך
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # שליחה ל-AI וקבלת המשך
    try:
        response = st.session_state.chat.send_message(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"אירעה שגיאה: {e}")