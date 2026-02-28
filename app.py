from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="secret"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # Increased to 100MB per your suggestion

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Initialization Check
def init_db():
    con = sqlite3.connect("app_data.db")
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
    con.commit()
    con.close()

init_db()

# Define the missing handle_sqlite_error function
def handle_sqlite_error(error):
    return jsonify({"error": "Database error occurred", "message": str(error)}), 500


# ---------------- ADMIN LOGIN ----------------
# HOME PAGE
@app.route("/")
def home():
    try:
        con = sqlite3.connect("app_data.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        projects_raw = cur.execute("SELECT * FROM projects").fetchall()
        return render_template("index.html", projects=projects_raw)
    except sqlite3.OperationalError as e:
        return handle_sqlite_error(e)
    finally:
        if con:
            con.close()


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login",methods=["GET","POST"])
def admin_login():

    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]

        con=sqlite3.connect("app_data.db")
        admin=con.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (u,p)).fetchone()

        if admin:
            session["admin"]=u
            return redirect("/admin_dashboard")

    return render_template("admin_login.html")


# ADMIN DASHBOARD
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")
    return render_template("admin_dashboard.html")


# ADMIN ORDERS
@app.route("/admin_orders")
def admin_orders():
    if "admin" not in session:
        return redirect("/admin_login")
    con = sqlite3.connect("app_data.db")
    orders = con.execute("""
        SELECT orders.id, projects.title, orders.student_username, orders.status, orders.transaction_id
        FROM orders 
        JOIN projects ON orders.project_id = projects.id
    """).fetchall()
    return render_template("admin_orders.html", orders=orders)


# ADD PROJECT
@app.route("/add_project",methods=["POST"])
def add_project():
    title=request.form["title"]
    price=request.form["price"]
    description=request.form.get("description", "")
    problem_statement=request.form.get("problem_statement", "")
    objectives=request.form.get("objectives", "")
    outcomes=request.form.get("outcomes", "")
    
    technologies = request.form.get("technologies", "")
    
    photos = request.files.getlist("photos")
    videos = request.files.getlist("videos")
    project_file = request.files.get("project_file")

    con=sqlite3.connect("app_data.db")
    cursor = con.cursor()
    
    file_path = ""
    if project_file and project_file.filename:
        filename = secure_filename(project_file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        project_file.save(path)
        file_path = "uploads/" + filename

    # Insert main project details
    cursor.execute("INSERT INTO projects(title,project_file,price,photo,video,description,problem_statement,objectives,outcomes,technologies) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (title,file_path,price,"","",description,problem_statement,objectives,outcomes,technologies))
    project_id = cursor.lastrowid

    
    # Save photos
    for photo in photos:
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            db_path = "uploads/" + filename
            cursor.execute("INSERT INTO project_photos(project_id, photo_path) VALUES(?,?)", (project_id, db_path))
            
    # Save videos
    for video in videos:
        if video and video.filename:
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(video_path)
            db_path = "uploads/" + filename
            cursor.execute("INSERT INTO project_videos(project_id, video_path) VALUES(?,?)", (project_id, db_path))

    con.commit()
    con.close()

    return redirect("/admin_dashboard")





# DELETE PROJECT
@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect("/admin_login")
    con=sqlite3.connect("app_data.db")
    con.execute("DELETE FROM projects WHERE id=?",(id,))
    con.commit()
    con.close()
    return redirect("/")


# ---------------- STUDENT LOGIN ----------------
@app.route("/student_login",methods=["GET","POST"])
def student_login():

    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]

        con=sqlite3.connect("app_data.db")
        user=con.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u,p)).fetchone()

        if user:
            session["student"]=u
            return redirect("/")

    return render_template("student_login.html")


# REGISTER
@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u=request.form["username"]
        p=request.form["password"]

        con=sqlite3.connect("app_data.db")
        con.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        con.commit()

        return redirect("/student_login")
    
    return render_template("student_register.html")


# CHECKOUT (Manual UPI)
@app.route("/checkout/<int:id>")
def checkout(id):
    if "student" not in session:
        return redirect("/student_login")
        
    con = sqlite3.connect("app_data.db")
    project = con.execute("SELECT id, title, price FROM projects WHERE id=?", (id,)).fetchone()
    
    if not project:
        return redirect("/")
        
    return render_template("checkout.html", project=project)


