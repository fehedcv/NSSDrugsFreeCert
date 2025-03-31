import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import uuid

app = Flask(__name__)
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
@app.route('/download_page')
def doownload_cer():
    return render_template('download.html')

@app.route('/submit_pledge', methods=['POST'])
def submit_pledge():
    try:
        data = request.json
        db.collection('pledges').add(data)
        return jsonify({"success": True, "message": "Pledge submitted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
# Directory to save generated certificates
os.makedirs("certificates", exist_ok=True)

@app.route('/download/certificate', methods=['GET'])
def download_certificate():
    try:
        # Get the phone number from the request
        phone_number = request.args.get("PhoneNumber")
        if not phone_number:
            return jsonify({"success": False, "message": "Phone number is required"}), 400

        # Query Firestore for the phone number
        pledge_ref = db.collection('pledges').where('mobile', '==', phone_number).get()
        if not pledge_ref:
            return jsonify({"success": False, "message": "Phone number not found"}), 404

        # Retrieve user details
        user_data = pledge_ref[0].to_dict()
        name = user_data.get('name', 'User')
        unique_id = pledge_ref[0].id  # Use Firestore document ID as the unique ID
        branch = user_data.get('branch', 'Unknown Branch')
        college = user_data.get('college', 'Unknown College')

        # Open the certificate template
        font_path = os.path.join(app.root_path, 'templates/fonts/cfont.ttf')
        template_path = os.path.join(app.root_path, 'templates/cer.jpeg')
        output_dir = os.path.join(app.root_path, "public/cert")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{phone_number}_certificate.jpeg")
        img = Image.open(template_path)

        # Prepare to draw on the image
        draw = ImageDraw.Draw(img)
        font_large = ImageFont.truetype(font_path, 36)  # Font for name
        font_small = ImageFont.truetype(font_path, 28)  # Font for unique ID

        # Center the name
        bbox_name = draw.textbbox((0, 0), name, font=font_large)
        text_width_name = bbox_name[2] - bbox_name[0]
        text_height_name = bbox_name[3] - bbox_name[1]
        img_width, img_height = img.size
        x_name = (img_width - text_width_name) / 2
        y_name = img_height / 2  # Adjust Y position as necessary
        draw.text((x_name, y_name), name, fill="black", font=font_large)

        # Center the unique ID below the name
        id_text = unique_id
        bbox_id = draw.textbbox((0, 0), id_text, font=font_small)
        text_width_id = bbox_id[2] - bbox_id[0]
        x_id = (img_width - text_width_id) / 2 -330
        y_id = y_name + 290  # Place slightly below the name
        draw.text((x_id, y_id), id_text, fill="black", font=font_small)

        # Save the updated certificate
        img.save(output_path)

        # Return the certificate for download
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)


