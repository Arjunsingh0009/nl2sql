import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.getenv("DB_PATH", "nl2sql.db")

SCHEMA_INFO = {
    "departments": {
        "columns": ["id", "name", "budget", "location", "created_at"],
        "description": "Company departments with budget and location info"
    },
    "employees": {
        "columns": ["id", "first_name", "last_name", "email", "department_id", "salary", "hire_date", "job_title", "age", "gender"],
        "description": "Employee records with salary, department, and job info",
        "foreign_keys": {"department_id": "departments.id"}
    },
    "students": {
        "columns": ["id", "name", "email", "age", "major", "gpa", "enrollment_year", "graduation_year"],
        "description": "Student records with academic details"
    },
    "courses": {
        "columns": ["id", "course_name", "course_code", "credits", "instructor", "department"],
        "description": "Course catalog with instructor and credit info"
    },
    "enrollments": {
        "columns": ["id", "student_id", "course_id", "grade", "semester", "year"],
        "description": "Student course enrollments with grades",
        "foreign_keys": {"student_id": "students.id", "course_id": "courses.id"}
    },
    "products": {
        "columns": ["id", "name", "category", "price", "stock_quantity", "supplier"],
        "description": "Product catalog with pricing and inventory"
    },
    "sales": {
        "columns": ["id", "product_id", "employee_id", "quantity", "total_amount", "sale_date", "region"],
        "description": "Sales transactions with product, employee, and region info",
        "foreign_keys": {"product_id": "products.id", "employee_id": "employees.id"}
    }
}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database with schema and seed data."""
    conn = get_connection()
    cur = conn.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        cur.executescript(f.read())

    cur.execute("SELECT COUNT(*) FROM departments")
    if cur.fetchone()[0] == 0:
        seed_data(cur)

    conn.commit()
    conn.close()


def seed_data(cur):
    """Insert realistic sample data."""
    departments = [
        ("Engineering", 1200000, "New York"),
        ("Marketing", 450000, "Los Angeles"),
        ("Sales", 800000, "Chicago"),
        ("HR", 300000, "Austin"),
        ("Finance", 600000, "Boston"),
        ("Product", 900000, "San Francisco"),
    ]
    cur.executemany(
        "INSERT INTO departments (name, budget, location) VALUES (?,?,?)",
        departments
    )

    majors = ["Computer Science", "Mathematics", "Physics", "Business",
              "Psychology", "Biology", "English", "Engineering"]
    student_names = [
        ("Alice Johnson", "alice@uni.edu"), ("Bob Smith", "bob@uni.edu"),
        ("Carol White", "carol@uni.edu"), ("David Brown", "david@uni.edu"),
        ("Emma Davis", "emma@uni.edu"), ("Frank Miller", "frank@uni.edu"),
        ("Grace Wilson", "grace@uni.edu"), ("Henry Moore", "henry@uni.edu"),
        ("Isla Taylor", "isla@uni.edu"), ("Jack Anderson", "jack@uni.edu"),
        ("Karen Thomas", "karen@uni.edu"), ("Liam Jackson", "liam@uni.edu"),
        ("Mia Harris", "mia@uni.edu"), ("Noah Martin", "noah@uni.edu"),
        ("Olivia Garcia", "olivia@uni.edu"), ("Paul Martinez", "paul@uni.edu"),
        ("Quinn Robinson", "quinn@uni.edu"), ("Rachel Clark", "rachel@uni.edu"),
        ("Sam Rodriguez", "sam@uni.edu"), ("Tina Lewis", "tina@uni.edu"),
    ]
    for name, email in student_names:
        cur.execute(
            "INSERT INTO students (name, email, age, major, gpa, enrollment_year, graduation_year) VALUES (?,?,?,?,?,?,?)",
            (name, email, random.randint(18, 25), random.choice(majors),
             round(random.uniform(2.5, 4.0), 2),
             random.choice([2020, 2021, 2022]),
             random.choice([2024, 2025, 2026]))
        )

    courses_data = [
        ("Introduction to Programming", "CS101", 3, "Prof. Adams", "Computer Science"),
        ("Data Structures", "CS201", 4, "Prof. Baker", "Computer Science"),
        ("Database Systems", "CS301", 3, "Prof. Chang", "Computer Science"),
        ("Machine Learning", "CS401", 4, "Prof. Davis", "Computer Science"),
        ("Calculus I", "MATH101", 4, "Prof. Evans", "Mathematics"),
        ("Linear Algebra", "MATH201", 3, "Prof. Foster", "Mathematics"),
        ("Statistics", "MATH301", 3, "Prof. Green", "Mathematics"),
        ("Physics I", "PHY101", 4, "Prof. Hall", "Physics"),
        ("Business Management", "BUS101", 3, "Prof. Irving", "Business"),
        ("Marketing Fundamentals", "BUS201", 3, "Prof. Johnson", "Business"),
    ]
    cur.executemany(
        "INSERT INTO courses (course_name, course_code, credits, instructor, department) VALUES (?,?,?,?,?)",
        courses_data
    )

    grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "D", "F"]
    semesters = ["Fall", "Spring", "Summer"]
    for student_id in range(1, 21):
        enrolled = random.sample(range(1, 11), random.randint(2, 5))
        for course_id in enrolled:
            cur.execute(
                "INSERT INTO enrollments (student_id, course_id, grade, semester, year) VALUES (?,?,?,?,?)",
                (student_id, course_id, random.choice(grades),
                 random.choice(semesters), random.choice([2022, 2023, 2024]))
            )

    titles = ["Software Engineer", "Senior Engineer", "Team Lead", "Manager",
              "Analyst", "Specialist", "Coordinator", "Director"]
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer",
                   "Michael", "Linda", "William", "Barbara", "Richard", "Susan",
                   "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                  "Garcia", "Miller", "Davis", "Wilson", "Moore"]
    for i in range(30):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        dept = random.randint(1, 6)
        hire = (datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3000))).strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO employees (first_name, last_name, email, department_id, salary, hire_date, job_title, age, gender) VALUES (?,?,?,?,?,?,?,?,?)",
            (fname, lname, f"{fname.lower()}.{lname.lower()}{i}@company.com",
             dept, round(random.uniform(45000, 150000), 2), hire,
             random.choice(titles), random.randint(22, 60),
             random.choice(["Male", "Female"]))
        )

    product_names = ["Laptop", "T-Shirt", "Coffee Beans", "Python Book",
                     "Running Shoes", "Desk Lamp", "Headphones", "Jeans",
                     "Green Tea", "SQL Guide", "Yoga Mat", "Hand Cream",
                     "Monitor", "Jacket", "Protein Powder", "React Handbook",
                     "Tennis Racket", "Candle"]
    categories = ["Electronics", "Clothing", "Food", "Books", "Sports", "Home", "Beauty"]
    suppliers = ["TechCorp", "FashionHub", "FoodPlus", "BookWorld", "SportZone", "HomeDecor"]
    for pname in product_names:
        cur.execute(
            "INSERT INTO products (name, category, price, stock_quantity, supplier) VALUES (?,?,?,?,?)",
            (pname, random.choice(categories), round(random.uniform(5, 1500), 2),
             random.randint(10, 500), random.choice(suppliers))
        )

    regions = ["North", "South", "East", "West", "Central"]
    base_date = datetime(2023, 1, 1)
    for _ in range(100):
        prod_id = random.randint(1, len(product_names))
        emp_id = random.randint(1, 30)
        qty = random.randint(1, 20)
        sale_date = (base_date + timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO sales (product_id, employee_id, quantity, total_amount, sale_date, region) VALUES (?,?,?,?,?,?)",
            (prod_id, emp_id, qty, round(qty * random.uniform(10, 500), 2),
             sale_date, random.choice(regions))
        )


def execute_multiple_queries(sql: str):
    """Execute multiple SQL statements and return combined results."""
    conn = get_connection()
    try:
        # Split statements by semicolon
        raw_statements = sql.split(";")
        statements = [s.strip() for s in raw_statements if s.strip()]

        if not statements:
            raise Exception("No SQL statements found.")

        all_results = []
        last_select_result = None
        total_affected = 0

        for i, statement in enumerate(statements):
            cur = conn.cursor()
            sql_upper = statement.strip().upper()

            try:
                # Handle transaction keywords
                if sql_upper.startswith("BEGIN"):
                    conn.execute("BEGIN")
                    all_results.append({
                        "statement": statement[:60],
                        "result": "✅ Transaction started.",
                        "rows": 0
                    })

                elif sql_upper.startswith("COMMIT"):
                    conn.commit()
                    all_results.append({
                        "statement": statement[:60],
                        "result": "✅ Transaction committed successfully.",
                        "rows": 0
                    })

                elif sql_upper.startswith("ROLLBACK"):
                    conn.rollback()
                    all_results.append({
                        "statement": statement[:60],
                        "result": "⚠️ Transaction rolled back.",
                        "rows": 0
                    })

                elif sql_upper.startswith("SELECT"):
                    cur.execute(statement)
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description] if cur.description else []
                    last_select_result = {
                        "columns": columns,
                        "rows": [list(row) for row in rows],
                        "row_count": len(rows)
                    }
                    all_results.append({
                        "statement": statement[:60],
                        "result": f"✅ Returned {len(rows)} row(s).",
                        "rows": len(rows)
                    })

                elif sql_upper.startswith(("INSERT", "UPDATE", "DELETE")):
                    cur.execute(statement)
                    conn.commit()
                    affected = cur.rowcount
                    total_affected += affected
                    all_results.append({
                        "statement": statement[:60],
                        "result": f"✅ {affected} row(s) affected.",
                        "rows": affected
                    })

                elif sql_upper.startswith(("CREATE", "ALTER", "DROP",
                                           "TRUNCATE", "CREATE VIEW",
                                           "CREATE INDEX")):
                    cur.execute(statement)
                    conn.commit()
                    all_results.append({
                        "statement": statement[:60],
                        "result": "✅ Executed successfully.",
                        "rows": 0
                    })

                else:
                    cur.execute(statement)
                    conn.commit()
                    all_results.append({
                        "statement": statement[:60],
                        "result": "✅ Executed successfully.",
                        "rows": 0
                    })

            except Exception as e:
                conn.rollback()
                all_results.append({
                    "statement": statement[:60],
                    "result": f"❌ Error: {str(e)}",
                    "rows": 0
                })

        # If there was a SELECT — show its results as main output
        if last_select_result and len(statements) == 1:
            return last_select_result

        # For multiple statements — show summary table
        return {
            "columns": ["#", "Statement", "Result", "Rows Affected"],
            "rows": [
                [i + 1, r["statement"] + "...", r["result"], r["rows"]]
                for i, r in enumerate(all_results)
            ],
            "row_count": len(all_results),
            "message": f"Executed {len(statements)} statement(s) successfully."
        }

    except Exception as e:
        conn.rollback()
        raise Exception(f"SQL Error: {str(e)}")
    finally:
        conn.close()


# Keep old function for compatibility
def execute_query(sql: str):
    return execute_multiple_queries(sql)


def get_schema_string():
    """Return a compact schema string for the LLM prompt."""
    lines = []
    for table, info in SCHEMA_INFO.items():
        cols = ", ".join(info["columns"])
        lines.append(f"- {table}({cols})  # {info['description']}")
        if "foreign_keys" in info:
            for col, ref in info["foreign_keys"].items():
                lines.append(f"    FK: {table}.{col} -> {ref}")
    return "\n".join(lines)