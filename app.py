from flask import Flask, render_template, request, jsonify
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pledges')
def pledge():
    return render_template('pledge.html')


@app.route('/submit_pledge', methods=['POST'])
def submit_pledge():
    data = request.json
    doc_ref = db.collection('pledges').add(data)  # Store in Firestore
    return jsonify({"success": True, "message": "Pledge submitted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
