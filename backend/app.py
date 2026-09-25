from flask import Flask, request, jsonify, send_from_directory, session, redirect
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "quizmaster-demo-secret"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(BASE_DIR, "pages")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student'
    );

    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        duration INTEGER NOT NULL DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        percentage REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );
    """)

    admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@quizmaster.com",)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            ("QuizMaster Admin", "admin@quizmaster.com", generate_password_hash("admin123"), "admin")
        )

    quiz_count = conn.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    if quiz_count == 0:
        cur = conn.execute(
            "INSERT INTO quizzes(title,description,duration) VALUES(?,?,?)",
            ("Python Basics", "Test your Python fundamentals.", 5)
        )
        quiz_id = cur.lastrowid
        questions = [
            (quiz_id, "Which of the following is used to print output in Python?", "print()", "display()", "output()", "show()", "A"),
            (quiz_id, "Which symbol is used for comments in Python?", "//", "#", "/* */", "<!-- -->", "B"),
            (quiz_id, "Which data type is used to store True or False?", "String", "Integer", "Boolean", "Float", "C"),
            (quiz_id, "Which keyword is used to define a function in Python?", "function", "func", "define", "def", "D"),
            (quiz_id, "Which of these is a Python list?", "[1, 2, 3]", "{1, 2, 3}", "(1, 2, 3)", "<1, 2, 3>", "A")
        ]
        conn.executemany(
            "INSERT INTO questions(quiz_id,question,option_a,option_b,option_c,option_d,answer) VALUES(?,?,?,?,?,?,?)",
            questions
        )
    conn.commit()
    conn.close()


# ---------- page routes ----------
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/login")
def login_page():
    return send_from_directory(PAGES_DIR, "login.html")

@app.route("/register")
def register_page():
    return send_from_directory(PAGES_DIR, "register.html")

@app.route("/student-dashboard")
def student_dashboard_page():
    return send_from_directory(PAGES_DIR, "student-dashboard.html")

@app.route("/quiz")
def quiz_page():
    return send_from_directory(PAGES_DIR, "quiz.html")

@app.route("/result")
def result_page():
    return send_from_directory(PAGES_DIR, "result.html")

@app.route("/admin-dashboard")
def admin_dashboard_page():
    return send_from_directory(PAGES_DIR, "admin-dashboard.html")

@app.route("/create-quiz")
def create_quiz_page():
    return send_from_directory(PAGES_DIR, "create-quiz.html")

@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")

@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")

# Optional .html compatibility for old links
@app.route("/<page>.html")
def old_html_route(page):
    allowed = {
        "login":"login.html", "register":"register.html", "student-dashboard":"student-dashboard.html",
        "quiz":"quiz.html", "result":"result.html", "admin-dashboard":"admin-dashboard.html", "create-quiz":"create-quiz.html"
    }
    if page in allowed:
        return send_from_directory(PAGES_DIR, allowed[page])
    return "Page not found", 404


# ---------- auth ----------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not name or not email or not password:
        return jsonify(error="Please fill all fields."), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)", (name,email,generate_password_hash(password),"student"))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify(error="Email already registered."), 409
    conn.close()
    return jsonify(success=True, message="Registration successful")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password"], password):
        return jsonify(success=False, error="Invalid email or password."), 401
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return jsonify(success=True, role=user["role"], name=user["name"])

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify(success=True)

@app.route("/api/me")
def api_me():
    if not session.get("user_id"):
        return jsonify(logged_in=False)
    return jsonify(logged_in=True, name=session["name"], role=session["role"], user_id=session["user_id"])

# ---------- quizzes ----------
@app.route("/api/quizzes")
def api_quizzes():
    conn = get_db()
    quizzes = conn.execute("SELECT id,title,description,duration FROM quizzes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(q) for q in quizzes])

@app.route("/api/quizzes/<int:quiz_id>")
def api_quiz(quiz_id):
    conn = get_db()
    quiz = conn.execute("SELECT id,title,description,duration FROM quizzes WHERE id=?", (quiz_id,)).fetchone()
    questions = conn.execute("SELECT id,question,option_a,option_b,option_c,option_d,answer FROM questions WHERE quiz_id=? ORDER BY id", (quiz_id,)).fetchall()
    conn.close()
    if not quiz:
        return jsonify(error="Quiz not found"), 404
    return jsonify(quiz=dict(quiz), questions=[dict(q) for q in questions])

@app.route("/api/quizzes", methods=["POST"])
def api_create_quiz():
    if session.get("role") != "admin":
        return jsonify(error="Admin access required."), 403
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    try:
        duration = max(1, int(data.get("duration", 5)))
    except (ValueError, TypeError):
        duration = 5
    questions = data.get("questions") or []
    if not title or not questions:
        return jsonify(error="Quiz title and at least one question are required."), 400
    conn = get_db()
    cur = conn.execute("INSERT INTO quizzes(title,description,duration) VALUES(?,?,?)", (title,description,duration))
    quiz_id = cur.lastrowid
    for q in questions:
        conn.execute("INSERT INTO questions(quiz_id,question,option_a,option_b,option_c,option_d,answer) VALUES(?,?,?,?,?,?,?)", (
            quiz_id, q.get("question",""), q.get("option_a",""), q.get("option_b",""), q.get("option_c",""), q.get("option_d",""), q.get("answer","A")
        ))
    conn.commit(); conn.close()
    return jsonify(success=True, id=quiz_id)

# ---------- results ----------
@app.route("/api/results", methods=["POST"])
def save_result():
    if not session.get("user_id"):
        return jsonify(error="Please login first."), 401
    data = request.get_json(silent=True) or {}
    try:
        quiz_id = int(data.get("quiz_id")); score = int(data.get("score")); total = int(data.get("total"))
    except (ValueError, TypeError):
        return jsonify(error="Invalid result data."), 400
    percentage = round((score / total) * 100, 2) if total else 0
    conn = get_db()
    conn.execute("INSERT INTO results(user_id,quiz_id,score,total,percentage) VALUES(?,?,?,?,?)", (session["user_id"],quiz_id,score,total,percentage))
    conn.commit(); conn.close()
    return jsonify(success=True, percentage=percentage)

@app.route("/api/results")
def get_results():
    if not session.get("user_id"):
        return jsonify(error="Please login first."), 401
    conn = get_db()
    if session.get("role") == "admin":
        rows = conn.execute("""SELECT r.id,r.score,r.total,r.percentage,r.created_at,u.name,q.title FROM results r JOIN users u ON u.id=r.user_id JOIN quizzes q ON q.id=r.quiz_id ORDER BY r.id DESC""").fetchall()
    else:
        rows = conn.execute("""SELECT r.id,r.score,r.total,r.percentage,r.created_at,q.title FROM results r JOIN quizzes q ON q.id=r.quiz_id WHERE r.user_id=? ORDER BY r.id DESC""", (session["user_id"],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
