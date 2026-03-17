from flask import Flask, render_template, redirect, url_for, flash
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forms import LoginForm, RegisterForm, CourseForm, TeacherForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "showcase-only-secret-key"

class DummyUser:
    is_authenticated = False
    role = "guest"
    full_name = "Mehmon"
    id = 0

@app.context_processor
def inject_user():
    return dict(current_user=DummyUser())

courses_data = [
    {
        "id": 1, 
        "title": "Python dasturlash", 
        "price": 1200000, 
        "duration": "3 oy", 
        "image_url": "images/python.png", 
        "description": "Noldan professional darajagacha Python o'rganing. Telegram botlar va backend asoslari."
    },
    {
        "id": 2, 
        "title": "Frontend Development", 
        "price": 1500000, 
        "duration": "4 oy", 
        "image_url": "images/frontend.png", 
        "description": "HTML, CSS, JavaScript va React yordamida zamonaviy veb-saytlar yaratishni o'rganing."
    },
    {
        "id": 3, 
        "title": "Grafik Dizayn", 
        "price": 1000000, 
        "duration": "3 oy", 
        "image_url": "images/design.png", 
        "description": "Photoshop, Illustrator va Figma yordamida professional dizayner bo'ling."
    },
    {
        "id": 4, 
        "title": "IELTS Preparation", 
        "price": 800000, 
        "duration": "2 oy", 
        "image_url": "images/ielts.png", 
        "description": "IELTS imtihoniga tayyorgarlik va kerakli bandni olish uchun intensiv kurs."
    },
    {
        "id": 5, 
        "title": "Mobil Dasturlash (Flutter)", 
        "price": 1800000, 
        "duration": "5 oy", 
        "image_url": "images/flutter.png", 
        "description": "Android va iOS uchun yagona kod bazasida ilovalar yaratish."
    },
]

teachers_data = [
    {"id": 1, "full_name": "Abduvosid Toshpo'latov", "subject": "Python & Backend", "image_url": None},
    {"id": 2, "full_name": "Dilshodbek Islomov", "subject": "Frontend Developer", "image_url": None},
    {"id": 3, "full_name": "Madina Aliyeva", "subject": "Grafik Dizayn", "image_url": None},
    {"id": 4, "full_name": "John Doe", "subject": "English / IELTS Expert", "image_url": None},
]

@app.route("/")
def index():
    return render_template("index.html", courses=courses_data[:6], teachers=teachers_data[:4])

@app.route("/courses")
def courses():
    return render_template("courses.html", courses=courses_data)

@app.route("/teachers")
def teachers():
    return render_template("teachers.html", teachers=teachers_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Sayt hozirda faqat ko'rgazma (demo) rejimida ishlaganligi sababli, tizimga kirish o'chirilgan.", "info")
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Sayt hozirda faqat ko'rgazma (demo) rejimida ishlaganligi sababli, ro'yxatdan o'tish o'chirilgan.", "info")
    return render_template("register.html", form=form)

@app.route("/enroll/<int:course_id>")
def enroll(course_id):
    flash("Sayt hozirda faqat ko'rgazma (demo) rejimida. Kurslarga yozilish tez kunda ishga tushadi!", "info")
    return redirect(url_for("courses"))

@app.route("/profile")
@app.route("/logout")
@app.route("/admin")
@app.route("/admin/courses")
@app.route("/admin/students")
@app.route("/admin/teachers")
def disabled_routes():
    flash("Sayt hozirda faqat ko'rgazma rejimida (demo). Bu sahifa vaqtinchalik yopiq.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
