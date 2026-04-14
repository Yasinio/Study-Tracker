from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from datetime import date
from urllib.parse import quote

app = FastAPI()

DB_NAME = "tasks.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            deadline TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


init_db()


def get_all_tasks():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def get_task_by_id(task_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    today = date.today().isoformat()
    tasks = get_all_tasks()

    qr_target = str(request.base_url).rstrip("/")
    qr_code_url = f"https://quickchart.io/qr?text={quote(qr_target)}&size=220"

    html_content = f"""
    <html>
        <head>
            <title>Tasky</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(to right, #e3f2fd, #fce4ec);
                    margin: 0;
                    padding: 0;
                }}

                .container {{
                    max-width: 950px;
                    margin: 40px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                }}

                h1 {{
                    text-align: center;
                    color: #1565c0;
                    margin-bottom: 10px;
                }}

                p {{
                    text-align: center;
                    color: #555;
                    margin-bottom: 30px;
                }}

                .task-form {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    justify-content: center;
                    margin-bottom: 30px;
                }}

                input, select, button {{
                    padding: 10px;
                    border-radius: 10px;
                    border: 1px solid #ccc;
                    font-size: 14px;
                }}

                input[type="text"] {{
                    width: 220px;
                }}

                button {{
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                }}

                .add-btn {{
                    background-color: #1976d2;
                    color: white;
                }}

                .complete-btn {{
                    background-color: #2e7d32;
                    color: white;
                    margin-right: 8px;
                }}

                .delete-btn {{
                    background-color: #d32f2f;
                    color: white;
                    margin-right: 8px;
                }}

                .edit-btn {{
                    background-color: #f9a825;
                    color: white;
                    margin-right: 8px;
                    text-decoration: none;
                    padding: 10px 14px;
                    border-radius: 10px;
                    font-weight: bold;
                }}

                .task-card {{
                    list-style: none;
                    background: #f9f9f9;
                    border-left: 8px solid #90caf9;
                    margin-bottom: 15px;
                    padding: 15px;
                    border-radius: 12px;
                }}

                .completed {{
                    opacity: 0.6;
                    text-decoration: line-through;
                    background: #e8f5e9;
                }}

                .high {{ border-left-color: #e53935; }}
                .medium {{ border-left-color: #fb8c00; }}
                .low {{ border-left-color: #43a047; }}

                .overdue {{ background: #ffebee; }}

                .task-title {{
                    font-size: 18px;
                    font-weight: bold;
                }}

                .badge {{
                    padding: 4px 10px;
                    border-radius: 20px;
                    color: white;
                    font-size: 12px;
                    margin-right: 5px;
                }}

                .badge-high {{ background: #e53935; }}
                .badge-medium {{ background: #fb8c00; }}
                .badge-low {{ background: #43a047; }}
                .badge-type {{ background: #5e35b1; }}

                .warning {{
                    color: red;
                    font-weight: bold;
                }}

                .footer {{
                    margin-top: 40px;
                    text-align: center;
                }}

                .ys-logo {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #1565c0, #7b1fa2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 30px;
                    margin: auto;
                }}

                .qr-box img {{
                    width: 200px;
                    margin-top: 10px;
                }}
            </style>
        </head>

        <body>
            <div class="container">
                <h1>Task Reminder</h1>

                <p>Manage your tasks, deadlines, and stay organised with reminders in one place.</p>

                <form action="/add" method="post" class="task-form">
                    <input type="text" name="task_name" placeholder="Enter task" required>

                    <select name="task_type" required>
                        <option value="Study">Study</option>
                        <option value="Email">Email</option>
                        <option value="Phone Call">Phone Call</option>
                        <option value="Meeting">Meeting</option>
                        <option value="Other">Other</option>
                    </select>

                    <select name="priority" required>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                    </select>

                    <input type="date" name="deadline" required>

                    <button class="add-btn">Add</button>
                </form>

                <h2>Your Tasks</h2>
                <ul>
    """

    for number, task in enumerate(tasks, start=1):
        completed = task["completed"] == 1
        overdue = not completed and task["deadline"] < today

        html_content += f"""
        <li class="task-card {'completed' if completed else ''} {'overdue' if overdue else ''}">
            <div class="task-title">{number}. {task["name"]}</div>

            <div>
                <span class="badge badge-{task["priority"].lower()}">{task["priority"]}</span>
                <span class="badge badge-type">{task["task_type"]}</span>
                Deadline: {task["deadline"]}
            </div>

            {"<div class='warning'>Overdue!</div>" if overdue else ""}

            <div>
                <form action="/complete/{task["id"]}" method="post" style="display:inline;">
                    <button class="complete-btn">Complete</button>
                </form>

                <a href="/edit/{task["id"]}" class="edit-btn">Edit</a>

                <form action="/delete/{task["id"]}" method="post" style="display:inline;">
                    <button class="delete-btn">Delete</button>
                </form>
            </div>
        </li>
        """

    html_content += f"""
                </ul>

                <div class="footer">
                    <div class="ys-logo">Ys</div>
                    <div>Scan to open</div>
                    <div class="qr-box">
                        <img src="{qr_code_url}">
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    return html_content


@app.post("/add")
def add_task(task_name: str = Form(...), task_type: str = Form(...),
             priority: str = Form(...), deadline: str = Form(...)):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (name, task_type, priority, deadline, completed) VALUES (?, ?, ?, ?, 0)",
        (task_name, task_type, priority, deadline)
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)


@app.post("/complete/{task_id}")
def complete(task_id: int):
    conn = get_connection()
    conn.execute("UPDATE tasks SET completed = 1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{task_id}")
def delete(task_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

