from flask import Flask, jsonify, request
from flask import send_file, render_template, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
from captcha.image import ImageCaptcha
import random
import string
import os

# Load .env file first
load_dotenv()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
app = Flask(__name__)
CORS(app)

current_captcha_answer = ""

# Ensure static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

# Configuration
CAPTCHA_TEXT_LENGTH = 6

"""Generates a random string of uppercase letters and digits."""
def generate_random_text():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=CAPTCHA_TEXT_LENGTH))

@app.route("/")
def index():
    # تمرير التوكن إلى القالب
    return render_template("index.html", access_token=ACCESS_TOKEN)

@app.route("/captcha", methods=["GET"])
def get_captcha():
    # تحقق من التوكن في الهيدر
    token = request.headers.get("Authorization")
    if token != ACCESS_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    global current_captcha_answer
    current_captcha_answer = generate_random_text()

    image = ImageCaptcha(width=280, height=90)
    image.write(current_captcha_answer, 'static/captcha.png')

    return jsonify({
        "status": "generated",
        "message": "New captcha image created as 'captcha.png'",
        "debug_text": current_captcha_answer
    }), 200

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route("/verify", methods=["POST"])
def verify_captcha():
    data = request.get_json()

    if not data or "captcha" not in data:
        return jsonify({"error": "Missing 'captcha' key in JSON"}), 400

    user_input = data.get("captcha").strip().upper()

    if user_input == current_captcha_answer:
        return jsonify({"status": "verified", "code": 200})
    return jsonify({"status": "failed", "reason": "Incorrect text"}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Captcha Service Running...")
    app.run(host='0.0.0.0', port=port)
    
    
    
    
    