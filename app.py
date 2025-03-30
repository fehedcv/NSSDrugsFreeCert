import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load Firebase credentials from environment variables
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')  # Landing page with "Take Pledge" button

@app.route('/pledge')
def pledge_form():
    return render_template('pledge.html')  # Pledge form page

@app.route('/submit_pledge', methods=['POST'])
def submit_pledge():
    try:
        data = request.json
        db.collection('pledges').add(data)
        return jsonify({"success": True, "message": "Pledge submitted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
