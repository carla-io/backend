import os
import cv2
import pytesseract
import numpy as np
import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Fix Matplotlib GUI issue
matplotlib.use('Agg')

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract path (update this for your installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load pre-trained TensorFlow model (ensure this model exists)
try:
    model = tf.keras.models.load_model("denoise_model.h5")
    print("✅ TensorFlow model loaded successfully.")
except Exception as e:
    print(f"⚠️ Error loading TensorFlow model: {e}")
    model = None

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  

    # Remove noise
    gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

    # Adaptive threshold instead of Otsu's
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return processed


def extract_text(image_path):
    img = cv2.imread(image_path)
    processed_img = preprocess_image(img)

    debug_path = os.path.join(UPLOAD_FOLDER, "enhanced_image.png")
    cv2.imwrite(debug_path, processed_img)  # Save for debugging

    custom_config = "--psm 4 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:"

    extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)

    print("\n===== Extracted Raw Text =====\n", extracted_text, "\n==========================\n")

    return clean_text(extracted_text)


def clean_text(text):
    """
    Cleans the extracted OCR text by removing extra spaces, fixing common OCR errors.
    """
    # Remove multiple newlines and weird spacing
    text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
    text = re.sub(r'\s{2,}', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^A-Za-z0-9\s:.-]', '', text)  # Remove unexpected characters

    # Fix common OCR misreads
    text = text.replace("lT", "IT").replace("1T", "IT")
    text = text.replace("Informatn", "Information")
    text = text.replace("Syten", "System")
    text = text.replace("Tchnlogy", "Technology")
    text = text.replace("Proraingan", "Programming")
    text = text.replace("Itagaie", "Integrative")
    text = text.replace("Sacuy", "Security")
    text = text.replace("Architeture", "Architecture")

    return text.strip()

def parse_grades(text):
    subjects, grades = [], []

    # Improved regex pattern to match subjects and valid grades (with decimals)
    pattern = r'([A-Za-z\s]+?)\s+(\d+(?:\.\d{1,2})?)\s*\d*'

    matches = re.findall(pattern, text)

    for subject, score in matches:
        subject = subject.strip()

        # Fix misplaced decimals
        if len(score) > 2 and '.' not in score:
            score = score[:-2] + "." + score[-2:]

        # Skip unwanted data
        if any(word in subject.lower() for word in ["republic", "university", "student", "gwa", "units", "issued"]):
            continue

        # Fix OCR mistakes
        subject = subject.replace("Muttimedla", "Multimedia").replace("Seourity", "Security").replace("T ", "").strip()

        subjects.append(subject)
        grades.append(float(score))

    print("\n📊 Cleaned Grades:", list(zip(subjects, grades)))
    return subjects, grades



def generate_pie_chart(subjects, grades):
    """
    Generates a pie chart of the extracted grades.
    """
    if not subjects or not grades:
        return None

    colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'yellow', 'pink']
    colors = colors[:len(subjects)]  # Adjust colors based on number of subjects

    plt.figure(figsize=(6, 6))
    plt.pie(grades, labels=subjects, autopct='%1.1f%%', colors=colors, startangle=140)
    
    chart_path = os.path.join(UPLOAD_FOLDER, "grades_pie_chart.png")
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    return chart_path

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to handle file upload and process grades.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    # Ensure a valid file is provided
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text and parse grades
    text = extract_text(file_path)
    subjects, grades = parse_grades(text)

    if not subjects or not grades:
        return jsonify({"error": "Could not extract grades. Please upload a clearer image."}), 400

    # Generate pie chart
    pie_chart_path = generate_pie_chart(subjects, grades)
    if not pie_chart_path:
        return jsonify({"error": "Could not generate chart."}), 500

    return send_file(pie_chart_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
