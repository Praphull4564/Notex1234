import os



class Config:
    SECRET_KEY = 'NotexWebsite'
    
    # MongoDB Settings
    MONGO_URI = 'mongodb+srv://notex4564:notex123456@notex.2pwmr.mongodb.net/notex_db?retryWrites=true&w=majority&appName=Notex'
    MONGO_DBNAME = 'notex_db'
    
    # Email Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'notex4564@gmail.com'
    MAIL_PASSWORD = 'fycafgwfhxpkdcfn'
    MAIL_DEFAULT_SENDER = 'notex4564@gmail.com'
    MAIL_MAX_EMAILS = 5
    MAIL_ASCII_ATTACHMENTS = False

