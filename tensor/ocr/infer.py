# import re
# from ocr.preprocess import extract_text  # Importing preprocess functions

# def extract_subjects_and_grades(image_path, use_easyocr=True):
#     """Extract subjects and grades, ensuring correct subject-grade pairing."""
#     text_data = extract_text(image_path, use_easyocr)

#     subjects_grades = {}  # Dictionary to store subjects and their associated grades
#     temp_subject = None

#     # Debugging: Print the raw extracted text
#     print("Extracted Text Data for Grades:", text_data)

#     for text in text_data:
#         text = text.strip()

#         # Detect grades (either numeric or letter-based grades)
#         if re.match(r'^\d{2,3}(\.\d+)?$', text):  # Detect grades like 89, 92.5
#             if temp_subject:
#                 # If subject exists, append the grade to that subject's list
#                 if temp_subject not in subjects_grades:
#                     subjects_grades[temp_subject] = []
#                 subjects_grades[temp_subject].append(text)
#         elif text and not re.search(r'\d{2,3}', text):  # Ensure it's not a grade, i.e., a subject
#             # Clean up text and ensure it's a valid subject name
#             text = re.sub(r'^[I|i]', '', text)  # Remove stray "I" in front of subjects (e.g., IEnglish -> English)
#             text = re.sub(r'\d.*', '', text)  # Remove any stray numbers that might have been OCR'd

#             if temp_subject != text:  # If a new subject is found
#                 temp_subject = text  # Update the subject

#     # Format the output to be subject followed by all grades
#     formatted_output = []
#     for subject, grades in subjects_grades.items():
#         formatted_output.append(f"{subject} " + " ".join(grades))  # Join grades as space-separated values

#     return formatted_output

# def extract_certificates(image_path, use_easyocr=True):
#     """Extract certificate information like name, date, and type from the image."""
#     text_data = extract_text(image_path, use_easyocr)

#     certificates_info = {}

#     # Debugging: Print the raw extracted text
#     print("Extracted Text Data for Certificates:", text_data)

#     # Define a set of keywords related to certificates (names, date, etc.)
#     name_keywords = ['Name', 'Name of Student', 'Full Name', 'Student Name']
#     date_keywords = ['Date', 'Issued', 'Graduation Date', 'Date of Issue']
#     cert_keywords = ['Certificate', 'Awarded', 'Completion']

#     temp_name = None
#     temp_date = None
#     temp_cert = None

#     # Iterate over text and capture relevant information
#     for text in text_data:
#         text = text.strip()

#         # Check if text contains name-related keywords
#         for keyword in name_keywords:
#             if keyword.lower() in text.lower():
#                 temp_name = text.split(keyword, 1)[-1].strip()
#                 break  # Stop searching after capturing the name

#         # Check if text contains date-related keywords
#         for keyword in date_keywords:
#             if keyword.lower() in text.lower():
#                 temp_date = text.split(keyword, 1)[-1].strip()
#                 break  # Stop searching after capturing the date

#         # Check if text contains certificate-related keywords
#         for keyword in cert_keywords:
#             if keyword.lower() in text.lower():
#                 temp_cert = text.strip()
#                 break  # Stop searching after capturing the certificate type

#         # Once all information is found, save and break loop (optional)
#         if temp_name and temp_date and temp_cert:
#             certificates_info['Name'] = temp_name
#             certificates_info['Date'] = temp_date
#             certificates_info['Certificate Type'] = temp_cert
#             break  # You can remove this break if there might be multiple certificates

#     # In case no information is found, return empty
#     return certificates_info


# if __name__ == "__main__":
#     # Extract subjects and grades
#     extracted_grades = extract_subjects_and_grades("test_image.png", use_easyocr=True)
#     print("Extracted Subjects & Grades:", extracted_grades)

#     # Extract certificate information
#     certificate_data = extract_certificates("certificate_image.png", use_easyocr=True)
#     print("Extracted Certificate Info:", certificate_data)

import easyocr
import re
from ocr.preprocess import extract_text  # Importing preprocess functions

def extract_subjects_and_grades(image_path, use_easyocr=True):
    """Extract subjects and grades, ensuring correct subject-grade pairing."""
    text_data = extract_text(image_path, use_easyocr)

    subjects_grades = {}  # Dictionary to store subjects and their associated grades
    temp_subject = None

    # Debugging: Print the raw extracted text
    print("Extracted Text Data for Grades:", text_data)

    for text in text_data:
        text = text.strip()

        # Detect grades (either numeric or letter-based grades)
        if re.match(r'^\d{2,3}(\.\d+)?$', text):  # Detect grades like 89, 92.5
            if temp_subject:
                # If subject exists, append the grade to that subject's list
                if temp_subject not in subjects_grades:
                    subjects_grades[temp_subject] = []
                subjects_grades[temp_subject].append(text)
        elif text and not re.search(r'\d{2,3}', text):  # Ensure it's not a grade, i.e., a subject
            # Clean up text and ensure it's a valid subject name
            text = re.sub(r'^[I|i]', '', text)  # Remove stray "I" in front of subjects (e.g., IEnglish -> English)
            text = re.sub(r'\d.*', '', text)  # Remove any stray numbers that might have been OCR'd

            if temp_subject != text:  # If a new subject is found
                temp_subject = text  # Update the subject

    # Format the output to be subject followed by all grades
    formatted_output = []
    for subject, grades in subjects_grades.items():
        formatted_output.append(f"{subject} " + " ".join(grades))  # Join grades as space-separated values

    return formatted_output


def extract_certificates(image_path, use_easyocr=True):
    """Extract certificate information like name, date, and type from the image."""
    text_data = extract_text(image_path, use_easyocr)

    certificates_info = {}

    # Debugging: Print the raw extracted text
    print("Extracted Text Data for Certificates:", text_data)

    # Define a set of keywords related to certificates (names, date, etc.)
    name_keywords = ['Name', 'Name of Student', 'Full Name', 'Student Name']
    date_keywords = ['Date', 'Issued', 'Graduation Date', 'Date of Issue']
    cert_keywords = ['Certificate', 'Awarded', 'Completion']

    temp_name = None
    temp_date = None
    temp_cert = None

    # Iterate over text and capture relevant information
    for text in text_data:
        text = text.strip()

        # Check if text contains name-related keywords
        for keyword in name_keywords:
            if keyword.lower() in text.lower():
                temp_name = text.split(keyword, 1)[-1].strip()
                break  # Stop searching after capturing the name

        # Check if text contains date-related keywords
        for keyword in date_keywords:
            if keyword.lower() in text.lower():
                temp_date = text.split(keyword, 1)[-1].strip()
                break  # Stop searching after capturing the date

        # Check if text contains certificate-related keywords
        for keyword in cert_keywords:
            if keyword.lower() in text.lower():
                temp_cert = text.strip()
                break  # Stop searching after capturing the certificate type

        # Once all information is found, save and break loop (optional)
        if temp_name and temp_date and temp_cert:
            certificates_info['Name'] = temp_name
            certificates_info['Date'] = temp_date
            certificates_info['Certificate Type'] = temp_cert
            break  # You can remove this break if there might be multiple certificates

    # In case no information is found, return empty
    return certificates_info


if __name__ == "__main__":
    # Extract subjects and grades
    extracted_grades = extract_subjects_and_grades("test_image.png", use_easyocr=True)
    print("Extracted Subjects & Grades:", extracted_grades)

    # Extract certificate information
    certificate_data = extract_certificates("certificate_image.png", use_easyocr=True)
    print("Extracted Certificate Info:", certificate_data)

