-- =============================================
-- NL2SQL Sample Database Schema
-- =============================================

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    budget REAL,
    location TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary REAL,
    hire_date TEXT,
    job_title TEXT,
    age INTEGER,
    gender TEXT
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER,
    major TEXT,
    gpa REAL,
    enrollment_year INTEGER,
    graduation_year INTEGER
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    course_code TEXT UNIQUE NOT NULL,
    credits INTEGER,
    instructor TEXT,
    department TEXT
);

-- Enrollments table (students <-> courses)
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade TEXT,
    semester TEXT,
    year INTEGER
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock_quantity INTEGER,
    supplier TEXT
);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    employee_id INTEGER REFERENCES employees(id),
    quantity INTEGER,
    total_amount REAL,
    sale_date TEXT,
    region TEXT
);
