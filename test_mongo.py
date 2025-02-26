from flask import Flask
from flask_pymongo import PyMongo
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)

def test_connection():
    try:
        # The ismaster command is cheap and does not require auth.
        mongo.db.command('ismaster')
        print("✅ MongoDB connection successful!")
        
        # Test database operations
        test_doc = {'test': 'document'}
        result = mongo.db.test.insert_one(test_doc)
        print("✅ Database write successful!")
        
        mongo.db.test.delete_one({'_id': result.inserted_id})
        print("✅ Database delete successful!")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection() 

    