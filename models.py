from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    enrollments = db.relationship('Enrollment', backref='user', lazy=True,
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.full_name}>'


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)
    duration = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    enrollments = db.relationship('Enrollment', backref='course', lazy=True,
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Teacher {self.full_name}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
