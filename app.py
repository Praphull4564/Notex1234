from flask import Flask, render_template, redirect, url_for, flash, request
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import AppointmentForm, LoginForm, RegistrationForm
from models import User, Appointment, mongo
from datetime import datetime, timedelta
import traceback
from urllib.parse import unquote
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from googlemapss import generate_maps_link

app = Flask(__name__)
app.config.from_object('config.Config')

# Add these configurations after other app.config settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize MongoDB first
mongo.init_app(app)

# Then initialize other extensions
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'

# Service Definitions
AADHAR_SERVICES = {
    "Enrollment & Issuance": [
        "New Aadhaar Enrollment",
        "Aadhaar Reprint-Duplicate",
        "e-Aadhaar Download",
        "Aadhaar PVC Card"
    ],
    "Update & Correction": [
        "Name Update",
        "Date of Birth Update",
        "Gender Update",
        "Address Change",
        "Mobile Number Update",
        "Email ID Update",
        "Photo Update",
        "Biometric Update"
    ],
    "Verification & Authentication": [
        "Aadhaar Number Verification",
        "Biometric Lock-Unlock",
        "OTP Authentication",
        "Offline Verification",
        "Paperless e-KYC"
    ],
    "Linking Services": [
        "Link with PAN",
        "Link with Bank Account",
        "Link with Mobile Number",
        "Link with EPF Account",
        "Link with LPG Subsidy",
        "Link with Ration Card"
    ]
}

PAN_SERVICES = {
    "Application & Issuance": [
        "New PAN Card Application",
        "Reprint-Duplicate PAN Card",
        "e-PAN Card Download"
    ],
    "Updates & Corrections": [
        "Name-DOB Change",
        "Address Change",
        "Photo & Signature Update",
        "Correction of PAN Details"
    ],
    "Linking Services": [
        "Link PAN with Aadhaar",
        "Link PAN with Bank Account",
        "Link PAN with Demat Account",
        "Link PAN with EPF"
    ],
    "Business Services": [
        "PAN for Companies",
        "PAN for LLPs & Firms",
        "PAN for Trusts & NGOs",
        "PAN for Foreign Companies"
    ]
}

EXAM_CENTER_SERVICES = {
    "Exam Center Services": [
        "Find Exam Center",
        "Upload New Admit Card",
        "View My Admit Cards"
    ],
    "Additional Services": [
        "Download Saved Admit Card",
        "Update Exam Center",
        "View Travel History"
    ]
}

@login_manager.user_loader
def load_user(user_id):
    try:
        # Try to convert the user_id to ObjectId
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    except:
        # If conversion fails or any other error occurs, return None
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists - this will also test the connection
            existing_email = mongo.db.users.find_one({'email': form.email.data})
            if existing_email:
                flash('Email already registered. Please login instead.', 'warning')
                return redirect(url_for('login'))
            
            existing_phone = mongo.db.users.find_one({'phone': form.phone.data})
            if existing_phone:
                flash('Phone number already registered.', 'warning')
                return redirect(url_for('register'))

            # Create new user
            hashed_password = generate_password_hash(form.password.data)
            user_data = User.create_user(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=hashed_password
            )
            
            # Insert user and check result
            result = mongo.db.users.insert_one(user_data)
            if result.inserted_id:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                raise Exception("Failed to insert user")
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_data = mongo.db.users.find_one({'email': form.email.data})
            if user_data and check_password_hash(user_data['password'], form.password.data):
                user = User(user_data)
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/'):
                    next_page = None
                return redirect(next_page or url_for('index'))
            else:
                if not user_data:
                    flash('No account found with that email.', 'danger')
                else:
                    flash('Incorrect password.', 'danger')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/aadhar_services')
def aadhar_services():
    return render_template('aadhar_services.html', aadhar_services=AADHAR_SERVICES)

@app.route('/pan_services')
def pan_services():
    return render_template('pan_services.html', pan_services=PAN_SERVICES)

@app.route('/exam_center_services')
def exam_center_services():
    return render_template('exam_center_services.html', exam_center_services=EXAM_CENTER_SERVICES)

