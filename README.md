# 🔍 NL2SQL — Natural Language to SQL Converter

A production-ready web application that converts plain English questions into SQL queries using Claude AI, executes them against a live SQLite database, and displays the results in a clean, dark-themed UI.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🧠 NL → SQL | Claude AI (claude-sonnet) with schema-aware prompting |
| 🔒 Security | SELECT-only enforcement, injection prevention, keyword blocking |
| 📊 Results Table | Sortable, filterable, paginated with 500-row limit |
| 💡 SQL Explanation | Converts generated SQL back to plain English |
| 📜 Query History | Last 20 queries with one-click replay |
| ⬡ Schema Viewer | Live interactive database schema browser |
| ⬇️ CSV Export | Download any result set as a CSV file |
| 🎨 Dark Terminal UI | Syne + JetBrains Mono, syntax-highlighted SQL |

---

## 🗂 Project Structure

```
nl2sql-project/
├── backend/
│   ├── main.py          # FastAPI app — all API endpoints
│   ├── model.py         # Claude AI NL→SQL + SQL explanation
│   ├── db.py            # SQLite init, seeding, query execution, schema
│   ├── schema.sql       # SQL DDL for all 7 tables
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variable template
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js           # Root component, state, API calls
│   │   ├── App.css          # Global dark theme + layout
│   │   └── components/
│   │       ├── QueryInput.js/css    # Text input with auto-resize
│   │       ├── SqlDisplay.js/css    # Syntax-highlighted SQL block
│   │       ├── ResultsTable.js/css  # Sortable, paginated table
│   │       ├── QueryHistory.js      # History side panel
│   │       ├── SchemaPanel.js       # Schema explorer side panel
│   │       └── SidePanel.css        # Shared panel styles
│   ├── package.json
│   └── .env.example
├── render.yaml          # Render.com deployment config
├── vercel.json          # Vercel deployment config
├── Procfile             # Railway/Heroku deployment
├── requirements.txt     # Root-level (for Railway auto-detection)
└── README.md
```

---

## 🗄 Database Schema

Seven interconnected sample tables:

```
departments   (id, name, budget, location)
employees     (id, first_name, last_name, email, department_id→, salary, hire_date, job_title, age, gender)
students      (id, name, email, age, major, gpa, enrollment_year, graduation_year)
courses       (id, course_name, course_code, credits, instructor, department)
enrollments   (id, student_id→, course_id→, grade, semester, year)
products      (id, name, category, price, stock_quantity, supplier)
sales         (id, product_id→, employee_id→, quantity, total_amount, sale_date, region)
```

Auto-seeded with realistic data: 30 employees, 20 students, 10 courses, 100+ sales transactions.

---

## 🚀 Local Setup (Run in VS Code)

### Prerequisites

- Python 3.10+
- Node.js 18+
- An Anthropic API key → https://console.anthropic.com

---

### Step 1 — Clone / Open the project

Open the `nl2sql-project/` folder in VS Code.

---

### Step 2 — Backend setup

Open a terminal in VS Code (`Ctrl + `` ` ``):

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
```

Edit `backend/.env` and add your API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
DB_PATH=nl2sql.db
PORT=8000
```

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

✅ Backend running at: http://localhost:8000  
✅ API docs at: http://localhost:8000/docs

---

### Step 3 — Frontend setup

Open a **second terminal** in VS Code:

```bash
cd frontend

# Install dependencies
npm install

# Create your .env file
cp .env.example .env
```

The default `frontend/.env` works as-is for local dev:
```
REACT_APP_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm start
```

✅ Frontend running at: http://localhost:3000

---

## 🌐 Deployment

### Backend → Render.com

1. Push project to GitHub
2. Go to https://render.com → New Web Service
3. Connect your repo
4. Set these:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `ANTHROPIC_API_KEY` = your key
6. Deploy → note your URL (e.g. `https://nl2sql-backend.onrender.com`)

### Frontend → Vercel

1. Go to https://vercel.com → New Project → Import your GitHub repo
2. Set:
   - **Root Directory:** `frontend`
   - **Framework:** Create React App
3. Add environment variable: `REACT_APP_API_URL` = your Render backend URL
4. Deploy ✅

---

## 🔒 Security Details

- Only `SELECT` queries are allowed (validated server-side)
- Forbidden keywords: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER`, `TRUNCATE`, `EXEC`, `UNION`, `ATTACH`, `PRAGMA`
- Multiple statements blocked (`;` in body)
- SQL comment injection blocked (`--`, `/*`)
- All queries validated **before** execution
- Results capped at 500 rows

---

## 🧪 Sample Queries to Try

```
Show all employees with salary above 80000
Which department has the highest average salary?
List the top 5 students by GPA
Count students per major
Show total sales by region
Find all employees hired after 2020
Which products have less than 50 items in stock?
Show courses with the most enrolled students
What is the average GPA by major?
List all sales in 2024 with product names
Which employee made the most sales?
Show employees and their department names
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | Convert NL to SQL and execute |
| GET | `/schema` | Get full database schema |
| GET | `/history` | Get last 20 queries |
| DELETE | `/history` | Clear query history |
| POST | `/download-csv` | Execute and return as CSV |
| GET | `/sample-questions` | Get sample query list |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI (auto-generated) |

### POST /query

**Request:**
```json
{
  "natural_language": "Show all students with GPA above 3.5",
  "explain": true
}
```

**Response:**
```json
{
  "sql": "SELECT * FROM students WHERE gpa > 3.5 ORDER BY gpa DESC",
  "columns": ["id", "name", "email", "age", "major", "gpa", "enrollment_year", "graduation_year"],
  "rows": [["1", "Alice Johnson", "alice@uni.edu", ...]],
  "row_count": 8,
  "explanation": "This query retrieves all student records where the GPA is greater than 3.5, sorted from highest to lowest GPA.",
  "execution_time_ms": 312.4
}
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, CSS3 (no UI library) |
| Backend | Python 3.10+, FastAPI |
| AI/NLP | Anthropic Claude (claude-sonnet-4) |
| Database | SQLite3 (file-based, zero config) |
| Fonts | Syne (display), JetBrains Mono (code) |
| Deployment | Render (backend), Vercel (frontend) |

---

## 🎓 Final Year Project Notes

This project demonstrates:
- **Full-stack development** (React + FastAPI)
- **AI/LLM integration** with prompt engineering
- **Schema-aware NL→SQL conversion**
- **Security best practices** (injection prevention, validation)
- **RESTful API design** with proper error handling
- **Responsive UI** with loading states
- **Cloud deployment** on Render + Vercel

---

## 📄 License

MIT — free to use for academic and personal projects.
