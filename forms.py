from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', 
                      validators=[DataRequired(message="Name is required"), 
                                Length(min=2, max=100, message="Name must be between 2 and 100 characters")])
    email = StringField('Email', 
                       validators=[DataRequired(message="Email is required"), 
                                 Email(message="Please enter a valid email address")])
    phone = StringField('Phone Number', 
                       validators=[DataRequired(message="Phone number is required"), 
                                 Length(min=10, max=15, message="Phone number must be between 10 and 15 digits")])
    password = PasswordField('Password', 
                           validators=[DataRequired(message="Password is required"), 
                                     Length(min=6, message="Password must be at least 6 characters")])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(message="Please confirm your password"), 
                                             EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AppointmentForm(FlaskForm):
    appointment_date = DateTimeField('Appointment Date and Time', 
                                   format='%Y-%m-%dT%H:%M',
                                   validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Book Appointment')
