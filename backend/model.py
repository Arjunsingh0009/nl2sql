from dotenv import load_dotenv
load_dotenv()

import os
import re
from groq import Groq
from db import get_schema_string

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert SQL query generator. Convert natural language questions to valid SQLite SQL queries.

DATABASE SCHEMA:
{schema}

RULES:
1. Output ONLY a single SQL SELECT statement.
2. No INSERT, UPDATE, DELETE, DROP, CREATE, ALTER allowed.
3. Use proper table aliases for JOINs.
4. Use SQLite-compatible syntax.
5. Add LIMIT 500 unless user asks for all.
6. Return ONLY the SQL query — no explanation, no markdown, no backticks.

EXAMPLES:
Q: Show all students with GPA above 3.5
A: SELECT * FROM students WHERE gpa > 3.5 ORDER BY gpa DESC

Q: Which department has the highest average salary?
A: SELECT d.name, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.id, d.name ORDER BY avg_salary DESC LIMIT 1

Q: Count students per major
A: SELECT major, COUNT(*) AS student_count FROM students GROUP BY major ORDER BY student_count DESC
"""

EXPLANATION_PROMPT = """You are an SQL expert. Explain the given SQL query in plain English in 2-3 sentences.
Focus on WHAT data it retrieves. Do NOT include SQL syntax in your explanation."""


def validate_sql(sql: str) -> tuple[bool, str]:
    sql_clean = sql.strip().rstrip(";").strip()

    if not re.match(r"^\s*SELECT\b", sql_clean, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    forbidden = [
        r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
        r"\bCREATE\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bEXEC\b",
        r"\bUNION\b", r"\bATTACH\b", r"\bPRAGMA\b", r"--", r"/\*",
    ]
    for pattern in forbidden:
        if re.search(pattern, sql_clean, re.IGNORECASE):
            return False, "Forbidden keyword detected."

    if sql_clean.count(";") > 0:
        return False, "Multiple SQL statements are not allowed."

    return True, ""


def nl_to_sql(natural_language: str) -> dict:
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
    sql_clean = re.sub(r"```(?:sql)?\s*", "", sql_raw, flags=re.IGNORECASE).strip()
    sql_clean = sql_clean.rstrip(";").strip()

    return {"sql": sql_clean, "raw": sql_raw}


def explain_sql(sql: str) -> str:
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
