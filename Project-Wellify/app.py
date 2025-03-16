import os
import pytesseract
from PIL import Image
import PyPDF2
import re
import numpy as np
from pdf2image import convert_from_path
from flask import Flask, request, render_template, jsonify

# Initialize Flask app
app = Flask(__name__)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file. If text extraction fails, fallback to OCR.
    """
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        
        # Print the extracted text to verify
        print("Extracted Text from PDF:\n", text)  # <-- Added print statement
        
        # If no text was extracted, use OCR
        if not text.strip():
            print("No text found, applying OCR...")
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"

    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    return text

# Function to extract key health metrics from text
def extract_health_data(text):
    """
    Extracts key health data from the text of a medical report.
    """
    health_data = {
        "eGFR": [],
        "Fasting Glucose": [],
        "Total Cholesterol": [],
        "HDL Cholesterol": [],
        "LDL Cholesterol": [],
        "Triglycerides": [],
        "BP Systolic": [],
        "BP Diastolic": []
    }
    
    # Regular expressions to find relevant data
    patterns = {
        "eGFR": r"eGFR.*?(\d+(\.\d+)?)",
        "Fasting Glucose": r"Glucose \(Fasting\).*?(\d+(\.\d+)?)",
        "Total Cholesterol": r"Total Cholesterol.*?(\d+(\.\d+)?)",
        "HDL Cholesterol": r"HDL Cholesterol.*?(\d+(\.\d+)?)",
        "LDL Cholesterol": r"LDL Cholesterol.*?(\d+(\.\d+)?)",
        "Triglycerides": r"Triglycerides.*?(\d+(\.\d+)?)",
        "BP Systolic": r"Blood Pressure.*?(\d{2,3})/(\d{2,3})"
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            if key == "BP Systolic":
                health_data["BP Systolic"].append(int(matches[0][0]))
                health_data["BP Diastolic"].append(int(matches[0][1]))
            else:
                health_data[key].append(float(matches[0][0]))
    
    # Print the extracted health data to verify
    print("Extracted Health Data:\n", health_data)  # <-- Added print statement
    
    return health_data

# Function to generate summary from extracted data
def generate_health_summary(health_data):
    """
    Generates a health summary from extracted values.
    """
    summary = {}
    for key, values in health_data.items():
        if values:
            summary[key] = {
                "min": min(values),
                "max": max(values),
                "average": round(np.mean(values), 2)
            }
        else:
            summary[key] = "No data available"
    
    # Print the generated summary to verify
    print("Generated Health Summary:\n", summary)  # <-- Added print statement
    
    return summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/md1')
def md1():
    return render_template('md1.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle multiple file uploads and process PDF reports.
    """
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist('files')
    all_health_data = {
        "eGFR": [],
        "Fasting Glucose": [],
        "Total Cholesterol": [],
        "HDL Cholesterol": [],
        "LDL Cholesterol": [],
        "Triglycerides": [],
        "BP Systolic": [],
        "BP Diastolic": []
    }
    years = []

    for file in files:
        if file.filename.endswith('.pdf'):
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)
            print(f"Processing file: {file.filename}")  # <-- Added print statement
            text = extract_text_from_pdf(file_path)
            health_data = extract_health_data(text)

            # Extract the year from the Reporting Date/Time field
            year_match = re.search(r"Reporting Date/Time:\s*(\d{2}/\w{3}/\d{4})", text)
            if year_match:
                year = year_match.group(1).split('/')[-1]  # Extract the year (e.g., 2024)
                years.append(year)

            # Merge extracted data into all_health_data
            for key in all_health_data.keys():
                if health_data[key]:
                    all_health_data[key].extend(health_data[key])
    
    # Print the final health data and years
    print("All Health Data:\n", all_health_data)  # <-- Added print statement
    print("Years:\n", years)  # <-- Added print statement
    
    # Calculate trends
    trends = {}
    for key, values in all_health_data.items():
        if len(values) > 1:
            if all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "🔴 Increasing"
            elif all(values[i] >= values[i + 1] for i in range(len(values) - 1)):
                trends[key] = "✅  Decreasing"
            else:
                trends[key] = "✅ Stable"
        else:
            trends[key] = "No trend data"

    # Prepare summary
    summary = {
        "health_data": all_health_data,
        "years": years,
        "trends": trends
    }

    return jsonify(summary)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)