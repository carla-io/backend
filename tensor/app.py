# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from ocr.infer import extract_subjects_and_grades, extract_certificates  

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/process", methods=["POST"])
# def process_files():
#     if "grades" not in request.files and "certificates" not in request.files:
#         return jsonify({"error": "Missing files: both grades and certificates must be provided."}), 400

#     extracted_data = {"grades": [], "certificates": []}

#     # Process Grade Sheets
#     if "grades" in request.files:
#         for file in request.files.getlist("grades"):
#             file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(file_path)
#             try:
#                 subjects_grades = extract_subjects_and_grades(file_path)
#                 extracted_data["grades"].append(subjects_grades)
#             except Exception as e:
#                 extracted_data["grades"].append({"error": f"Failed to extract grades from {file.filename}: {str(e)}"})

#     # Process Certificates
#     if "certificates" in request.files:  # ✅ This should be inside the function
#         for file in request.files.getlist("certificates"):
#             file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(file_path)
#             try:
#                 certificates_info = extract_certificates(file_path)
#                 if certificates_info:
#                     extracted_data["certificates"].append(certificates_info)
#                 else:
#                     extracted_data["certificates"].append({"error": f"No data extracted from {file.filename}"})
#             except Exception as e:
#                 extracted_data["certificates"].append({"error": f"Failed to extract certificates from {file.filename}: {str(e)}"})

#     return jsonify(extracted_data)

# if __name__ == "__main__":
#     app.run(debug=True, port=5001)


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ocr.infer import extract_subjects_and_grades, extract_certificates, extract_text, detect_document_type

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/process", methods=["POST"])
def process_files():
    if "grades" not in request.files and "certificates" not in request.files:
        return jsonify({"error": "Missing files: Please upload grades or certificates."}), 400

    extracted_data = {"grades": [], "certificates": []}

    # Process Grade Sheets
    if "grades" in request.files:
        for file in request.files.getlist("grades"):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            try:
                # Detect document type
                doc_type = detect_document_type(extract_text(file_path))

                if doc_type == "certificate":
                    extracted_data["grades"].append(
                        {"warning": f"{file.filename} appears to be a certificate, not a grade sheet."}
                    )
                else:
                    subjects_grades = extract_subjects_and_grades(file_path)  # Extract grades
                    extracted_data["grades"].append(subjects_grades)
            except Exception as e:
                extracted_data["grades"].append(
                    {"error": f"Failed to extract grades from {file.filename}: {str(e)}"}
                )

    # Process Certificates
    if "certificates" in request.files:
        for file in request.files.getlist("certificates"):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            try:
                # Detect document type before extracting
                doc_type = detect_document_type(extract_text(file_path))

                if doc_type == "certificate":
                    certificates_info = extract_certificates(file_path)  # Extract certificate data
                    extracted_data["certificates"].append(certificates_info)
                else:
                    extracted_data["certificates"].append(
                        {"error": f"{file.filename} does not appear to be a certificate."}
                    )
            except Exception as e:
                extracted_data["certificates"].append(
                    {"error": f"Failed to extract certificates from {file.filename}: {str(e)}"}
                )

    return jsonify(extracted_data)


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
