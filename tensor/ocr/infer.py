import easyocr
import re
from ocr.preprocess import extract_text  # Importing preprocess functions

GRADES_KEYWORDS = {"math", "science", "english", "subject", "grade", "gpa", "score", "marks", "assessment", "percentage"}
CERTIFICATE_KEYWORDS = {"certificate", "completion", "awarded", "achievement", "diploma", "degree", "recognition"}

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

def extract_subjects_and_grades(image_path, use_easyocr=True):
    """Extract subjects and their corresponding grades."""
    text_data = extract_text(image_path, use_easyocr)
    subjects_grades = {}  # Dictionary to store subjects and their associated grades
    temp_subject = None

    # Debugging: Print extracted text
    print("\n🔍 Extracted Text Data for Grades:", text_data)

    for text in text_data:
        text = text.strip()

        # Detect numeric grades (e.g., 85, 92.5)
        if re.match(r'^\d{1,3}(\.\d+)?$', text):  
            if temp_subject:
                if temp_subject not in subjects_grades:
                    subjects_grades[temp_subject] = []
                subjects_grades[temp_subject].append(text)
        elif text and not re.search(r'\d{2,3}', text):  # Ensure it's not a grade
            text = re.sub(r'^[I|i]', '', text)  # Remove leading "I" (e.g., "IEnglish" → "English")
            text = re.sub(r'\d.*', '', text)  # Remove stray numbers
            temp_subject = text  # Assign subject

    # Formatting output
    formatted_output = [{subject: grades} for subject, grades in subjects_grades.items()]
    return formatted_output

def extract_certificates(image_path, use_easyocr=True):
    """Extract certificate details like name, date, and type."""
    text_data = extract_text(image_path, use_easyocr)
    certificates_info = {
        "Name": "Not Found",
        "Date": "Not Found",
        "Certificate Type": "Not Found",
        "Achievement": "Not Found",
        
    }

    # Debugging: Print extracted text
    print("\n🔍 Extracted Text Data for Certificates:", text_data)

    # Patterns for extracting certificate-related info
    # name_pattern = re.compile(r'\b(Name|Student Name|Candidate|Recipient)\b', re.IGNORECASE)
    # date_pattern = re.compile(r'\b(Date|Issued|Graduation|Awarded on|Date of Issue)\b', re.IGNORECASE)
    # cert_pattern = re.compile(r'\b(Certificate|Award|Diploma|Degree|Completion|Achievement in)\b', re.IGNORECASE)
    name_pattern = re.compile(r'\b(Name|Student Name|Candidate|Recipient)\b', re.IGNORECASE)
    date_pattern = re.compile(r'\b(Date|Issued|Graduation|Awarded on|Date of Issue)\b', re.IGNORECASE)
    cert_pattern = re.compile(r'\b(Certificate|Award|Diploma|Degree|Completion)\b', re.IGNORECASE)
    achievement_pattern = re.compile(r'\b(Certified in|Completed|Achievement in|Awarded for|Successfully completed|This Certificate|Recognition for|This certificate is given to|This certificate is awarded to)\b', re.IGNORECASE)
    

    temp_name, temp_date, temp_cert = None, None, None

    for text in text_data:
        text = text.strip()

        if name_pattern.search(text):
            temp_name = text
        elif date_pattern.search(text):
            temp_date = text
        elif cert_pattern.search(text):
            temp_cert = text
        elif achievement_pattern.search(text):
            temp_cert = text

        if temp_name and temp_date and temp_cert:
            break  # Stop once all are found

    # Update dictionary if values found
    if temp_name:
        certificates_info["Name"] = temp_name
    if temp_date:
        certificates_info["Date"] = temp_date
    if temp_cert:
        certificates_info["Certificate Type"] = temp_cert
    if temp_cert:
        certificates_info["Achievement"] = temp_cert


    return certificates_info

if __name__ == "__main__":
    # Example usage
    extracted_text = extract_text("test_image.png", use_easyocr=True)
    doc_type = detect_document_type(extracted_text)
    print("\n📌 Detected Document Type:", doc_type)
    
    if doc_type == "grades":
        extracted_grades = extract_subjects_and_grades("test_image.png", use_easyocr=True)
        print("\n📌 Extracted Subjects & Grades:", extracted_grades)
    elif doc_type == "certificate":
        certificate_data = extract_certificates("certificate_image.png", use_easyocr=True)
        print("\n📌 Extracted Certificate Info:", certificate_data)