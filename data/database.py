import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.environ["TURSO_DATABASE_URL"] + "/v2/pipeline"
TURSO_TOKEN = os.environ["TURSO_AUTH_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json",
}


def _execute(sql, args=None):
    stmt = {"sql": sql}
    if args:
        stmt["args"] = [
            _to_turso_value(v) for v in args
        ]
    payload = {
        "requests": [
            {"type": "execute", "stmt": stmt},
            {"type": "close"},
        ]
    }
    r = requests.post(TURSO_URL, json=payload, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    result = data["results"][0]
    if result["type"] == "error":
        raise Exception(result.get("error", {}).get("message", "Unknown error"))
    return result["response"]["result"]


def _to_turso_value(v):
    if v is None:
        return {"type": "null", "value": None}
    if isinstance(v, bool):
        return {"type": "integer", "value": "1" if v else "0"}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": str(v)}
    return {"type": "text", "value": str(v)}


def _from_turso_row(cols, row):
    obj = {}
    for i, col in enumerate(cols):
        name = col["name"]
        val = row[i]
        if val["type"] == "null":
            obj[name] = None
        elif val["type"] == "integer":
            obj[name] = int(val["value"])
        elif val["type"] == "float":
            obj[name] = float(val["value"])
        else:
            obj[name] = val["value"]
    return obj


def init_db():
    tables = [
        """CREATE TABLE IF NOT EXISTS personal (
            id INTEGER PRIMARY KEY DEFAULT 1,
            name TEXT DEFAULT '', title TEXT DEFAULT '',
            email TEXT DEFAULT '', phone TEXT DEFAULT '',
            location TEXT DEFAULT '', bio TEXT DEFAULT '',
            avatar TEXT DEFAULT '', github TEXT DEFAULT '',
            linkedin TEXT DEFAULT '', twitter TEXT DEFAULT '',
            admin_password TEXT DEFAULT 'admin123'
        )""",
        """CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL, position TEXT NOT NULL,
            period TEXT NOT NULL, description TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS skill_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES skill_categories(id)
        )""",
        """CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT NOT NULL,
            tech TEXT NOT NULL DEFAULT '[]',
            url TEXT NOT NULL DEFAULT '', image TEXT NOT NULL DEFAULT ''
        )""",
        """CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution TEXT NOT NULL, degree TEXT NOT NULL,
            period TEXT NOT NULL, description TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, date TEXT NOT NULL,
            summary TEXT NOT NULL, tags TEXT NOT NULL DEFAULT '[]',
            url TEXT NOT NULL DEFAULT ''
        )""",
    ]
    for sql in tables:
        _execute(sql)


# --- Personal ---

def get_personal():
    result = _execute("SELECT * FROM personal WHERE id = 1")
    if not result["rows"]:
        return None
    row = _from_turso_row(result["cols"], result["rows"][0])
    row["social"] = {
        "github": row.pop("github", ""),
        "linkedin": row.pop("linkedin", ""),
        "twitter": row.pop("twitter", ""),
    }
    return row


def save_personal(data):
    existing = get_personal()
    password = existing["admin_password"] if existing else "admin123"
    _execute("DELETE FROM personal WHERE id = 1")
    _execute(
        """INSERT INTO personal (id, name, title, email, phone, location, bio, avatar, github, linkedin, twitter, admin_password)
           VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [data["name"], data["title"], data["email"], data["phone"],
         data["location"], data["bio"], data["avatar"],
         data.get("social", {}).get("github", ""),
         data.get("social", {}).get("linkedin", ""),
         data.get("social", {}).get("twitter", ""),
         password]
    )


# --- Experience ---

def get_experience():
    result = _execute("SELECT * FROM experience ORDER BY id DESC")
    return [_from_turso_row(result["cols"], row) for row in result["rows"]]


def save_experience(items):
    _execute("DELETE FROM experience")
    for item in items:
        _execute(
            "INSERT INTO experience (company, position, period, description) VALUES (?, ?, ?, ?)",
            [item["company"], item["position"], item["period"], item["description"]]
        )


# --- Skills ---

def get_skills():
    cats = _execute("SELECT * FROM skill_categories ORDER BY id")
    result = {}
    for cat in _from_turso_row_list(cats["cols"], cats["rows"]):
        items = _execute("SELECT name FROM skills WHERE category_id = ? ORDER BY id", [cat["id"]])
        result[cat["category"]] = [r["name"] for r in _from_turso_row_list(items["cols"], items["rows"])]
    return result


def save_skills(skills_dict):
    _execute("DELETE FROM skills")
    _execute("DELETE FROM skill_categories")
    for cat_name, skill_list in skills_dict.items():
        insert_result = _execute("INSERT INTO skill_categories (category) VALUES (?)", [cat_name])
        cat_id = insert_result["last_insert_rowid"]
        for skill in skill_list:
            _execute(
                "INSERT INTO skills (category_id, name) VALUES (?, ?)",
                [cat_id, skill]
            )


# --- Projects ---

def get_projects():
    result = _execute("SELECT * FROM projects ORDER BY id DESC")
    projects = []
    for row in _from_turso_row_list(result["cols"], result["rows"]):
        row["tech"] = json.loads(row.get("tech", "[]"))
        projects.append(row)
    return projects


def save_projects(items):
    _execute("DELETE FROM projects")
    for item in items:
        _execute(
            "INSERT INTO projects (title, description, tech, url, image) VALUES (?, ?, ?, ?, ?)",
            [item["title"], item["description"],
             json.dumps(item.get("tech", [])),
             item.get("url", ""), item.get("image", "")]
        )


# --- Education ---

def get_education():
    result = _execute("SELECT * FROM education ORDER BY id DESC")
    return [_from_turso_row(result["cols"], row) for row in result["rows"]]


def save_education(items):
    _execute("DELETE FROM education")
    for item in items:
        _execute(
            "INSERT INTO education (institution, degree, period, description) VALUES (?, ?, ?, ?)",
            [item["institution"], item["degree"], item["period"], item["description"]]
        )


# --- Blog ---

def get_blog_posts():
    result = _execute("SELECT * FROM blog_posts ORDER BY id DESC")
    posts = []
    for row in _from_turso_row_list(result["cols"], result["rows"]):
        row["tags"] = json.loads(row.get("tags", "[]"))
        posts.append(row)
    return posts


def save_blog_posts(items):
    _execute("DELETE FROM blog_posts")
    for item in items:
        _execute(
            "INSERT INTO blog_posts (title, date, summary, tags, url) VALUES (?, ?, ?, ?, ?)",
            [item["title"], item["date"], item["summary"],
             json.dumps(item.get("tags", [])), item.get("url", "")]
        )


# --- Auth ---

def check_password(password):
    result = _execute("SELECT admin_password FROM personal WHERE id = 1")
    if result["rows"]:
        stored = result["rows"][0][0]["value"]
        return stored == password
    return "admin123" == password


def change_password(new_password):
    _execute("UPDATE personal SET admin_password = ? WHERE id = 1", [new_password])


# --- Helpers ---

def _from_turso_row_list(cols, rows):
    return [_from_turso_row(cols, row) for row in rows]
