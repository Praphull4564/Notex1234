from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from models import db, User, Appointment
from forms import AppointmentForm

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aadhar_services')
def aadhar_services():
    services = ["New Aadhaar Card", "Aadhaar Update", "Aadhaar Link to Mobile", "Address Change"]
    return render_template('aadhar_services.html', services=services)

@app.route('/pan_services')
def pan_services():
    services = ["New PAN Card", "PAN Card Update", "Reprint PAN Card"]
    return render_template('pan_services.html', services=services)

@app.route('/book_appointment/<service_type>/<service_name>', methods=['GET', 'POST'])
def book_appointment(service_type, service_name):
    form = AppointmentForm()
    form.specific_service.data = service_name

    if form.validate_on_submit():
        user = User.query.first()  # Fetch first user (Modify as needed)
        appointment = Appointment(user_id=user.id, 
                                  service_type=service_type, 
                                  specific_service=form.specific_service.data, 
                                  appointment_date=form.appointment_date.data)
        db.session.add(appointment)
        db.session.commit()

        # Send email
        msg = Message('Appointment Confirmation', sender='your_email@gmail.com', recipients=[user.email])
        msg.body = f'You have booked {appointment.specific_service} under {appointment.service_type} on {appointment.appointment_date}.'
        mail.send(msg)

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('book_appointment.html', form=form, service_type=service_type, service_name=service_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
