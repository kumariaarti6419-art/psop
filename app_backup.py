from flask import Flask, request, redirect, session, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///theory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    public = db.Column(db.Boolean, default=False)


USERNAME = "admin"
PASSWORD = "12345"


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    public_theories = Theory.query.filter_by(public=True).all()

    return render_template_string("""
    <h1>My Theory Website</h1>

    <h2>Public Theories</h2>

    {% for t in theories %}
        <h3>{{ t.title }}</h3>
        <p>{{ t.content }}</p>
        <hr>
    {% else %}
        <p>Abhi koi public theory nahi hai.</p>
    {% endfor %}

    <a href="/login">Admin Login</a>
    """, theories=public_theories)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form["username"] == USERNAME and
                request.form["password"] == PASSWORD):

            session["login"] = True
            return redirect("/admin")

        return "<h3>Username ya password galat hai.</h3>"

    return """
    <h2>Admin Login</h2>

    <form method="post">
        Username:<br>
        <input name="username"><br><br>

        Password:<br>
        <input name="password" type="password"><br><br>

        <button type="submit">Login</button>
    </form>
    """


@app.route("/admin")
def admin():
    if not session.get("login"):
        return redirect("/login")

    theories = Theory.query.all()

    return render_template_string("""
    <h1>Admin Panel</h1>

    <h2>Nayi Theory Add Karo</h2>

    <form action="/add" method="post">

        Title:<br>
        <input name="title" required><br><br>

        Theory:<br>
        <textarea name="content" rows="10" cols="40"
        required></
