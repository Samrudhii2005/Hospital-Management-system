from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# User Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

# User Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Appointment Booking Form (For Patients)
class AppointmentForm(FlaskForm):
    doctor_id = IntegerField('Doctor ID', validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')
