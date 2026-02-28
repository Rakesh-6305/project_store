import sqlite3
import os

def init_db():
    db_path = os.path.join(os.getcwd(), "app_data.db")
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Create projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        project_file TEXT,
        price INTEGER,
        photo TEXT,
        video TEXT,
        description TEXT,
        problem_statement TEXT,
        objectives TEXT,
        outcomes TEXT,
        technologies TEXT
    )
    """)

    # Create project_photos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        photo_path TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    # Create project_videos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        video_path TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        student_username TEXT,
        status TEXT,
        transaction_id TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    con.commit()
    con.close()
