from app import app, mongo
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Ensure unique indexes
        mongo.db.users.create_index('email', unique=True)
        mongo.db.users.create_index('phone', unique=True)
        
        # Indexes for faster queries
        mongo.db.appointments.create_index('user_id')
        mongo.db.appointments.create_index('appointment_date')
        
        # Create admin user if it doesn't exist
        if not mongo.db.users.find_one({'email': 'admin@notex.com'}):
            admin_user = {
                'name': 'Admin',
                'email': 'admin@notex.com',
                'phone': '0000000000',
                'password': generate_password_hash('admin123'),
                'is_admin': True
            }
            mongo.db.users.insert_one(admin_user)
            print("✅ Admin user created successfully!")

if __name__ == '__main__':
    init_db()
