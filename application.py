from flask import Flask, render_template, request, session, redirect, flash, url_for
from werkzeug.utils import secure_filename
from flask_session import Session
import sqlite3
import os
from hashlib import md5

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOUD_FOLDER"] = "./static/img"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000
Session(app)

DATABASE_NAME = "freeMarket.db"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route("/", methods=["GET", "POST"])
def index():
    
    # Verifying if user is loged
    if not session.get("userId"):
        return redirect("/login")

    # Logout 
    if request.method == "POST":
        # forget the current session
        session.clear()
        return redirect("/login")

    cnn = sqlite3.connect(DATABASE_NAME)
    cursor = cnn.cursor()

    posts = cursor.execute(
    """
    SELECT posts.id as id, extension, title, description, price
    FROM users JOIN posts ON users.id = posts.userId 
    WHERE users.id = ?
    """, [session.get("userId")]).fetchall()
    
    return render_template("/index.html", username=session["userId"], posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cnn = sqlite3.connect(DATABASE_NAME)

        username = request.form.get("username")
        password = request.form.get("password")

        # Checking usename fild was submited
        if not username:
            return render_template("error.html", error="Username must be provided")

        # Checking password fild was submited
        if not password:
            return render_template("error.html", error="Password must be provided")

        # Evalueting credentials
        hash = md5(b"{password}").hexdigest()
        user = cnn.execute("SELECT * FROM users WHERE username = ? AND hash = ?", [username, hash]).fetchall()

        if len(user) == 0:
            return render_template("error.html", error="Username or password incorrect")
 
        session["userId"] = user[0][0]

        return redirect("/")
    
    return render_template("/login.html")
        

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # Establishing a connection with the data base
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        users = conn.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()

        # Checking username
        if len(users) > 0:
            return render_template("error.html", error="Username is already selected")
        
        # Checking passwords
        if password != confirmation:
            return render_template("error.html", error="Password must match")
        
        # Confirme registration
        hash = md5(b"{password}").hexdigest()
        cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)", [username, hash])
    
        conn.commit()

        return redirect("/")
        
    return render_template("/register.html")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS;

@app.route("/post", methods=["GET", "POST"])
def post():
    if request.method == "POST":

        if "file" not in request.files:
            flash("Not file")
            return redirect(request.url)

        # Access file
        file = request.files["file"]

        # Checking file name 
        if file.filename == '':
            flash("File was not selected")
            return redirect(request.url)

        # Storing the file 
        if file and allowed_file(file.filename):
            
            cnn = sqlite3.connect(DATABASE_NAME)
            cursor = cnn.cursor()

            # Post data
            title = request.form.get("title")
            description = request.form.get("description")
            price = request.form.get("price")
            userId = session.get("userId")
            extension = file.filename.rsplit(".", 1)[1]

            cursor.execute("""
            INSERT INTO posts (title, description, price, extension, userId) 
            VALUES (?, ?, ?, ?, ?)
            """, [title, description, price, extension, userId])

            filename = f"{cursor.lastrowid}.{extension}"
            file.save(os.path.join(app.config["UPLOUD_FOLDER"], filename))

            cnn.commit()

        
    return render_template("/post.html")

