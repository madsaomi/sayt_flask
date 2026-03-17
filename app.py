from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forms import LoginForm, RegisterForm, CourseForm, TeacherForm
from models import db, User, Course, Teacher, Enrollment

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/edu_center.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Iltimos, tizimga kiring"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Decorators ──────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Bu sahifaga kirish uchun admin huquqi kerak", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ── Public routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    courses = Course.query.limit(6).all()
    teachers = Teacher.query.limit(4).all()
    return render_template("index.html", courses=courses, teachers=teachers)


@app.route("/courses")
def courses():
    all_courses = Course.query.all()
    return render_template("courses.html", courses=all_courses)


@app.route("/teachers")
def teachers():
    all_teachers = Teacher.query.all()
    return render_template("teachers.html", teachers=all_teachers)


# ── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            full_name=form.full_name.data,
            phone=form.phone.data,
            password=hashed_pw,
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        flash("Muvaffaqiyatli ro'yxatdan o'tdingiz! Tizimga kiring.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"Xush kelibsiz, {user.full_name}!", "success")
            return redirect(next_page or url_for("profile"))
        flash("Telefon yoki parol noto'g'ri", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Tizimdan chiqdingiz", "info")
    return redirect(url_for("index"))


# ── Student routes ───────────────────────────────────────────────────────────

@app.route("/profile")
@login_required
def profile():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", enrollments=enrollments)


@app.route("/enroll/<int:course_id>")
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()
    if existing:
        flash(f"Siz '{course.title}' kursiga allaqachon yozilgansiz", "warning")
    else:
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f"'{course.title}' kursiga muvaffaqiyatli yozildingiz!", "success")
    return redirect(url_for("courses"))


# ── Admin routes ─────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    stats = {
        "users": User.query.filter_by(role="student").count(),
        "courses": Course.query.count(),
        "teachers": Teacher.query.count(),
        "enrollments": Enrollment.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@app.route("/admin/courses", methods=["GET"])
@login_required
@admin_required
def admin_courses():
    all_courses = Course.query.all()
    form = CourseForm()
    return render_template("admin/courses.html", courses=all_courses, form=form)


@app.route("/admin/courses/add", methods=["POST"])
@login_required
@admin_required
def admin_add_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
        )
        db.session.add(course)
        db.session.commit()
        flash("Kurs muvaffaqiyatli qo'shildi!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for("admin_courses"))


@app.route("/admin/courses/delete/<int:course_id>")
@login_required
@admin_required
def admin_delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash(f"'{course.title}' kursi o'chirildi", "success")
    return redirect(url_for("admin_courses"))


@app.route("/admin/students")
@login_required
@admin_required
def admin_students():
    students = User.query.filter_by(role="student").all()
    return render_template("admin/students.html", students=students)


@app.route("/admin/teachers", methods=["GET"])
@login_required
@admin_required
def admin_teachers():
    all_teachers = Teacher.query.all()
    form = TeacherForm()
    return render_template("admin/teachers.html", teachers=all_teachers, form=form)


@app.route("/admin/teachers/add", methods=["POST"])
@login_required
@admin_required
def admin_add_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(full_name=form.full_name.data, subject=form.subject.data)
        db.session.add(teacher)
        db.session.commit()
        flash("O'qituvchi qo'shildi!", "success")
    return redirect(url_for("admin_teachers"))


@app.route("/admin/teachers/delete/<int:teacher_id>")
@login_required
@admin_required
def admin_delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash(f"'{teacher.full_name}' o'chirildi", "success")
    return redirect(url_for("admin_teachers"))


def seed_data():
    """Boshlang'ich demo ma'lumotlarni qo'shish."""
    # Kurslar
    if not Course.query.first():
        demo_courses = [
            Course(title="Python dasturlash", price=1200000, duration="3 oy", 
                   image_url="images/python.png",
                   description="Noldan professional darajagacha Python o'rganing. Telegram botlar va backend asoslari."),
            Course(title="Frontend Development", price=1500000, duration="4 oy", 
                   image_url="images/frontend.png",
                   description="HTML, CSS, JavaScript va React yordamida zamonaviy veb-saytlar yaratishni o'rganing."),
            Course(title="Grafik Dizayn", price=1000000, duration="3 oy", 
                   image_url="images/design.png",
                   description="Photoshop, Illustrator va Figma yordamida professional dizayner bo'ling."),
            Course(title="IELTS Preparation", price=800000, duration="2 oy", 
                   image_url="images/ielts.png",
                   description="IELTS imtihoniga tayyorgarlik va kerakli bandni olish uchun intensiv kurs."),
            Course(title="Mobil Dasturlash (Flutter)", price=1800000, duration="5 oy", 
                   image_url="images/flutter.png",
                   description="Android va iOS uchun yagona kod bazasida ilovalar yaratish."),
        ]
        db.session.add_all(demo_courses)
        print("Success: Demo courses created")

    # O'qituvchilar
    if not Teacher.query.first():
        demo_teachers = [
            Teacher(full_name="Abduvosid Toshpo'latov", subject="Python & Backend", image_url=None),
            Teacher(full_name="Dilshodbek Islomov", subject="Frontend Developer", image_url=None),
            Teacher(full_name="Madina Aliyeva", subject="Grafik Dizayn", image_url=None),
            Teacher(full_name="John Doe", subject="English / IELTS Expert", image_url=None),
        ]
        db.session.add_all(demo_teachers)
        print("Success: Demo teachers created")
    
    db.session.commit()


# ── Init ─────────────────────────────────────────────────────────────────────

@app.before_request
def initialize_database():
    app.before_request_funcs[None].remove(initialize_database)
    
    db.create_all()
    # Admin
    if not User.query.filter_by(role="admin").first():
        admin = User(
            full_name="Admin",
            phone="admin",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Success: Admin created -> phone: admin | password: admin123")
    
    # Seed
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
