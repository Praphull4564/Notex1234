from flask import Flask, render_template
from models import db, Appointment

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

@app.route('/admin_dashboard')
def admin_dashboard():
    appointments = Appointment.query.all()
    return render_template('admin_dashboard.html', appointments=appointments)
