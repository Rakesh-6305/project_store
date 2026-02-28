import sqlite3

# Connect to the database
con = sqlite3.connect("app_data.db")

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

con.execute("""
CREATE TABLE IF NOT EXISTS project_requests(
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
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS request_photos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
request_id INTEGER,
photo_path TEXT,
FOREIGN KEY(request_id) REFERENCES project_requests(id)
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS request_videos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
request_id INTEGER,
video_path TEXT,
FOREIGN KEY(request_id) REFERENCES project_requests(id)
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS request_messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
request_id INTEGER,
sender TEXT,
message TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(request_id) REFERENCES project_requests(id)
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS order_messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INTEGER,
sender TEXT,
message TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(order_id) REFERENCES orders(id)
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS admin(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# Insert default admin user if not exists
admin_exists = con.execute("SELECT * FROM admin WHERE username='Rakesh'").fetchone()
if not admin_exists:
    con.execute("INSERT INTO admin(username,password) VALUES('Rakesh','Rakesh205@')")


# Commit and close connection
con.commit()
con.close()

print("StudentProjectHub Database initialized successfully!")