@app.route('/book_appointment/<service_type>/<service_name>', methods=['GET', 'POST'])
@login_required
def book_appointment(service_type, service_name):
    try:
        service_name = unquote(service_name)
        
        if service_type not in ['Aadhaar', 'PAN']:
            flash('Invalid service type.', 'danger')
            return redirect(url_for('index'))
        
        services_dict = AADHAR_SERVICES if service_type == 'Aadhaar' else PAN_SERVICES
        valid_services = [
            service 
            for category in services_dict.values() 
            for service in category
        ]
        
        if service_name not in valid_services:
            flash(f'Invalid service selected: {service_name}', 'danger')
            return redirect(url_for('index'))
        
        form = AppointmentForm()
        today = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
        if form.validate_on_submit():
            try:
                appointment_data = Appointment.create_appointment(
                    user_id=current_user.id,
                    service_type=service_type,
                    specific_service=service_name,
                    appointment_date=form.appointment_date.data,
                    notes=form.notes.data
                )
                mongo.db.appointments.insert_one(appointment_data)

                # Send confirmation emails
                try:
                    # Email to user
                    user_msg = Message(
                        subject='Appointment Request Received - Notex',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[current_user.email]
                    )
                    user_msg.body = f"""
Dear {current_user.name},

Thank you for booking an appointment with Notex. Your appointment request has been received:

Service Details:
---------------
Service Type: {service_type}
Service: {service_name}
Requested Date: {form.appointment_date.data.strftime('%d %B %Y, %I:%M %p')}

Our team will review your request and contact you shortly on your registered phone number ({current_user.phone}) to confirm the appointment time and provide further instructions.

Additional Notes: {form.notes.data if form.notes.data else 'None'}

Please keep this email for your reference.

Best regards,
Team Notex
"""
                    mail.send(user_msg)

                    # Email to admin
                    admin_msg = Message(
                        subject=f'New Appointment Request - {service_name}',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[app.config['MAIL_USERNAME']]  # Send to admin email
                    )
                    admin_msg.body = f"""
New Appointment Request Details:
------------------------------
Customer Name: {current_user.name}
Phone: {current_user.phone}
Email: {current_user.email}

Service Type: {service_type}
Service: {service_name}
Requested Date: {form.appointment_date.data.strftime('%d %B %Y, %I:%M %p')}

Additional Notes: {form.notes.data if form.notes.data else 'None'}

Please review and contact the customer to confirm the appointment.
"""
                    mail.send(admin_msg)
                    
                    print(f"Confirmation emails sent to {current_user.email} and admin")
                    flash('Appointment request received! We will contact you shortly to confirm the time.', 'success')
                    
                except Exception as e:
                    print(f"Email sending failed: {str(e)}")
                    print(traceback.format_exc())
                    flash('Appointment booked successfully! (Email notification failed)', 'warning')

                return redirect(url_for('index'))
            
            except Exception as e:
                print(f"Appointment booking error: {str(e)}")
                flash('An error occurred while booking your appointment. Please try again.', 'danger')
        
        return render_template('book_appointment.html', 
                             form=form, 
                             service_type=service_type, 
                             service_name=service_name,
                             today=today)
    
    except Exception as e:
        print(f"Error in book_appointment: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    appointments = list(mongo.db.appointments.aggregate([
        {
            '$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }
        },
        {
            '$unwind': '$user'
        }
    ]))
    
    return render_template('admin_dashboard.html', appointments=appointments)

@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            subject='Test Email from Notex',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]  # Send to yourself
        )
        msg.body = "This is a test email from Notex application."
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Email sending failed: {str(e)}\n{traceback.format_exc()}'

