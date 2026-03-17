from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RegisterForm(FlaskForm):
    full_name = StringField("Ism Familiya", validators=[DataRequired(), Length(2, 100)])
    phone = StringField("Telefon raqam", validators=[DataRequired()])
    password = PasswordField("Parol", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Parolni tasdiqlang",
                            validators=[DataRequired(), EqualTo("password", message="Parollar mos emas")])
    submit = SubmitField("Ro'yxatdan o'tish")


class LoginForm(FlaskForm):
    phone = StringField("Telefon raqam", validators=[DataRequired()])
    password = PasswordField("Parol", validators=[DataRequired()])
    submit = SubmitField("Kirish")


class CourseForm(FlaskForm):
    title = StringField("Kurs nomi", validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField("Tavsif")
    price = FloatField("Narxi (so'm)", default=0)
    duration = StringField("Davomiyligi (masalan: 3 oy)")
    submit = SubmitField("Saqlash")


class TeacherForm(FlaskForm):
    full_name = StringField("Ism Familiya", validators=[DataRequired(), Length(2, 100)])
    subject = StringField("Fan / Yo'nalish", validators=[DataRequired()])
    submit = SubmitField("Saqlash")
