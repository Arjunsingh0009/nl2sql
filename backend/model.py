from dotenv import load_dotenv
load_dotenv()

import os
import re
from groq import Groq
from db import get_schema_string

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are an expert SQL query generator for SQLite databases. Convert natural language to valid SQL queries.

DATABASE SCHEMA:
{schema}

RULES:
1. Output ONLY a single SQL statement — no markdown, no backticks, no explanation.
2. Support ALL SQL operations: SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP.
3. Use SQLite-compatible syntax.
4. For CREATE TABLE — always include proper data types and PRIMARY KEY.
5. For INSERT — always include column names.
6. For SELECT — add LIMIT 500 unless user asks for all.
7. Return ONLY the SQL query nothing else.

EXAMPLES:
Q: Show all students with GPA above 3.5
A: SELECT * FROM students WHERE gpa > 3.5 ORDER BY gpa DESC

Q: Create a new table called projects with id, name, deadline and budget columns
A: CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, deadline TEXT, budget REAL)

Q: Add a new student named John with GPA 3.8 majoring in Computer Science
A: INSERT INTO students (name, email, age, major, gpa, enrollment_year, graduation_year) VALUES ('John', 'john@uni.edu', 20, 'Computer Science', 3.8, 2023, 2027)

Q: Update salary of employee with id 1 to 90000
A: UPDATE employees SET salary = 90000 WHERE id = 1

Q: Delete all students with GPA below 2.0
A: DELETE FROM students WHERE gpa < 2.0

Q: Add a new column phone to employees table
A: ALTER TABLE employees ADD COLUMN phone TEXT

Q: Drop the projects table
A: DROP TABLE IF EXISTS projects

Q: Count students per major
A: SELECT major, COUNT(*) AS student_count FROM students GROUP BY major ORDER BY student_count DESC

Q: Which department has the highest average salary?
A: SELECT d.name, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.id, d.name ORDER BY avg_salary DESC LIMIT 1

Q: Top 5 products by total sales revenue
A: SELECT p.name, SUM(s.total_amount) AS total_revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.id, p.name ORDER BY total_revenue DESC LIMIT 5
"""

EXPLANATION_PROMPT = """You are an SQL expert. Given a SQL query, explain it in plain English in 2-3 clear sentences.
Be concise and focus on WHAT the query does.
Do NOT include any SQL syntax in your explanation."""


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate that the SQL is safe."""
    sql_clean = sql.strip().rstrip(";").strip()

    # Allow all major SQL commands
    allowed_patterns = [
        r"^\s*SELECT\b",
        r"^\s*INSERT\b",
        r"^\s*UPDATE\b",
        r"^\s*DELETE\b",
        r"^\s*CREATE\b",
        r"^\s*ALTER\b",
        r"^\s*DROP\b",
        r"^\s*TRUNCATE\b",
    ]

    is_allowed = any(
        re.match(pattern, sql_clean, re.IGNORECASE)
        for pattern in allowed_patterns
    )

    if not is_allowed:
        return False, "Invalid SQL command."

    # Block dangerous injections only
    forbidden = [
        r"\bxp_\w+",
        r"/\*",
        r"\bATTACH\b",
        r"\bDETACH\b",
        r"\bPRAGMA\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, sql_clean, re.IGNORECASE):
            return False, "Forbidden keyword detected."

    return True, ""


def nl_to_sql(natural_language: str) -> dict:
    """Convert natural language to SQL using Groq."""
    schema = get_schema_string()
    prompt = SYSTEM_PROMPT.format(schema=schema)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": natural_language}
        ],
        temperature=0.1,
        max_tokens=500
    )

    sql_raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    sql_clean = re.sub(r"```(?:sql)?\s*", "", sql_raw, flags=re.IGNORECASE).strip()
    sql_clean = re.sub(r"```", "", sql_clean).strip()
    sql_clean = sql_clean.rstrip(";").strip()

    return {"sql": sql_clean, "raw": sql_raw}


def explain_sql(sql: str) -> str:
    """Convert SQL back to plain English explanation."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": EXPLANATION_PROMPT},
            {"role": "user", "content": f"Explain this SQL:\n{sql}"}
        ],
        temperature=0.1,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()