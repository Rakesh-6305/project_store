import sqlite3
import os

# Update database path for Render environment
db_path = os.path.join(os.getcwd(), "app_data.db")

try:
    # Connect to the database
    con = sqlite3.connect(db_path)
    
    # Create tables
    con.execute("""
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

    con.execute("""
    CREATE TABLE IF NOT EXISTS project_photos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    photo_path TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS project_videos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    video_path TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    student_username TEXT,
    status TEXT DEFAULT 'Pending',
    transaction_id TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    # Add admin table creation
    con.execute("""
    CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
    )
    """)

    # Add students table creation
    con.execute("""
    CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    email TEXT
    )
    """)

    # Commit the changes
    con.commit()
    print("Database initialized successfully.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the connection is closed
    if con:
        con.close()
