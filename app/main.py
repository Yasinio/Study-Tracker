from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date

app = FastAPI()

tasks = []


@app.get("/", response_class=HTMLResponse)
def home():
    today = date.today().isoformat()

    html_content = f"""
    <html>
        <head>
            <title>Cloud DevOps Study Tracker</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(to right, #e3f2fd, #fce4ec);
                    margin: 0;
                    padding: 0;
                }}

                .container {{
                    max-width: 900px;
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

                form {{
                    margin-bottom: 15px;
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
                    margin-left: 8px;
                }}

                .delete-btn {{
                    background-color: #d32f2f;
                    color: white;
                    margin-left: 8px;
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

                h2 {{
                    color: #333;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Cloud DevOps Study Tracker</h1>
                <p>Track study tasks, emails, calls, and deadlines in one place.</p>

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

    for index, task in enumerate(tasks):
        completed_class = "completed" if task["completed"] else ""
        priority_class = task["priority"].lower()
        overdue_class = ""

        if not task["completed"] and task["deadline"] < today:
            overdue_class = "overdue"

        if task["priority"] == "High":
            badge_class = "badge-high"
        elif task["priority"] == "Medium":
            badge_class = "badge-medium"
        else:
            badge_class = "badge-low"

        status = "✅ Completed" if task["completed"] else "⏳ Pending"

        warning_message = ""
        if not task["completed"] and task["deadline"] < today:
            warning_message = "<div class='warning'>⚠ This task is overdue!</div>"

        html_content += f"""
                    <li class="task-card {completed_class} {priority_class} {overdue_class}">
                        <div class="task-title">{task["name"]}</div>

                        <div class="task-info">
                            <span class="badge {badge_class}">{task["priority"]}</span>
                            <span class="badge badge-type">{task["task_type"]}</span>
                            Deadline: <strong>{task["deadline"]}</strong>
                            | Status: <strong>{status}</strong>
                        </div>

                        {warning_message}

                        <div class="actions">
                            <form action="/complete/{index}" method="post" style="display:inline;">
                                <button type="submit" class="complete-btn">Complete</button>
                            </form>

                            <form action="/delete/{index}" method="post" style="display:inline;">
                                <button type="submit" class="delete-btn">Delete</button>
                            </form>
                        </div>
                    </li>
        """

    html_content += """
                </ul>
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
    tasks.append({
        "name": task_name,
        "task_type": task_type,
        "priority": priority,
        "deadline": deadline,
        "completed": False
    })

    return RedirectResponse(url="/", status_code=303)


@app.post("/complete/{task_id}")
def complete_task(task_id: int):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = True

    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{task_id}")
def delete_task(task_id: int):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)

    return RedirectResponse(url="/", status_code=303)

