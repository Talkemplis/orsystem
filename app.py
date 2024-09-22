import streamlit as st
import pandas as pd
import os

# נתיב לקובצי CSV
CSV_FILE = 'shomer1.csv'
HISTORY_FILE = 'history1.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            data = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            data.columns = data.columns.str.strip()
            return data
        except Exception as e:
            st.error(f"שגיאה בטעינת קובץ: {e}")
            return pd.DataFrame(columns=["שם", "צוות", "מספר משימות"])
    return pd.DataFrame(columns=["שם", "צוות", "מספר משימות"])

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            history = pd.read_csv(HISTORY_FILE, encoding='utf-8-sig')
            history.columns = history.columns.str.strip()
            return history
        except Exception as e:
            st.error(f"שגיאה בטעינת היסטוריה: {e}")
            return pd.DataFrame(columns=["שם משימה", "מקום", "תאריך", "שעת התחלה", "שעת סיום", "מספר תורנים", "תורנים"])
    return pd.DataFrame(columns=["שם משימה", "מקום", "תאריך", "שעת התחלה", "שעת סיום", "מספר תורנים", "תורנים"])

def update_guard_task_count(data, history):
    data["מספר משימות"] = 0
    for _, row in history.iterrows():
        guards = row["תורנים"].split(", ")
        for guard in guards:
            if guard in data["שם"].values:
                data.loc[data["שם"] == guard, "מספר משימות"] += 1
    return data

# אפליקציית Streamlit
st.title("מערכת תורנים מדור אור")

data = load_data()
history = load_history()

# הצגת נתונים לדיוק
st.write("רשימת צוותים:", data)
st.write("היסטוריה:", history)

# הוספת שומרים
st.header("הוספת חייל")
guard_name = st.text_input("שם החייל:")
guard_team = st.text_input("צוות החייל:")
if st.button("הוסף חייל"):
    if guard_name and guard_team:
        new_guard = pd.DataFrame({"שם": [guard_name], "צוות": [guard_team], "מספר משימות": [0]})
        data = pd.concat([data, new_guard], ignore_index=True)
        data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success(f"חייל {guard_name} נוסף בהצלחה!")
    else:
        st.warning("נא להזין שם וצוות.")

# מחיקת שומרים
st.header("מחיקת חייל")
if "שם" in data.columns:
    guard_to_remove = st.selectbox("בחר חייל למחיקה:", data["שם"].tolist())
    if st.button("מחק חייל"):
        data = data[data["שם"] != guard_to_remove]
        data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success(f"חייל {guard_to_remove} נמחק בהצלחה!")
else:
    st.warning("העמודה 'שם' לא קיימת בנתונים.")

# הצגת רשימת שומרים
st.header("רשימת חיילים")
st.write(data)

# הוספת משימות
st.header("הוספת משימה")
task_name = st.text_input("שם המשימה:")
location = st.text_input("מקום המשימה:")
date = st.date_input("תאריך המשימה:")
start_time = st.time_input("שעת התחלה:")
end_time = st.time_input("שעת סיום:")
num_guards = st.number_input("כמות תורנים:", min_value=1)

# בחירת תורן
st.header("בחירת תורן")
available_guards = data["שם"].tolist()
selected_guards = st.multiselect("בחר תורנים:", available_guards)

if st.button("שמור תורנים"):
    if len(selected_guards) <= num_guards:
        history_entry = pd.DataFrame({
            "שם משימה": [task_name],
            "מקום": [location],
            "תאריך": [pd.to_datetime(date)],
            "שעת התחלה": [start_time],
            "שעת סיום": [end_time],
            "מספר תורנים": [num_guards],
            "תורנים": [', '.join(selected_guards)]
        })
        history = pd.concat([history, history_entry], ignore_index=True)
        data = update_guard_task_count(data, history)
        history.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
        data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success(f"משימה {task_name} עם תורנים {', '.join(selected_guards)} נוספה בהצלחה!")
    else:
        st.warning("לא ניתן להקצות יותר תורנים מהנדרש.")

# הצגת היסטוריית משימות
st.header("היסטוריית משימות")
st.write(history)

# מחיקת משימה
st.header("מחיקת משימה")
if "שם משימה" in history.columns:
    task_to_remove = st.selectbox("בחר משימה למחיקה:", history["שם משימה"].tolist())
    if st.button("מחק משימה"):
        history = history[history["שם משימה"] != task_to_remove]
        data = update_guard_task_count(data, history)
        history.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
        data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success(f"משימה {task_to_remove} נמחקה בהצלחה!")
else:
    st.warning("העמודה 'שם משימה' לא קיימת בהיסטוריה.")

# עריכת תורנים במשימה
st.header("עריכת תורנים במשימה")
task_to_edit = st.selectbox("בחר משימה לעריכת תורנים:", history["שם משימה"].tolist())
if task_to_edit:
    current_guards = history[history["שם משימה"] == task_to_edit]["תורנים"].values[0].split(', ')
    new_selected_guards = st.multiselect("בחר תורנים חדשים:", available_guards, default=current_guards)

    if st.button("שמור שינויים"):
        history.loc[history["שם משימה"] == task_to_edit, "תורנים"] = ', '.join(new_selected_guards)
        data = update_guard_task_count(data, history)
        history.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
        data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success(f"תורנים למשימה {task_to_edit} עודכנו בהצלחה!")

# עדכון סופי של מספר המשימות
data = update_guard_task_count(data, history)

# הצגת רשימת תורנים עם מספר משימות
st.header("רשימת תורנים מעודכנת")
st.write(data[["שם", "צוות", "מספר משימות"]])

# שמירה עדכנית
data.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')