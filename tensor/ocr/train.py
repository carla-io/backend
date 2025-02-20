import easyocr
import os
import json

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

def train_ocr(dataset_folder, labels_file):
    """Train OCR model using labeled dataset"""
    with open(labels_file, 'r') as f:
        labels = json.load(f)

    correct = 0
    total = 0

    for image_name, true_text in labels.items():
        image_path = os.path.join(dataset_folder, image_name)
        result = reader.readtext(image_path, detail=0)
        
        if result and true_text.lower() in result[0].lower():
            correct += 1
        total += 1

    accuracy = correct / total * 100
    print(f"OCR Training Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    train_ocr("dataset/", "dataset/labels.json")
