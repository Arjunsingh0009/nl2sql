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

SYSTEM_PROMPT = """You are an expert SQLite SQL query generator. Convert natural language to valid SQLite SQL queries.

DATABASE SCHEMA:
{schema}

RULES:
1. Output ONLY valid SQL statements — no markdown, no backticks, no explanation, no comments.
2. Support ALL SQL operations:
   - DDL: CREATE TABLE, CREATE VIEW, CREATE INDEX, ALTER TABLE, DROP TABLE, DROP VIEW
   - DML: SELECT, INSERT, UPDATE, DELETE, TRUNCATE
   - TCL: BEGIN TRANSACTION, COMMIT, ROLLBACK
   - Aggregations: COUNT, SUM, AVG, MAX, MIN, GROUP BY, HAVING
   - Joins: INNER JOIN, LEFT JOIN, RIGHT JOIN
   - Subqueries, DISTINCT, ORDER BY, LIMIT, OFFSET
3. Use SQLite-compatible syntax ONLY:
   - Use INTEGER PRIMARY KEY AUTOINCREMENT
   - Use TEXT for strings
   - Use REAL for decimals
   - Use strftime() for date functions
   - SQLite does not support RIGHT JOIN — use LEFT JOIN instead
   - SQLite does not support stored procedures
4. For multiple operations — separate each statement with a semicolon on a new line.
5. For CREATE TABLE — always include data types and constraints.
6. For INSERT — always include column names.
7. For transactions — wrap in BEGIN TRANSACTION and COMMIT.
8. Return ONLY the SQL — nothing else.

EXAMPLES:

Q: Create employees table and insert records
A: CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, salary REAL, department TEXT, email TEXT UNIQUE);
INSERT INTO employees (name, salary, department, email) VALUES ('Alice', 75000, 'Engineering', 'alice@company.com');
INSERT INTO employees (name, salary, department, email) VALUES ('Bob', 55000, 'Marketing', 'bob@company.com');

Q: Show employees with salary between 30000 and 100000 whose name starts with A sorted by salary
A: SELECT * FROM employees WHERE salary BETWEEN 30000 AND 100000 AND name LIKE 'A%' ORDER BY salary DESC LIMIT 5

Q: Join employees with departments and show total and average salary per department where total exceeds 100000
A: SELECT d.name AS department_name, COUNT(e.id) AS employee_count, SUM(e.salary) AS total_salary, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.id, d.name HAVING SUM(e.salary) > 100000 ORDER BY total_salary DESC

Q: Update salary by 10 percent for Engineering department
A: UPDATE employees SET salary = salary * 1.10 WHERE department = 'Engineering'

Q: Create a view for high salary employees
A: CREATE VIEW IF NOT EXISTS high_salary_employees AS SELECT * FROM employees WHERE salary > 80000

Q: Create an index on salary column
A: CREATE INDEX IF NOT EXISTS idx_salary ON employees(salary)

Q: Delete employees who were hired before 2015
A: DELETE FROM employees WHERE hire_date < '2015-01-01'

Q: Truncate employees table
A: DELETE FROM employees

Q: Drop employees table
A: DROP TABLE IF EXISTS employees

Q: Use transaction to update and commit
A: BEGIN TRANSACTION;
UPDATE employees SET salary = salary * 1.10 WHERE department_id = 1;
COMMIT

Q: Create table insert data and select it
A: CREATE TABLE IF NOT EXISTS library (id INTEGER PRIMARY KEY AUTOINCREMENT, book_name TEXT NOT NULL, author TEXT, copies INTEGER DEFAULT 0);
INSERT INTO library (book_name, author, copies) VALUES ('Python Programming', 'Guido', 5);
INSERT INTO library (book_name, author, copies) VALUES ('SQL Guide', 'Joe Celko', 3);
SELECT * FROM library
"""

EXPLANATION_PROMPT = """You are an SQL expert. Given one or more SQL statements, explain what they do together in 3-4 clear sentences.
Focus on WHAT the query does — what data it creates, retrieves, modifies or deletes.
Do NOT include SQL syntax in your explanation."""


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate SQL — supports multiple statements of all types."""

    # Split into individual statements
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    if not statements:
        return False, "No SQL statements found."

    allowed_patterns = [
        r"^\s*SELECT\b",
        r"^\s*INSERT\b",
        r"^\s*UPDATE\b",
        r"^\s*DELETE\b",
        r"^\s*CREATE\b",
        r"^\s*ALTER\b",
        r"^\s*DROP\b",
        r"^\s*TRUNCATE\b",
        r"^\s*BEGIN\b",
        r"^\s*COMMIT\b",
        r"^\s*ROLLBACK\b",
        r"^\s*SAVEPOINT\b",
    ]

    for statement in statements:
        is_allowed = any(
            re.match(pattern, statement, re.IGNORECASE)
            for pattern in allowed_patterns
        )
        if not is_allowed:
            return False, f"Invalid SQL command: {statement[:50]}"

    # Block dangerous system-level keywords only
    forbidden = [
        r"\bxp_\w+",
        r"\bATTACH\b",
        r"\bDETACH\b",
        r"\bPRAGMA\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, sql, re.IGNORECASE):
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
        max_tokens=2000
    )

    sql_raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    sql_clean = re.sub(r"```(?:sql)?\s*", "", sql_raw, flags=re.IGNORECASE).strip()
    sql_clean = re.sub(r"```", "", sql_clean).strip()

    # Remove any explanation text before the SQL
    lines = sql_clean.split("\n")
    sql_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and any(re.match(p, stripped, re.IGNORECASE) for p in [
            r"^\s*SELECT\b", r"^\s*INSERT\b", r"^\s*UPDATE\b", r"^\s*DELETE\b",
            r"^\s*CREATE\b", r"^\s*ALTER\b", r"^\s*DROP\b", r"^\s*TRUNCATE\b",
            r"^\s*BEGIN\b", r"^\s*COMMIT\b", r"^\s*ROLLBACK\b", r"^\s*WITH\b",
            r".*\);?$", r".*VALUES.*", r".*WHERE.*", r".*JOIN.*", r".*GROUP.*",
            r".*ORDER.*", r".*HAVING.*", r".*SET\b.*",
        ]):
            sql_lines.append(line)
        elif sql_lines:
            sql_lines.append(line)

    sql_clean = "\n".join(sql_lines).strip() if sql_lines else sql_clean

    return {"sql": sql_clean, "raw": sql_raw}


def explain_sql(sql: str) -> str:
    """Convert SQL back to plain English explanation."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": EXPLANATION_PROMPT},
            {"role": "user", "content": f"Explain these SQL statements:\n{sql}"}
        ],
        temperature=0.1,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()