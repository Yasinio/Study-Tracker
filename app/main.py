from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
import os
from datetime import date
from urllib.parse import quote

app = FastAPI()

# For Render with a persistent disk, use:
# DB_NAME = "/var/data/tasks.db"
# For local development, use the local file:
DB_NAME = os.getenv("DB_NAME", "tasks.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def get_task_by_id(task_id: int):
    conn = get_connection()
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

                h2 {{
                    color: #333;
                    margin-top: 20px;
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

                .add-btn:hover {{
                    background-color: #125aa0;
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
                    display: inline-block;
                    padding: 10px 14px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}

                .task-card {{
                    list-style: none;
                    background: #f9f9f9;
                    border-left: 8px solid #90caf9;
                    margin-bottom: 15px;
                    padding: 15px;
                    border-radius: 12px;
                    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
                }}

                .completed {{
                    opacity: 0.7;
                    text-decoration: line-through;
                    background: #e8f5e9;
                }}

                .high {{
                    border-left-color: #e53935;
                }}

                .medium {{
                    border-left-color: #fb8c00;
                }}

                .low {{
                    border-left-color: #43a047;
                }}

                .overdue {{
                    background: #ffebee;
                }}

                .task-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #222;
                }}

                .task-info {{
                    margin-top: 8px;
                    color: #555;
                }}

                .badge {{
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                    margin-right: 8px;
                }}

                .badge-high {{
                    background-color: #e53935;
                }}

                .badge-medium {{
                    background-color: #fb8c00;
                }}

                .badge-low {{
                    background-color: #43a047;
                }}

                .badge-type {{
                    background-color: #5e35b1;
                }}

                .warning {{
                    color: #c62828;
                    font-weight: bold;
                    margin-top: 8px;
                }}

                .actions {{
                    margin-top: 12px;
                }}

                .footer {{
                    margin-top: 40px;
                    padding-top: 24px;
                    border-top: 2px solid #eee;
                    text-align: center;
                }}

                .ys-logo {{
                    width: 86px;
                    height: 86px;
                    margin: 0 auto 12px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #1565c0, #7b1fa2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 34px;
                    font-weight: 800;
                    letter-spacing: -2px;
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
                    font-family: Georgia, serif;
                }}

                .footer-text {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 12px;
                }}

                .qr-box {{
                    margin-top: 16px;
                }}

                .qr-box img {{
                    width: 220px;
                    height: 220px;
                    border-radius: 12px;
                    border: 1px solid #ddd;
                    background: white;
                    padding: 10px;
                }}

                .scan-note {{
                    margin-top: 10px;
                    color: #444;
                    font-size: 13px;
                    word-break: break-word;
                }}

                .edit-container {{
                    max-width: 700px;
                    margin: 50px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                }}

                .back-link {{
                    display: inline-block;
                    margin-top: 15px;
                    text-decoration: none;
                    color: #1565c0;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Task Reminder</h1>
                <p>Manage your tasks, deadlines, and stay organised with reminders in one place.</p>

                <form action="/add" method="post" class="task-form">
                    <input type="text" name="task_name" placeholder="Enter a task" required>

                    <select name="task_type" required>
                        <option value="">Select Type</option>
                        <option value="Study">Study</option>
                        <option value="Email">Email</option>
                        <option value="Phone Call">Phone Call</option>
                        <option value="Meeting">Meeting</option>
                        <option value="Other">Other</option>
                    </select>

                    <select name="priority" required>
                        <option value="">Select Priority</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                    </select>

                    <input type="date" name="deadline" required>

                    <button type="submit" class="add-btn">Add Task</button>
                </form>

                <h2>Your Tasks</h2>
                <ul>
    """

    for number, task in enumerate(tasks, start=1):
        completed_class = "completed" if task["completed"] == 1 else ""
        priority_class = task["priority"].lower()
        overdue_class = ""

        if task["completed"] == 0 and task["deadline"] < today:
            overdue_class = "overdue"

        if task["priority"] == "High":
            badge_class = "badge-high"
        elif task["priority"] == "Medium":
            badge_class = "badge-medium"
        else:
            badge_class = "badge-low"

        status = "Completed" if task["completed"] == 1 else "Pending"

        warning_message = ""
        if task["completed"] == 0 and task["deadline"] < today:
            warning_message = "<div class='warning'>This task is overdue!</div>"

        html_content += f"""
                    <li class="task-card {completed_class} {priority_class} {overdue_class}">
                        <div class="task-title">{number}. {task["name"]}</div>

                        <div class="task-info">
                            <span class="badge {badge_class}">{task["priority"]}</span>
                            <span class="badge badge-type">{task["task_type"]}</span>
                            Deadline: <strong>{task["deadline"]}</strong>
                            | Status: <strong>{status}</strong>
                        </div>

                        {warning_message}

                        <div class="actions">
                            <form action="/complete/{task["id"]}" method="post" style="display:inline;">
                                <button type="submit" class="complete-btn">Complete</button>
                            </form>

                            <a href="/edit/{task["id"]}" class="edit-btn">Edit</a>

                            <form action="/delete/{task["id"]}" method="post" style="display:inline;">
                                <button type="submit" class="delete-btn">Delete</button>
                            </form>
                        </div>
                    </li>
        """

    html_content += f"""
                </ul>

                <div class="footer">
                    <div class="ys-logo">Ys</div>
                    <div class="footer-text">Scan to open Task Reminder</div>

                    <div class="qr-box">
                        <img src="{qr_code_url}" alt="QR Code">
                    </div>

                    <div class="scan-note">
                        QR target: {qr_target}
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    return html_content


@app.get("/edit/{task_id}", response_class=HTMLResponse)
def edit_task_page(task_id: int):
    task = get_task_by_id(task_id)

    if not task:
        return HTMLResponse("<h2>Task not found</h2>", status_code=404)

    high_selected = "selected" if task["priority"] == "High" else ""
    medium_selected = "selected" if task["priority"] == "Medium" else ""
    low_selected = "selected" if task["priority"] == "Low" else ""

    study_selected = "selected" if task["task_type"] == "Study" else ""
    email_selected = "selected" if task["task_type"] == "Email" else ""
    phone_selected = "selected" if task["task_type"] == "Phone Call" else ""
    meeting_selected = "selected" if task["task_type"] == "Meeting" else ""
    other_selected = "selected" if task["task_type"] == "Other" else ""

    html_content = f"""
    <html>
        <head>
            <title>Edit Task</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(to right, #e3f2fd, #fce4ec);
                    margin: 0;
                    padding: 0;
                }}

                .edit-container {{
                    max-width: 700px;
                    margin: 50px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                }}

                h1 {{
                    text-align: center;
                    color: #1565c0;
                }}

                form {{
                    display: flex;
                    flex-direction: column;
                    gap: 14px;
                    margin-top: 20px;
                }}

                input, select, button {{
                    padding: 12px;
                    border-radius: 10px;
                    border: 1px solid #ccc;
                    font-size: 14px;
                }}

                button {{
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    font-weight: bold;
                    cursor: pointer;
                }}

                .back-link {{
                    display: inline-block;
                    margin-top: 15px;
                    text-decoration: none;
                    color: #1565c0;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="edit-container">
                <h1>Edit Task</h1>

                <form action="/update/{task["id"]}" method="post">
                    <input type="text" name="task_name" value="{task["name"]}" required>

                    <select name="task_type" required>
                        <option value="Study" {study_selected}>Study</option>
                        <option value="Email" {email_selected}>Email</option>
                        <option value="Phone Call" {phone_selected}>Phone Call</option>
                        <option value="Meeting" {meeting_selected}>Meeting</option>
                        <option value="Other" {other_selected}>Other</option>
                    </select>

                    <select name="priority" required>
                        <option value="High" {high_selected}>High</option>
                        <option value="Medium" {medium_selected}>Medium</option>
                        <option value="Low" {low_selected}>Low</option>
                    </select>

                    <input type="date" name="deadline" value="{task["deadline"]}" required>

                    <button type="submit">Save Changes</button>
                </form>

                <a href="/" class="back-link">← Back to Home</a>
            </div>
        </body>
    </html>
    """

    return html_content


@app.post("/add")
def add_task(
    task_name: str = Form(...),
    task_type: str = Form(...),
    priority: str = Form(...),
    deadline: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (name, task_type, priority, deadline, completed)
        VALUES (?, ?, ?, ?, ?)
    """, (task_name, task_type, priority, deadline, 0))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=303)


@app.post("/update/{task_id}")
def update_task(
    task_id: int,
    task_name: str = Form(...),
    task_type: str = Form(...),
    priority: str = Form(...),
    deadline: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET name = ?, task_type = ?, priority = ?, deadline = ?
        WHERE id = ?
    """, (task_name, task_type, priority, deadline, task_id))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=303)


@app.post("/complete/{task_id}")
def complete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=303)

