from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "todo.db"

# Initialize database
def init_db():
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                status TEXT,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

# Add new task
@app.route("/add", methods=["POST"])
def add_task():
    data = request.get_json()
    task = data.get("task") if data else None
    if not task or not task.strip():
        return jsonify({"error": "Task cannot be empty"}), 400

    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        conn.commit()
    return jsonify({"message": "Task added"})

# Complete task and move to history
@app.route("/complete/<int:id>", methods=["PUT"])
def complete_task(id):
    conn = get_db_connection()
    row = conn.execute("SELECT task FROM tasks WHERE id=?", (id,)).fetchone()
    if row:
        # Move to history as completed
        conn.execute("INSERT INTO history (task, status) VALUES (?, ?)", (row["task"], "completed"))
        # Delete from tasks
        conn.execute("DELETE FROM tasks WHERE id=?", (id,))
        conn.commit()
    conn.close()
    return jsonify({"message": "Task marked completed and moved to history"})

# Delete task (move to history as pending)
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_task(id):
    conn = get_db_connection()
    row = conn.execute("SELECT task, status FROM tasks WHERE id=?", (id,)).fetchone()
    if row:
        conn.execute("INSERT INTO history (task, status) VALUES (?, ?)", (row["task"], row["status"]))
        conn.execute("DELETE FROM tasks WHERE id=?", (id,))
        conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted and moved to history"})

# Fetch active tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    tasks_list = [{"id": t["id"], "task": t["task"], "status": t["status"]} for t in tasks]
    return jsonify(tasks_list)

# Fetch history
@app.route("/history", methods=["GET"])
def get_history():
    conn = get_db_connection()
    history = conn.execute("SELECT * FROM history ORDER BY deleted_at DESC").fetchall()
    conn.close()
    history_list = [
        {"id": h["id"], "task": h["task"], "status": h["status"], "deleted_at": h["deleted_at"]}
        for h in history
    ]
    return jsonify(history_list)

# Delete history permanently
@app.route("/history/delete/<int:id>", methods=["DELETE"])
def delete_history(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM history WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "History item deleted"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
