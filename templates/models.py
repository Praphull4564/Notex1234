from flask_login import UserMixin
from datetime import datetime
from bson import ObjectId
from flask_pymongo import PyMongo

mongo = PyMongo()

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data if user_data else {}

    @property
    def id(self):
        # Convert ObjectId to string for Flask-Login
        return str(self.user_data.get('_id')) if self.user_data else None

    @property
    def name(self):
        return self.user_data.get('name')

    @property
    def email(self):
        return self.user_data.get('email')

    @property
    def phone(self):
        return self.user_data.get('phone')

    @property
    def is_admin(self):
        return self.user_data.get('is_admin', False)

    def get_id(self):
        # Required for Flask-Login
        return str(self.user_data.get('_id')) if self.user_data else None

    @staticmethod
    def create_user(name, email, phone, password, is_admin=False):
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
            'is_admin': is_admin,
            'created_at': datetime.utcnow()
        }
        return user_data

class Appointment:
    @staticmethod
    def create_appointment(user_id, service_type, specific_service, appointment_date, notes=None):
        appointment_data = {
            'user_id': ObjectId(user_id),
            'service_type': service_type,
            'specific_service': specific_service,
            'appointment_date': appointment_date,
            'status': 'Pending',
            'notes': notes,
            'created_at': datetime.utcnow()
        }
        return appointment_data
