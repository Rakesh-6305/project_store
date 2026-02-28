import sqlite3
import os

db_path = "app_data.db"
con = sqlite3.connect(db_path)

tables = [
    """CREATE TABLE IF NOT EXISTS project_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_username TEXT,
        title TEXT,
        description TEXT,
        problem_statement TEXT,
        objectives TEXT,
        outcomes TEXT,
        output_idea TEXT,
        price INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Requested',
        transaction_id TEXT,
        final_file TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS request_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER,
        photo_path TEXT,
        FOREIGN KEY(request_id) REFERENCES project_requests(id)
    )""",
    """CREATE TABLE IF NOT EXISTS request_videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER,
        video_path TEXT,
        FOREIGN KEY(request_id) REFERENCES project_requests(id)
    )"""
]

print(f"Checking tables in {db_path}...")
for sql in tables:
    con.execute(sql)
    print("Executed table creation check.")

con.commit()
con.close()
print("Database fix completed.")
