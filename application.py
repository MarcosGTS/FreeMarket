from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, session, redirect, flash, url_for
from werkzeug.utils import secure_filename
from flask_session import Session
import sqlite3
import os


from helper import login_required, hashing

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
    cnn = sqlite3.connect(DATABASE_NAME)
    cnn.row_factory = sqlite3.Row
    cursor = cnn.cursor()

    sql = "SELECT id, extension, title, price FROM posts"
    posts = cursor.execute(sql).fetchall()
    
    return render_template("/index.html", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cnn = sqlite3.connect(DATABASE_NAME)
        cnn.row_factory = sqlite3.Row
        cursor = cnn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")

        # Checking usename fild was submited
        if not username:
            return redirect("/error/Username must be provided")

        # Checking password fild was submited
        if not password:
            return redirect("/error/Password must be provided")

        # Evalueting credentials
        user = cnn.execute("SELECT * FROM users WHERE username = ? AND hash = ?", [username, hashing(password)]).fetchone()

        if not user:
            return redirect("/error/Username or password incorrect")
 
        session["userId"] = user["id"]

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
            return redirect("/error/Username is already selected")
        
        # Checking passwords
        if password != confirmation:
            return redirect("/error/Password must match")
        
        # Confirme registration
        hash = hashing(password)
        cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)", [username, hash])
    
        conn.commit()

        return redirect("/")
        
    return render_template("/register.html")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS;

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():

    cnn = sqlite3.connect(DATABASE_NAME)
    cnn.row_factory = sqlite3.Row
    cursor = cnn.cursor()
    
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
            
            # Post data
            title = request.form.get("title")
            description = request.form.get("description")
            price = request.form.get("price")
            userId = session.get("userId")
            extension = file.filename.rsplit(".", 1)[1]

            sql = "INSERT INTO posts (title, description, price, extension, userId) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, [title, description, price, extension, userId])

            filename = f"{cursor.lastrowid}.{extension}"
            file.save(os.path.join(app.config["UPLOUD_FOLDER"], filename))

            cnn.commit()
    
    sql = "SELECT * FROM posts WHERE userid = ?"
    posts = cursor.execute(sql, [session["userId"]]).fetchall()

    return render_template("/post.html", posts=posts)

@app.route("/remove_post", methods=["POST"])
@login_required
def remove_post():
    postId = request.form.get("id")

    cnn = sqlite3.connect(DATABASE_NAME)
    
    sql = "DELETE FROM posts WHERE id = ? AND userId = ?"
    cnn.execute(sql, [postId, session["userId"]])
    cnn.commit()

    return redirect("/post")

@app.route("/logout")
@login_required
def logout():
    # forget the current session
    session.clear()
    return redirect("/")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    cnn = sqlite3.connect(DATABASE_NAME)
    cnn.row_factory = sqlite3.Row
    cursor = cnn.cursor()

    sql = "SELECT username FROM users WHERE id = ?"
    user = cursor.execute(sql, [session["userId"]]).fetchone()

    # Changing password
    if request.method == "POST":
        
        oldPassword = request.form.get("old_password")
        newPassword = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        sql = "SELECT hash FROM users WHERE id = ? AND hash = ?"
        crrPass = cursor.execute(sql, [session["userId"], hashing(oldPassword)]).fetchone()
        # Checking password
        if not crrPass:
            return redirect("/error/Incorrect password")

        if not newPassword:
            return redirect("/error/Must have password")
        
        if not confirmation:
            return redirect("/error/Must confirm password")
        
        if newPassword != confirmation:
            return redirect("/error/Passwords must match")

        # Hashing new password
        hash = hashing(newPassword)

        # Updating password
        slq = "UPDATE users SET hash = ?"
        cursor.execute(slq, [hash])

        #Saving
        cnn.commit()

    return render_template("/account.html", username=user["username"])

@app.route("/more/<id>")
def more(id):
    cnn = sqlite3.connect(DATABASE_NAME)
    cnn.row_factory = sqlite3.Row
    cursor = cnn.cursor()

    sql = "SELECT * FROM posts JOIN users ON users.id = userId WHERE posts.id = ?"
    post = cursor.execute(sql, [id]).fetchone()
    
    filename = f"img/{post['id']}.{post['extension']}"
    filepath = url_for('static', filename=filename)

    return render_template("/more.html", post=post, filepath=filepath);

@app.route("/error/<message>")
def error(message):
    return render_template("/error.html", error=message)