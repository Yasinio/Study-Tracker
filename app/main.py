from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

tasks = []


@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <html>
        <head>
            <title>Cloud DevOps Study Tracker</title>
        </head>
        <body>
            <h1>Cloud DevOps Study Tracker</h1>
            <p>Add your study tasks below.</p>

            <form action="/add" method="post">
                <input type="text" name="task_name" placeholder="Enter a study task" required>

                <select name="priority" required>
                    <option value="">Select Priority</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>

                <input type="date" name="due_date" required>

                <button type="submit">Add Task</button>
            </form>

            <h2>Your Tasks</h2>
            <ul>
    """

    for index, task in enumerate(tasks):
        status = "✅" if task["completed"] else "❌"

        html_content += f"""
            <li>
                {status} <strong>{task["name"]}</strong>
                | Priority: {task["priority"]}
                | Due Date: {task["due_date"]}

                <form action="/complete/{index}" method="post" style="display:inline;">
                    <button type="submit">Complete</button>
                </form>

                <form action="/delete/{index}" method="post" style="display:inline;">
                    <button type="submit">Delete</button>
                </form>
            </li>
        """

    html_content += """
            </ul>
        </body>
    </html>
    """

    return html_content


@app.post("/add")
def add_task(
    task_name: str = Form(...),
    priority: str = Form(...),
    due_date: str = Form(...)
):
    tasks.append({
        "name": task_name,
        "completed": False,
        "priority": priority,
        "due_date": due_date
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

