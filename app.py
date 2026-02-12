import streamlit as st
import google.generativeai as genai

# הגדרת ה-API (החלף ב-Key שלך)
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# --- ממשק המשתמש (UI) ---
st.set_page_config(page_title="מספר הסיפורים האינטראקטיבי", page_icon="📖")
st.title("📖 בנה את הסיפור שלך")

# תפריט צד להגדרות
with st.sidebar:
    st.header("הגדרות סיפור")
    age = st.number_input("גיל הקורא:", min_value=3, max_value=120, value=30)
    genre = st.selectbox("בחר ג'אנר:", ["מתח", "רומנטיקה", "קומדיה", "ספר ילדים"])
    
# לוגיקת הפרומפט המשתנה
def get_system_instruction(age, genre):
    base = "אתה מנוע סיפור אינטראקטיבי בעברית. כתוב בגוף שלישי."
    
    if age < 8:
        return f"{base} סגנון: ספר ילדים לגילאי {age}. שפה פשוטה, קסומה ומעודדת. אין מוות או סכנה קיצונית. התמקד בערכים והרפתקאות מתוקות."
    
    styles = {
        "מתח": "סגנון בוגר, אפל, מותח ומציאותי. החלטות שגויות עלולות להוביל לכישלון או מוות.",
        "רומנטיקה": "התמקד ברגשות, מתח בין-אישי, תיאורי אווירה ודיאלוגים רגישים.",
        "קומדיה": "סגנון קליל, מצחיק, משתמש בהומור מצבים ובשנינות.",
        "ספר ילדים": "שפה עשירה אך מותאמת לילדים, דגש על הרפתקאות ודמיון."
    }
    
    return f"{base} {styles.get(genre, '')} גיל היעד הוא {age}. אם המשתמש מבקש 'תזכורת', פרט את מצבו והחפצים שלו."

# --- ניהול הזיכרון (Chat Session) ---
if "chat" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=get_system_instruction(age, genre)
    )
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.story_started = False

# התחלת הסיפור
if not st.session_state.story_started:
    if st.button("התחל את המסע"):
        response = st.session_state.chat.send_message(f"התחל סיפור חדש בג'אנר {genre} עבור קורא בגיל {age}.")
        st.session_state.story_started = True
        st.rerun()

# הצגת היסטוריית הסיפור
for message in st.session_state.chat.history:
    role = "📖" if message.role == "model" else "👤"
    with st.chat_message(message.role, avatar=role):
        st.markdown(message.parts[0].text)

# קלט מהמשתמש
if user_input := st.chat_input("מה הדמות עושה?"):
    response = st.session_state.chat.send_message(user_input)
    st.rerun()