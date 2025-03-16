import os
import pytesseract
from PIL import Image
import PyPDF2
import re
import numpy as np
from pdf2image import convert_from_path
from flask import Flask, request, render_template, jsonify
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # Updated to "uploads"


print(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        
        if not text.strip():
            print("No text found, applying OCR...")
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Function to extract key health metrics
def extract_health_data(text):
    health_data = {
        "eGFR": [], "Fasting Glucose": [], "HDL Cholesterol": [],
        "LDL Cholesterol": [], "Triglycerides": [], "BP Systolic": [], "BP Diastolic": []
    }
    patterns = {
        "eGFR": r"eGFR.*?(\d+(\.\d+)?)",
        "Fasting Glucose": r"Glucose \(Fasting\).*?(\d+(\.\d+)?)",
        "HDL Cholesterol": r"HDL Cholesterol.*?(\d+(\.\d+)?)",
        "LDL Cholesterol": r"LDL Cholesterol.*?(\d+(\.\d+)?)",
        "Triglycerides": r"Triglycerides.*?(\d+(\.\d+)?)",
        "BP Systolic": r"Blood Pressure.*?(\d{2,3})/(\d{2,3})"
    }

    year_match = re.search(r"Reporting Date/Time:\s*(\d{2}/\w{3}/\d{4})", text)
    year = year_match.group(1).split('/')[-1] if year_match else "Unknown"

    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            if key == "BP Systolic":
                health_data["BP Systolic"].append(int(matches[0][0]))
                health_data["BP Diastolic"].append(int(matches[0][1]))
            else:
                health_data[key].append(float(matches[0][0]))
    
    return health_data, year

@app.route('/')
def home():
    return render_template('md1.html')

@app.route('/upload_reports', methods=['POST'])
def upload_reports():
    if 'medicalReports' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    files = request.files.getlist('medicalReports')
    saved_files = []
    all_health_data = {
        "eGFR": [], "Fasting Glucose": [], "HDL Cholesterol": [],
        "LDL Cholesterol": [], "Triglycerides": [], "BP Systolic": [], "BP Diastolic": []
    }
    years = []

    for file in files:
        if file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            text = extract_text_from_pdf(file_path)
            health_data, year = extract_health_data(text)

            if year != "Unknown":
                years.append(year)

            for key in all_health_data.keys():
                if health_data[key]:
                    all_health_data[key].extend(health_data[key])
            
            saved_files.append(file.filename)
    
    trends = {}
    for key, values in all_health_data.items():
        if len(values) > 1:
            if all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "🔴 Increasing"
            elif all(values[i] >= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "✅ Decreasing"
            else:
                trends[key] = "✅ Stable"
        else:
            trends[key] = "No trend data"

    summary = {"health_data": all_health_data, "years": years, "trends": trends}
    return jsonify({"message": "Files uploaded successfully!", "files": saved_files, "summary": summary})

@app.route('/get_health_trends', methods=['GET'])
def get_health_trends():
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    all_health_data = {
        "eGFR": {}, "Fasting Glucose": {}, "HDL Cholesterol": {},
        "LDL Cholesterol": {}, "Triglycerides": {}, "BP Systolic": {}, "BP Diastolic": {}
    }
    years = set()

    # Extract data from all PDFs
    for file in upload_path.glob('*.pdf'):
        text = extract_text_from_pdf(file)
        health_data, year = extract_health_data(text)
        if year != "Unknown":
            years.add(year)
        for key, values in health_data.items():
            if values:  # Only add if there's data
                all_health_data[key][year] = values[0]  # Take first value if multiple per file

    # Convert years to sorted list
    years = sorted(list(years))

    # Fill missing years with "-"
    for key in all_health_data:
        for year in years:
            if year not in all_health_data[key]:
                all_health_data[key][year] = "-"

    # Calculate trends based on sorted year values
    trends = {}
    for key in all_health_data:
        values = [all_health_data[key][year] for year in years if all_health_data[key][year] != "-"]
        if len(values) > 1:
            if all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "🔴 Increasing"
            elif all(values[i] >= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "✅ Decreasing"
            else:
                trends[key] = "✅ Stable"
        else:
            trends[key] = "No trend data"

    return jsonify({"health_data": all_health_data, "years": years, "trends": trends})

if __name__ == '__main__':
    app.run(debug=True)
