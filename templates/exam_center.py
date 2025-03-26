from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from googlemapss import generate_maps_link

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['exam_center_db']
admit_cards = db['admit_cards']

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/exam-center', methods=['GET'])
def exam_center():
    return render_template('upload_admit_card.html')

@app.route('/upload-admit-card', methods=['POST'])
def upload_admit_card():
    if 'admit_card' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['admit_card']
    if file.filename == '':
        return 'No file selected', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Store file info in MongoDB
    admit_card_doc = {
        'filename': filename,
        'file_path': file_path,
        'user_id': request.form.get('user_id', 'anonymous')  # You might want to add user authentication
    }
    admit_cards.insert_one(admit_card_doc)
    
    return redirect(url_for('enter_address'))

@app.route('/enter-address', methods=['GET'])
def enter_address():
    return render_template('enter_address.html')

@app.route('/get-directions', methods=['POST'])
def get_directions():
    address = request.form.get('address')
    if not address:
        return 'Address is required', 400
    
    maps_link = generate_maps_link(address)
    return render_template('show_directions.html', maps_link=maps_link)

if __name__ == '__main__':
    app.run(debug=True) 