from flask import Flask, request, redirect, session, render_template_string, abort
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

app.secret_key = "6da192a6dd56e3843fc34e5336dad8f7042f212ebbb09b4449d7fa1464e76726"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///theory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"


class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    public = db.Column(db.Boolean, default=True)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("login"):
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    theories = Theory.query.filter_by(public=True).order_by(Theory.id.desc()).all()

    return render_template_string("""
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Theory Website</title>
<meta name="description" content="Study, Science और Education Theory Website">
<meta name="robots" content="index, follow">
<style>
body{font-family:Arial;background:#f5f7fa;margin:0}
header{background:#222;color:white;padding:25px;text-align:center}
.container{max-width:850px;margin:auto;padding:20px}
.card{background:white;padding:20px;margin-bottom:20px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
.read{display:inline-block;background:#222;color:white;padding:10px 16px;border-radius:6px;text-decoration:none}
.admin{display:block;text-align:center;margin-top:30px}
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
<p>Theory पढ़ने के लिए नीचे क्लिक करें।</p>
<a class="read" href="/theory/{{ theory.id }}">Read Theory</a>
</div>
{% endfor %}
{% else %}
<div class="card">
<h2>Welcome</h2>
<p>अभी कोई public theory publish नहीं हुई है।</p>
</div>
{% endif %}

<a class="admin" href="/login">Admin Login</a>

</div>
</body>
</html>
""", theories=theories)


@app.route("/theory/<int:id>")
def theory_page(id):
    theory = Theory.query.get_or_404(id)

    if not theory.public:
        abort(404)

    return render_template_string("""
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ theory.title }} - My Theory Website</title>
<meta name="description" content="{{ theory.content[:155] }}">
<meta name="robots" content="index, follow">
<style>
body{font-family:Arial;background:#f5f7fa;margin:0}
.container{max-width:850px;margin:30px auto;padding:20px}
.article{background:white;padding:25px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.1)}
.content{white-space:pre-wrap;line-height:1.8;font-size:17px}
.back{text-decoration:none}
</style>
</head>
<body>
<div class="container">
<a class="back" href="/">← Home</a>
<div class="article">
<h1>{{ theory.title }}</h1>
<div class="content">{{ theory.content }}</div>
</div>
</div>
</body>
</html>
""", theory=theory)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["login"] = True
            return redirect("/admin")

        error = "Username या password गलत है।"

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Admin Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f2f4f7}
.box{max-width:400px;margin:100px auto;background:white;padding:25px;border-radius:12px}
input{width:100%;padding:12px;margin:8px 0;box-sizing:border-box}
button{width:100%;padding:12px;background:#222;color:white;border:0;border-radius:6px}
.error{color:red}
</style>
</head>
<body>
<div class="box">
<h2>Admin Login</h2>
{% if error %}<p class="error">{{ error }}</p>{% endif %}
<form method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
</div>
</body>
</html>
""", error=error)


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
body{font-family:Arial;background:#f5f5f5;margin:0}
.container{max-width:850px;margin:auto;padding:20px}
.box{background:white;padding:20px;margin-bottom:20px;border-radius:12px}
input,textarea,select{width:100%;padding:12px;margin:8px 0;box-sizing:border-box}
button{background:#222;color:white;border:0;padding:12px 20px;border-radius:6px}
.delete{background:#d00000}
.public{color:green;font-weight:bold}
.private{color:red;font-weight:bold}
</style>
</head>
<body>

<div class="container">

<h1>Admin Panel</h1>

<div class="box">
<h2>Nayi Theory Add Karo</h2>

<form action="/add" method="post">

<label>Title</label>
<input name="title" placeholder="Theory ka title" required>

<label>Theory</label>
<textarea name="content" rows="14" placeholder="Yahan theory likho..." required></textarea>

<label>Visibility</label>
<select name="public">
<option value="1">Public - Google par aa sakti hai</option>
<option value="0">Private - Sirf Admin Panel me</option>
</select>

<br><br>
<button type="submit">Save Theory</button>
</form>
</div>

<div class="box">
<h2>All Theories</h2>

{% for theory in theories %}
<div>
<h3>{{ theory.title }}</h3>

{% if theory.public %}
<p class="public">PUBLIC</p>
<a href="/theory/{{ theory.id }}">Public Page Dekho</a>
{% else %}
<p class="private">PRIVATE</p>
{% endif %}

<p>{{ theory.content }}</p>

<form action="/delete/{{ theory.id }}" method="post">
<button class="delete" type="submit">Delete</button>
</form>

<hr>
</div>

{% else %}
<p>Abhi koi theory nahi hai.</p>
{% endfor %}

</div>

<a href="/logout">Logout</a>
<br><br>
<a href="/">Public Website</a>

</div>
</body>
</html>
""", theories=theories)


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title")
    content = request.form.get("content")
    public = request.form.get("public") == "1"

    if title and content:
        theory = Theory(title=title, content=content, public=public)
        db.session.add(theory)
        db.session.commit()

    return redirect("/admin")


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    theory = Theory.query.get_or_404(id)

    db.session.delete(theory)
    db.session.commit()

    return redirect("/admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/robots.txt")
def robots():
    return """User-agent: *
Allow: /

Sitemap: /sitemap.xml
""", 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    theories = Theory.query.filter_by(public=True).all()

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>/</loc></url>
"""

    for theory in theories:
        xml += f"""
<url>
<loc>/theory/{theory.id}</loc>
</url>
"""

    xml += "</urlset>"

    return xml, 200, {"Content-Type": "application/xml"}


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