@app.cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    with app.app_context():
        if not mongo.db.users.find_one({'email': 'admin@notex.com'}):
            admin_user = User.create_user(
                name="Admin",
                email="admin@notex.com",
                phone="0000000000",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            try:
                mongo.db.users.insert_one(admin_user)
                print("Admin user created successfully!")
            except Exception as e:
                print(f"Error creating admin user: {e}")

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return redirect(url_for('index'))
    
    results = []
    
    # Search in Aadhaar services
    for category, services in AADHAR_SERVICES.items():
        for service in services:
            if query in service.lower():
                results.append({
                    'type': 'Aadhaar',
                    'category': category,
                    'service': service
                })
    
    # Search in PAN services
    for category, services in PAN_SERVICES.items():
        for service in services:
            if query in service.lower():
                results.append({
                    'type': 'PAN',
                    'category': category,
                    'service': service
                })
    
    # Add Exam Center services to search
    for category, services in EXAM_CENTER_SERVICES.items():
        for service in services:
            if query in service.lower():
                results.append({
                    'type': 'Exam Center',
                    'category': category,
                    'service': service,
                    'url': url_for('book_exam_center', service_name=service)
                })
    
    return render_template('search_results.html', 
                         results=results, 
                         query=query)

@app.route('/book_exam_center/<service_name>', methods=['GET', 'POST'])
@login_required
def book_exam_center(service_name):
    try:
        service_name = unquote(service_name)
        valid_services = [
            service 
            for category in EXAM_CENTER_SERVICES.values() 
            for service in category
        ]
        
        if service_name not in valid_services:
            flash(f'Invalid service selected: {service_name}', 'danger')
            return redirect(url_for('exam_center_services'))
        
        if service_name == "Find Exam Center":
            # Check if user has uploaded any admit card
            admit_cards = list(mongo.db.admit_cards.find({'user_id': current_user.id}))
            if not admit_cards:
                flash('Please upload your admit card first before getting directions.', 'warning')
                return redirect(url_for('book_exam_center', service_name='Upload New Admit Card'))
            return render_template('enter_exam_address.html', 
                                 service_name=service_name,
                                 service_type="Exam Center")
        
        elif service_name == "Upload New Admit Card":
            return render_template('upload_admit_card.html', 
                                 service_name=service_name,
                                 service_type="Exam Center")
        
        elif service_name == "View My Admit Cards":
            admit_cards = list(mongo.db.admit_cards.find({'user_id': current_user.id}))
            return render_template('view_admit_cards.html', 
                                 admit_cards=admit_cards,
                                 service_type="Exam Center")
    
    except Exception as e:
        print(f"Error in book_exam_center: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('exam_center_services'))

@app.route('/upload-admit-card', methods=['POST'])
@login_required
def upload_admit_card():
    if 'admit_card' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('book_exam_center', service_name='Upload New Admit Card'))
    
    file = request.files['admit_card']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('book_exam_center', service_name='Upload New Admit Card'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Store file info in MongoDB
    admit_card_doc = {
        'filename': filename,
        'file_path': file_path,
        'user_id': current_user.id,
        'upload_date': datetime.now()
    }
    mongo.db.admit_cards.insert_one(admit_card_doc)
    
    flash('Admit card uploaded successfully! Now enter your exam center address.', 'success')
    return redirect(url_for('book_exam_center', service_name='Find Exam Center'))

@app.route('/get-exam-directions', methods=['POST'])
@login_required
def get_exam_directions():
    try:
        # Verify user has an admit card
        admit_cards = list(mongo.db.admit_cards.find({'user_id': current_user.id}))
        if not admit_cards:
            flash('Please upload your admit card first before getting directions.', 'warning')
            return redirect(url_for('book_exam_center', service_name='Upload New Admit Card'))
        

        starting_address = request.form.get('starting_address')
        address = request.form.get('address')
        if not address:
            flash('Address is required', 'danger')
            return redirect(url_for('book_exam_center', service_name='Find Exam Center'))
        
        maps_link = generate_maps_link(starting_address,address)
        if not maps_link:
            flash('Could not generate directions. Please try again.', 'warning')
            return redirect(url_for('book_exam_center', service_name='Find Exam Center'))
        
        return render_template('show_exam_directions.html', 
                             maps_link=maps_link,
                             service_type="Exam Center",
                             admit_cards=admit_cards)
    except Exception as e:
        print(f"Error generating directions: {str(e)}")
        flash('An error occurred while generating directions. Please try again.', 'danger')
        return redirect(url_for('book_exam_center', service_name='Find Exam Center'))

@app.route('/process_location', methods=['POST'])
def process_location():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    manual_address = request.form.get('manual_address')
    
    # Use either the coordinates or manual address based on what was provided
    start_location = manual_address if not latitude else f"{latitude},{longitude}"
    
    # Continue with your existing logic for directions
    return redirect(url_for('show_directions', start=start_location))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
