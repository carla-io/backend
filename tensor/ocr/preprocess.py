

# import cv2
# import numpy as np
# import pytesseract
# import easyocr
# import re

# reader = easyocr.Reader(['en'])

# def preprocess_image(image_path, color=True):
#     img = cv2.imread(image_path)
#     img = cv2.resize(img, (1500, 1100))
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
#     gray = clahe.apply(gray)
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
#     edges = cv2.Canny(gray, 100, 200)
#     kernel = np.ones((3, 3), np.uint8)
#     gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
#     gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

#     return img if color else gray

# def extract_text(image_path, use_easyocr=True):
#     processed_img = preprocess_image(image_path, color=True)

#     if use_easyocr:
#         results = reader.readtext(processed_img, detail=1)
#         text_data = [text[1] for text in results if text[2] > 0.7]
#     else:
#         custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz% '
#         text_data = pytesseract.image_to_string(processed_img, config=custom_config).split('\n')

#     return text_data

# import re

# def extract_certificates(image_path, use_easyocr=True):
#     text_data = extract_text(image_path, use_easyocr)
#     certificates_info = {}

#     # Regex patterns for different sections
#     name_pattern = re.compile(r'\b(Name|Student Name|Candidate|Recipient)\b', re.IGNORECASE)
#     date_pattern = re.compile(r'\b(Date|Issued|Graduation|Awarded on|Date of Issue)\b', re.IGNORECASE)
#     cert_pattern = re.compile(r'\b(Certificate|Award|Diploma|Degree|Completion)\b', re.IGNORECASE)
#     achievement_pattern = re.compile(r'\b(Certified in|Completed|Achievement in|Awarded for|Successfully completed|This Certificate|Recognition for|This certificate is given to|This certificate is awarded to)\b', re.IGNORECASE)

#     temp_name, temp_date, temp_cert, temp_achievement = None, None, None, None

#     for i, text in enumerate(text_data):
#         text = text.strip()

#         # Extracting based on known keywords
#         if name_pattern.search(text):
#             temp_name = text
#         elif date_pattern.search(text):
#             temp_date = text
#         elif cert_pattern.search(text):
#             temp_cert = text
#         elif achievement_pattern.search(text):
#             temp_achievement = text

#         # If "Certificate" is found, check the next few lines for context
#         if "CERTIFICATE" in text.upper() and i < len(text_data) - 2:
#             possible_achievement = text_data[i + 1] + " " + text_data[i + 2]
#             if len(possible_achievement.split()) > 4:  # Ensuring it's a meaningful phrase
#                 temp_achievement = possible_achievement

#         if temp_name and temp_date and temp_cert and temp_achievement:
#             break

#     certificates_info['Name'] = temp_name or "Not Found"
#     certificates_info['Date'] = temp_date or "Not Found"
#     certificates_info['Certificate Type'] = temp_cert or "Not Found"
#     certificates_info['Achievement'] = temp_achievement or "Not Found"

#     return certificates_info

import cv2
import numpy as np
import pytesseract
import easyocr
import re

reader = easyocr.Reader(['en'])

# Keywords to detect grades and certificates
GRADES_KEYWORDS = {"math", "science", "english", "subject", "grade", "gpa", "score", "marks", "assessment", "percentage"}
CERTIFICATE_KEYWORDS = {"certificate", "completion", "awarded", "achievement", "diploma", "degree", "recognition"}

def preprocess_image(image_path, color=True):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (1500, 1100))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 100, 200)
    kernel = np.ones((3, 3), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    return img if color else gray

def extract_text(image_path, use_easyocr=True):
    processed_img = preprocess_image(image_path, color=True)

    if use_easyocr:
        results = reader.readtext(processed_img, detail=1)
        text_data = [text[1] for text in results if text[2] > 0.7]
    else:
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz% '
        text_data = pytesseract.image_to_string(processed_img, config=custom_config).split('\n')

    return text_data

def detect_document_type(text_data):
    """Detect whether the document contains grades or certificates"""
    grades_count = sum(1 for word in text_data if any(kw in word.lower() for kw in GRADES_KEYWORDS))
    certificates_count = sum(1 for word in text_data if any(kw in word.lower() for kw in CERTIFICATE_KEYWORDS))

    if grades_count > certificates_count:
        return "grades"
    elif certificates_count > grades_count:
        return "certificate"
    else:
        return "unknown"

def validate_upload(image_path, expected_type):
    """Check if uploaded document matches the expected type (grades/certificate)"""
    text_data = extract_text(image_path)
    detected_type = detect_document_type(text_data)

    if detected_type != expected_type:
        return f"⚠ Warning: This section is for {expected_type} only. You uploaded a {detected_type} document."

    return "✅ Document uploaded successfully."

def extract_certificates(image_path, use_easyocr=True):
    text_data = extract_text(image_path, use_easyocr)
    certificates_info = {}

    name_pattern = re.compile(r'\b(Name|Student Name|Candidate|Recipient)\b', re.IGNORECASE)
    date_pattern = re.compile(r'\b(Date|Issued|Graduation|Awarded on|Date of Issue)\b', re.IGNORECASE)
    cert_pattern = re.compile(r'\b(Certificate|Award|Diploma|Degree|Completion)\b', re.IGNORECASE)
    achievement_pattern = re.compile(r'\b(Certified in|Completed|Achievement in|Awarded for|Successfully completed|This Certificate|Recognition for|This certificate is given to|This certificate is awarded to)\b', re.IGNORECASE)

    temp_name, temp_date, temp_cert, temp_achievement = None, None, None, None

    for i, text in enumerate(text_data):
        text = text.strip()

        if name_pattern.search(text):
            temp_name = text
        elif date_pattern.search(text):
            temp_date = text
        elif cert_pattern.search(text):
            temp_cert = text
        elif achievement_pattern.search(text):
            temp_achievement = text

        if "CERTIFICATE" in text.upper() and i < len(text_data) - 2:
            possible_achievement = text_data[i + 1] + " " + text_data[i + 2]
            if len(possible_achievement.split()) > 4:
                temp_achievement = possible_achievement

        if temp_name and temp_date and temp_cert and temp_achievement:
            break

    certificates_info['Name'] = temp_name or "Not Found"
    certificates_info['Date'] = temp_date or "Not Found"
    certificates_info['Certificate Type'] = temp_cert or "Not Found"
    certificates_info['Achievement'] = temp_achievement or "Not Found"

    return certificates_info