# SUBMIT PAYMENT (Manual Transaction ID)
@app.route("/submit_payment/<int:project_id>", methods=["POST"])
def submit_payment(project_id):
    if "student" not in session:
        return redirect("/student_login")
        
    txn_id = request.form.get("transaction_id")
    student_username = session["student"]
    
    con = sqlite3.connect("app_data.db")
    
    # Check if already has a record
    existing = con.execute("SELECT * FROM orders WHERE project_id=? AND student_username=?", 
                           (project_id, student_username)).fetchone()
                           
    if not existing:
        con.execute("INSERT INTO orders(project_id, student_username, status, transaction_id) VALUES(?, ?, 'Pending', ?)",
                    (project_id, student_username, txn_id))
    else:
        con.execute("UPDATE orders SET status='Pending', transaction_id=? WHERE project_id=? AND student_username=?",
                    (txn_id, project_id, student_username))
                    
    con.commit()
    con.close()
    
    return redirect("/")




# ---------------- PROJECT REQUESTS (STUDENT) ----------------
@app.route("/request_project", methods=["GET", "POST"])
def request_project():
    if "student" not in session:
        return redirect("/student_login")
    
    if request.method == "POST":
        student_username = session["student"]
        title = request.form["title"]
        description = request.form["description"]
        problem_statement = request.form["problem_statement"]
        objectives = request.form["objectives"]
        outcomes = request.form["outcomes"]
        output_idea = request.form["output_idea"]
        
        photos = request.files.getlist("photos")
        videos = request.files.getlist("videos")

        con = sqlite3.connect("app_data.db")
        cursor = con.cursor()
        
        cursor.execute("""
            INSERT INTO project_requests(student_username, title, description, problem_statement, objectives, outcomes, output_idea)
            VALUES(?,?,?,?,?,?,?)
        """, (student_username, title, description, problem_statement, objectives, outcomes, output_idea))
        
        request_id = cursor.lastrowid
        
        # Save photos
        for photo in photos:
            if photo and photo.filename:
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                db_path = "uploads/" + filename
                cursor.execute("INSERT INTO request_photos(request_id, photo_path) VALUES(?,?)", (request_id, db_path))
                
        # Save videos
        for video in videos:
            if video and video.filename:
                filename = secure_filename(video.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video.save(video_path)
                db_path = "uploads/" + filename
                cursor.execute("INSERT INTO request_videos(request_id, video_path) VALUES(?,?)", (request_id, db_path))

        con.commit()
        con.close()
        return redirect("/my_requests")

    return render_template("request_project.html")


@app.route("/my_requests")
def my_requests():
    if "student" not in session:
        return redirect("/student_login")
    
    student_username = session["student"]
    con = sqlite3.connect("app_data.db")
    requests = con.execute("SELECT * FROM project_requests WHERE student_username=?", (student_username,)).fetchall()
    con.close()
    
    return render_template("my_requests.html", requests=requests)


@app.route("/submit_request_payment/<int:request_id>", methods=["POST"])
def submit_request_payment(request_id):
    if "student" not in session:
        return redirect("/student_login")
    
    txn_id = request.form.get("transaction_id")
    con = sqlite3.connect("app_data.db")
    con.execute("UPDATE project_requests SET transaction_id=?, status='Pending' WHERE id=?", (txn_id, request_id))
    con.commit()
    con.close()
    
    return redirect("/my_requests")


@app.route("/download_request/<int:request_id>")
def download_request(request_id):
    if "student" not in session:
        return redirect("/student_login")
    
    con = sqlite3.connect("app_data.db")
    req = con.execute("SELECT final_file, status FROM project_requests WHERE id=?", (request_id,)).fetchone()
    con.close()
    
    if req and req[1] == 'Completed' and req[0]:
        filename = req[0].replace('uploads/', '')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        return "Error: The file exists in our records but was not found on the server. Please contact support.", 404
    
    return "Access Denied: Custom request is not completed or file is missing.", 403




# ---------------- PROJECT REQUESTS (ADMIN) ----------------
@app.route("/admin_requests")
def admin_requests():
    if "admin" not in session:
        return redirect("/admin_login")
    
    con = sqlite3.connect("app_data.db")
    con.row_factory = sqlite3.Row
    requests_raw = con.execute("SELECT * FROM project_requests ORDER BY id DESC").fetchall()
    
    requests = []
    for r in requests_raw:
        req_dict = dict(r)
        photos = con.execute("SELECT photo_path FROM request_photos WHERE request_id=?", (r['id'],)).fetchall()
        videos = con.execute("SELECT video_path FROM request_videos WHERE request_id=?", (r['id'],)).fetchall()
        req_dict['photos'] = [p['photo_path'] for p in photos]
        req_dict['videos'] = [v['video_path'] for v in videos]
        requests.append(req_dict)
    
    con.close()
    return render_template("admin_requests.html", requests=requests)


@app.route("/admin_set_price/<int:request_id>", methods=["POST"])
def admin_set_price(request_id):
    if "admin" not in session:
        return redirect("/admin_login")
    
    price = request.form["price"]
    con = sqlite3.connect("app_data.db")
    con.execute("UPDATE project_requests SET price=?, status='Price Set' WHERE id=?", (price, request_id))
    con.commit()
    con.close()
    
    return redirect("/admin_requests")


@app.route("/admin_complete_request/<int:request_id>", methods=["POST"])
def admin_complete_request(request_id):
    if "admin" not in session:
        return redirect("/admin_login")
    
    final_file = request.files.get("final_file")
    if final_file and final_file.filename:
        filename = secure_filename(final_file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        final_file.save(path)
        db_path = "uploads/" + filename
        
        con = sqlite3.connect("app_data.db")
        con.execute("UPDATE project_requests SET final_file=?, status='Completed' WHERE id=?", (db_path, request_id))
        con.commit()
        con.close()
    
    return redirect("/admin_requests")


# CONFIRM PAYMENT
@app.route("/confirm_payment/<int:order_id>")
def confirm_payment(order_id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    con = sqlite3.connect("app_data.db")
    con.execute("UPDATE orders SET status='Confirmed' WHERE id=?", (order_id,))
    con.commit()
    
    return redirect("/admin_orders")


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("student", None)
    session.pop("admin", None)
    return redirect("/")


# DOWNLOAD PROJECT
@app.route("/download/<int:project_id>")

def download(project_id):
    if "student" not in session:
        return redirect("/student_login")
        
    student_username = session["student"]
    con = sqlite3.connect("app_data.db")
    
    # Check if order is confirmed
    order = con.execute("SELECT status FROM orders WHERE project_id=? AND student_username=?", 
                        (project_id, student_username)).fetchone()
    
    if order and order[0] == 'Confirmed':
        project = con.execute("SELECT project_file FROM projects WHERE id=?", (project_id,)).fetchone()
        if project and project[0]:
            filename = project[0].replace('uploads/', '')
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
            return "Error: Project file record exists but the file is missing from the server. Please notify the administrator.", 404
        return "File not found: The project file has not been uploaded for this project yet.", 404
            
    return "Access Denied: Payment not confirmed or project not found.", 403

# ---------------- CHAT SYSTEM ----------------
@app.route("/send_message/<int:request_id>", methods=["POST"])
def send_message(request_id):
    if "student" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401
    
    sender = session.get("student") if "student" in session else "Admin"
    message = request.json.get("message")
    
    if not message:
        return {"error": "Empty message"}, 400
        
    con = sqlite3.connect("app_data.db")
    con.execute("INSERT INTO request_messages(request_id, sender, message) VALUES(?,?,?)",
                (request_id, sender, message))
    con.commit()
    con.close()
    return {"status": "success"}

@app.route("/get_messages/<int:request_id>")
def get_messages(request_id):
    if "student" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401
        
    con = sqlite3.connect("app_data.db")
    con.row_factory = sqlite3.Row
    messages = con.execute("SELECT * FROM request_messages WHERE request_id=? ORDER BY timestamp ASC",
                           (request_id,)).fetchall()
    con.close()
    
    return {"messages": [dict(m) for m in messages]}


@app.route("/get_order_messages/<int:order_id>")
def get_order_messages(order_id):
    if "student" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401
        
    con = sqlite3.connect("app_data.db")
    con.row_factory = sqlite3.Row
    messages = con.execute("SELECT * FROM order_messages WHERE order_id=? ORDER BY timestamp ASC",
                           (order_id,)).fetchall()
    con.close()
    
    return {"messages": [dict(m) for m in messages]}

@app.route("/send_order_message/<int:order_id>", methods=["POST"])
def send_order_message(order_id):
    if "student" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401
    
    sender = session.get("student") if "student" in session else "Admin"
    message = request.json.get("message")
    
    if not message:
        return {"error": "Empty message"}, 400
        
    con = sqlite3.connect("app_data.db")
    con.execute("INSERT INTO order_messages(order_id, sender, message) VALUES(?,?,?)",
                (order_id, sender, message))
    con.commit()
    con.close()
    return {"status": "success"}


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

