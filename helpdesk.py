import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "data", "college_data.json")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


# ============================================================
# 📂 LOAD DATA
# ============================================================

def load_data():

    folder = os.path.dirname(DATA_FILE)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(DATA_FILE):

        default = {
            "notices": [],
            "timetable": [],
            "announcements": []
        }

        with open(DATA_FILE, "w") as f:
            json.dump(default, f, indent=4)

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    except:

        data = {
            "notices": [],
            "timetable": [],
            "announcements": []
        }

    # ✅ remove expired automatically
    data = remove_expired(data)

    # ✅ sort pinned notices first
    data = sort_pinned(data)

    save_data(data)

    return data


# ============================================================
# ⭐ SORT PINNED ITEMS
# ============================================================

def sort_pinned(data):

    def sorter(items):

        return sorted(
            items,
            key=lambda x: (
                not x.get("pinned", False),
                x.get("created_at", "")
            ),
            reverse=False
        )

    data["notices"] = sorter(data["notices"])
    data["timetable"] = sorter(data["timetable"])
    data["announcements"] = sorter(data["announcements"])

    return data


# ============================================================
# 🧹 REMOVE EXPIRED ITEMS
# ============================================================

def remove_expired(data):

    def valid_items(items):

        filtered = []

        for item in items:

            try:
                expiry = datetime.fromisoformat(item["expiry_time"])

                if datetime.now() < expiry:
                    filtered.append(item)

            except:
                continue

        return filtered

    data["notices"] = valid_items(data["notices"])
    data["timetable"] = valid_items(data["timetable"])
    data["announcements"] = valid_items(data["announcements"])

    return data


# ============================================================
# 💾 SAVE DATA
# ============================================================

def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# ⏱ CREATE ITEM
# ============================================================

def create_item(
    text,
    value,
    unit,
    priority="Low",
    category="General",
    pinned=False
):

    if unit == "Minutes":
        delta = timedelta(minutes=value)

    elif unit == "Hours":
        delta = timedelta(hours=value)

    elif unit == "Days":
        delta = timedelta(days=value)

    else:
        delta = timedelta(hours=1)

    return {
        "text": text,
        "created_at": datetime.now().isoformat(),
        "expiry_time": (datetime.now() + delta).isoformat(),
        "priority": priority,
        "category": category,
        "pinned": pinned
    }


# ============================================================
# 📢 ADD NOTICE
# ============================================================

def add_notice(
    text,
    value,
    unit,
    priority="Low",
    category="General",
    pinned=False
):

    if not text.strip():
        return "❌ Empty notice"

    data = load_data()

    item = create_item(
        text,
        value,
        unit,
        priority,
        category,
        pinned
    )

    data["notices"].append(item)

    save_data(data)

    return "✅ Notice added successfully"


# ============================================================
# 📅 ADD TIMETABLE
# ============================================================

def add_timetable(
    text,
    value,
    unit,
    priority="Medium",
    category="Timetable",
    pinned=False
):

    if not text.strip():
        return "❌ Empty timetable"

    data = load_data()

    item = create_item(
        text,
        value,
        unit,
        priority,
        category,
        pinned
    )

    data["timetable"].append(item)

    save_data(data)

    return "✅ Timetable added successfully"


# ============================================================
# 📣 ADD ANNOUNCEMENT
# ============================================================

def add_announcement(
    text,
    value,
    unit,
    priority="Medium",
    category="Announcement",
    pinned=False
):

    if not text.strip():
        return "❌ Empty announcement"

    data = load_data()

    item = create_item(
        text,
        value,
        unit,
        priority,
        category,
        pinned
    )

    data["announcements"].append(item)

    save_data(data)

    return "✅ Announcement added successfully"


# ============================================================
# 📊 GET DATA
# ============================================================

def get_data():
    return load_data()


# ============================================================
# 📌 TOGGLE PIN
# ============================================================

def toggle_pin(section, index):

    data = load_data()

    try:

        current = data[section][index].get("pinned", False)

        data[section][index]["pinned"] = not current

        save_data(data)

        return "✅ Pin updated"

    except:
        return "❌ Invalid item"


# ============================================================
# 🗑 DELETE ITEM
# ============================================================

def delete_item(section, index):

    data = load_data()

    try:

        data[section].pop(index)

        save_data(data)

        return "✅ Item deleted"

    except:
        return "❌ Delete failed"


# ============================================================
# 🧠 CONTEXT FOR AI
# ============================================================

def get_context():

    data = load_data()

    def format_items(items):

        formatted = []

        for item in items:

            pinned = "Yes" if item.get("pinned") else "No"

            formatted.append(
                f"""
Text: {item.get('text')}
Priority: {item.get('priority')}
Category: {item.get('category')}
Pinned: {pinned}
"""
            )

        return "\n".join(formatted)

    return f"""

NOTICES:
{format_items(data['notices'])}

TIMETABLE:
{format_items(data['timetable'])}

ANNOUNCEMENTS:
{format_items(data['announcements'])}

"""


# ============================================================
# 🤖 AI HELPDESK
# ============================================================

def ask_helpdesk(question):

    context = get_context()

    prompt = f"""
You are a college helpdesk assistant.

STRICT RULES:
- Answer ONLY from provided data
- Do NOT guess
- If information is unavailable say:
  "No official update available."

COLLEGE DATA:
{context}

QUESTION:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
# ============================================================
# ❓ STUDENT QUERY SYSTEM (NEW FEATURE)
# ============================================================

QA_FILE = os.path.join(BASE_DIR, "..", "data", "student_queries.json")


def load_queries():

    folder = os.path.dirname(QA_FILE)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(QA_FILE):
        with open(QA_FILE, "w") as f:
            json.dump([], f, indent=4)

    try:
        with open(QA_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_queries(data):

    with open(QA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_student_question(student_name, question):

    if not question.strip():
        return "❌ Empty question"

    data = load_queries()

    data.append({
        "id": len(data) + 1,
        "student_name": student_name,
        "question": question,
        "reply": "",
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    })

    save_queries(data)

    return "✅ Question submitted successfully"


def reply_to_question(q_id, reply_text):

    data = load_queries()

    for item in data:
        if item["id"] == q_id:
            item["reply"] = reply_text
            item["status"] = "Answered"
            save_queries(data)
            return "✅ Reply sent"

    return "❌ Question not found"


def get_all_questions():

    return load_queries()