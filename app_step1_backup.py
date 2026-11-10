from flask import Flask, request, redirect, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# =========================
# SETTINGS
# =========================

app.secret_key = "CHANGE_THIS_SECRET_KEY_123456"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///theory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE
# =========================

class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)


# =========================
# ADMIN LOGIN
# =========================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("login"):
            return redirect("/login")
        return func(*args, **kwargs)

    return wrapper


# =========================
# HOME - PUBLIC
# =========================

@app.route("/")
def home():

    theories = Theory.query.order_by(Theory.id.desc()).all()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>My Theory Website</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    font-family: Arial, sans-serif;
    background: #f5f7fa;
    margin: 0;
}

header {
    background: #222;
    color: white;
    padding: 20px;
    text-align: center;
}

.container {
    max-width: 800px;
    margin: 25px auto;
    padding: 15px;
}

.card {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
    margin: 0;
}

h2 {
    color: #222;
}

p {
    line-height: 1.7;
}

a {
    text-decoration: none;
}

.admin {
    display: block;
    text-align: center;
    margin-top: 30px;
}
</style>

</head>

<body>

<header>
<h1>My Theory Website</h1>
<p>Study • Theory • Knowledge</p>
</header>

<div class="container">

{% if theories %}

{% for theory in theories %}

<div class="card">

<h2>{{ theory.title }}</h2>

<p>
{{ theory.content }}
</p>

</div>

{% endfor %}

{% else %}

<div class="card">
<h2>Welcome</h2>
<p>Abhi koi theory publish nahi hui hai.</p>
</div>

{% endif %}

<a class="admin" href="/login">Admin Login</a>

</div>

</body>
</html>
""", theories=theories)


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["login"] = True

            return redirect("/admin")

        else:
            error = "Username ya password galat hai."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>

<title>Admin Login</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body {
    font-family: Arial;
    background: #f2f4f7;
}

.box {
    max-width: 400px;
    margin: 100px auto;
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,.15);
}

input {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    box-sizing: border-box;
}

button {
    width: 100%;
    padding: 12px;
    background: #222;
    color: white;
    border: 0;
    border-radius: 6px;
}

.error {
    color: red;
}

</style>

</head>

<body>

<div class="box">

<h2>Admin Login</h2>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="post">

<input
name="username"
placeholder="Username"
required>

<input
type="password"
name="password"
placeholder="Password"
required>

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>
""" , error=error)


# =========================
# ADMIN PANEL
# =========================

@app.route("/admin")
@login_required
def admin():

    theories = Theory.query.order_by(Theory.id.desc()).all()

    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<title>Admin Panel</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body {
    font-family: Arial;
    background: #f5f5f5;
    margin: 0;
}

.container {
    max-width: 800px;
    margin: auto;
    padding: 20px;
}

.box {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
}

input, textarea {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    box-sizing: border-box;
}

button {
    background: #222;
    color: white;
    border: 0;
    padding: 12px 20px;
    border-radius: 6px;
}

.delete {
    background: #d00000;
}

</style>

</head>

<body>

<div class="container">

<h1>Admin Panel</h1>

<div class="box">

<h2>Nayi Theory Add Karo</h2>

<form action="/add" method="post">

<label>Title</label>

<input
name="title"
placeholder="Theory ka title"
required>

<label>Theory</label>

<textarea
name="content"
rows="12"
placeholder="Yahan theory likho..."
required></textarea>

<button type="submit">
Publish Theory
</button>

</form>

</div>


<div class="box">

<h2>Published Theories</h2>

{% for theory in theories %}

<div>

<h3>{{ theory.title }}</h3>

<p>{{ theory.content }}</p>

<form action="/delete/{{ theory.id }}" method="post">

<button class="delete" type="submit">
Delete
</button>

</form>

<hr>

</div>

{% else %}

<p>Abhi koi theory nahi hai.</p>

{% endfor %}

</div>

<a href="/logout">Logout</a>

<br><br>

<a href="/">Public Website Dekho</a>

</div>

</body>

</html>
""", theories=theories)


# =========================
# ADD THEORY
# =========================

@app.route("/add", methods=["POST"])
@login_required
def add():

    title = request.form.get("title")
    content = request.form.get("content")

    if title and content:

        new_theory = Theory(
            title=title,
            content=content
        )

        db.session.add(new_theory)
        db.session.commit()

    return redirect("/admin")


# =========================
# DELETE THEORY
# =========================

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):

    theory = Theory.query.get_or_404(id)

    db.session.delete(theory)
    db.session.commit()

    return redirect("/admin")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# DATABASE + START
# =========================

with app.app_context():
    db.create_all()


if __name__ == "__main__":

    print("")
    print("==============================")
    print("   THEORY WEBSITE STARTED")
    print("==============================")
    print("Open: http://127.0.0.1:8000")
    print("Admin: http://127.0.0.1:8000/login")
    print("Username: admin")
    print("Password: 12345")
    print("==============================")
    print("")

    app.run(host="0.0.0.0", port=8000)
