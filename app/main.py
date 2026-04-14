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
                <button type="submit">Add Task</button>
            </form>

            <h2>Your Tasks</h2>
            <ul>
    """

    for index, task in enumerate(tasks):
        status_text = "Completed" if task["completed"] else "Pending"

        html_content += f"""
                <li>
                    <strong>{task["name"]}</strong> - {status_text}
        """

        if not task["completed"]:
            html_content += f'<a href="/complete/{index}"> Mark as Complete</a>'

        html_content += "</li>"

    html_content += """
            </ul>
        </body>
    </html>
    """
    return html_content


@app.post("/add")
def add_task(task_name: str = Form(...)):
    tasks.append({"name": task_name, "completed": False})
    return RedirectResponse(url="/", status_code=303)


@app.get("/complete/{task_index}")
def complete_task(task_index: int):
    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
    return RedirectResponse(url="/", status_code=303)


