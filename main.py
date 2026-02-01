# Personal Expense Tracker – FastAPI + Modern UI
# Run: python main.py

import os
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

try:
  from fastapi import FastAPI, Request, Form
  from fastapi.responses import HTMLResponse, RedirectResponse
  from fastapi.staticfiles import StaticFiles
  from fastapi.templating import Jinja2Templates
except ModuleNotFoundError as e:
  print(f"Missing Python package: {e.name}")
  print("Install dependencies with: python -m pip install -r requirements.txt")
  raise SystemExit(1)

app = FastAPI()

# --- Database ---
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")
conn.commit()

TEMPLATE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Expense Tracker</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{{ request.url_for('static', path='css/styles.css') }}">
  <script src="{{ request.url_for('static', path='js/app.js') }}" defer></script>
</head>
<body>
  <div class="container">
    <h1>💸 Personal Expense Tracker</h1>

    <div class="card">
      <form action="/add" method="post">
        <input name="title" placeholder="Expense name" required />
        <input name="amount" type="number" step="0.01" placeholder="Amount" required />
        <select name="category">
          <option>Food</option>
          <option>Transport</option>
          <option>Shopping</option>
          <option>Entertainment</option>
          <option>Other</option>
        </select>
        <button>Add</button>
      </form>
    </div>

    <div class="card">
      <table>
        <tr>
          <th>Title</th><th>Amount</th><th>Category</th><th>Date</th><th></th>
        </tr>
        {% for e in expenses %}
        <tr>
          <td>{{ e[1] }}</td>
          <td>${{ '%.2f'|format(e[2]) }}</td>
          <td>{{ e[3] }}</td>
          <td>{{ e[4] }}</td>
          <td><a class="delete" href="/delete/{{ e[0] }}">✕</a></td>
        </tr>
        {% endfor %}
      </table>
      <div class="total">Total Spent: ${{ '%.2f'|format(total) }}</div>
    </div>
  </div>
</body>
</html>
"""

# Ensure templates folder and index.html exist so app can run without manual setup
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
index_path = TEMPLATES_DIR / "index.html"
if not index_path.exists():
    index_path.write_text(TEMPLATE_HTML, encoding="utf-8")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# mount static files
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    total = sum(e[2] for e in expenses)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "expenses": expenses,
        "total": total
    })

@app.post("/add")
def add_expense(
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...)
):
    cursor.execute(
        "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
        (title, amount, category, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/delete/{expense_id}")
def delete_expense(expense_id: int):
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    return RedirectResponse("/", status_code=303)

# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


# -----------------------------
# Create folder: templates/
# Create file: templates/index.html
# -----------------------------

"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Expense Tracker</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: Inter, sans-serif;
      background: linear-gradient(135deg, #0f172a, #020617);
      color: #e5e7eb;
      margin: 0;
      padding: 40px;
    }
    .container {
      max-width: 900px;
      margin: auto;
    }
    h1 {
      font-size: 2.2rem;
      margin-bottom: 10px;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 20px 40px rgba(0,0,0,.6);
      margin-bottom: 24px;
    }
    form {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr auto;
      gap: 12px;
    }
    input, select, button {
      padding: 12px;
      border-radius: 10px;
      border: none;
      font-size: 14px;
    }
    input, select {
      background: #020617;
      color: #fff;
      border: 1px solid #1e293b;
    }
    button {
      background: #6366f1;
      color: #fff;
      cursor: pointer;
      font-weight: 600;
    }
    button:hover { background: #4f46e5; }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 14px;
      border-bottom: 1px solid #1e293b;
      text-align: left;
    }
    .delete {
      color: #f87171;
      text-decoration: none;
      font-weight: bold;
    }
    .total {
      font-size: 1.4rem;
      margin-top: 10px;
      color: #a5b4fc;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💸 Personal Expense Tracker</h1>

    <div class="card">
      <form action="/add" method="post">
        <input name="title" placeholder="Expense name" required />
        <input name="amount" type="number" step="0.01" placeholder="Amount" required />
        <select name="category">
          <option>Food</option>
          <option>Transport</option>
          <option>Shopping</option>
          <option>Entertainment</option>
          <option>Other</option>
        </select>
        <button>Add</button>
      </form>
    </div>

    <div class="card">
      <table>
        <tr>
          <th>Title</th><th>Amount</th><th>Category</th><th>Date</th><th></th>
        </tr>
        {% for e in expenses %}
        <tr>
          <td>{{ e[1] }}</td>
          <td>${{ '%.2f'|format(e[2]) }}</td>
          <td>{{ e[3] }}</td>
          <td>{{ e[4] }}</td>
          <td><a class="delete" href="/delete/{{ e[0] }}">✕</a></td>
        </tr>
        {% endfor %}
      </table>
      <div class="total">Total Spent: ${{ '%.2f'|format(total) }}</div>
    </div>
  </div>
</body>
</html>
"""
