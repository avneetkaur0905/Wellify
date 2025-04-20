from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import time
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Initialize Hugging Face client for summarization
client = InferenceClient(
    provider="nebius",
    api_key=os.getenv("HF_API_KEY")
)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}  # Keep your original allowed extensions
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
SUMMARY_FILE = 'static/data/summary.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create summary file if it doesn't exist
if not os.path.exists(SUMMARY_FILE):
    with open(SUMMARY_FILE, 'w') as f:
        json.dump([], f)

# Validate OCR_API_KEY
OCR_API_KEY = os.getenv("OCR_API_KEY")
if not OCR_API_KEY:
    print("Error: OCR_API_KEY not found in environment variables. Please set it in your .env file.")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')

@app.route('/upload_reports', methods=['POST'])
def upload_reports():
    """Handle medical reports upload"""
    if 'medicalReports' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    files = request.files.getlist('medicalReports')
    report_details = request.form.get('reportDetails', '').strip()
    
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    if not report_details:
        return jsonify({'success': False, 'error': 'Please provide report details'}), 400
    
    saved_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Error saving {file.filename}: {str(e)}'}), 500
    
    if saved_files:
        print(f"Report Details: {report_details}")
        print(f"Saved Files: {saved_files}")
        return jsonify({'success': True, 'message': f'Successfully uploaded {len(saved_files)} file(s)'})
    
    return jsonify({'success': False, 'error': 'No files were saved'}), 500

@app.route('/upload_prescription', methods=['POST'])
def upload_prescription():
    """Handle prescription upload"""
    if 'prescriptionFile' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    file = request.files['prescriptionFile']
    prescription_details = request.form.get('prescriptionDetails', '').strip()
    
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not prescription_details:
        return jsonify({'success': False, 'error': 'Please provide prescription details'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"Prescription Details: {prescription_details}")
            print(f"Saved File: {filename}")
            return jsonify({'success': True, 'message': 'Successfully uploaded prescription'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error saving {file.filename}: {str(e)}'}), 500
    
    return jsonify({'success': False, 'error': 'File type not allowed'}), 400

@app.route('/upload_medicine_images', methods=['POST'])
def upload_medicine_images():
    """Handle medicine images upload"""
    if 'medicineImages' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    files = request.files.getlist('medicineImages')
    medicine_details = request.form.get('medicineDetails', '').strip()
    
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    if not medicine_details:
        return jsonify({'success': False, 'error': 'Please provide medicine details'}), 400
    
    saved_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Error saving {file.filename}: {str(e)}'}), 500
    
    if saved_files:
        print(f"Medicine Details: {medicine_details}")
        print(f"Saved Files: {saved_files}")
        return jsonify({'success': True, 'message': f'Successfully uploaded {len(saved_files)} medicine image(s)'})
    
    return jsonify({'success': False, 'error': 'No files were saved'}), 500

@app.route('/health-summary')
def health_summary():
    """Show all uploaded files with analysis options"""
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):  # Check if it's a file (not a directory)
            files.append({
                'name': filename,
                'size': f"{os.path.getsize(filepath) / 1024:.1f} KB",
                'date': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M'),
                'type': filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            })
    return render_template('health_summary.html', files=files)

@app.route('/medical-summary')
def medical_summary():
    """Show all summaries stored in summary.json"""
    try:
        with open(SUMMARY_FILE, 'r') as f:
            summaries = json.load(f)
    except Exception as e:
        summaries = []
        print(f"Error loading summaries: {str(e)}")
    
    # Sort summaries by date (descending order)
    summaries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return render_template('medical_summary.html', summaries=summaries)

@app.route('/analyze-report', methods=['POST'])
def analyze_report():
    """Analyze a specific report using OCR"""
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    if not OCR_API_KEY:
        return jsonify({'error': 'OCR API key not configured'}), 500
    
    try:
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds limit of {MAX_FILE_SIZE / (1024 * 1024)} MB'}), 400
        
        print(f"Starting OCR analysis for file: {filename}, size: {file_size / 1024:.1f} KB")
        
        # OCR API Request with enhanced settings
        with open(filepath, 'rb') as f:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'file': f},
                data={
                    'apikey': OCR_API_KEY,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'OCREngine': 2,  # Best for free tier
                    'scale': True,
                    'detectOrientation': True
                },
                timeout=20  # Reduced timeout to 20 seconds to prevent long hangs
            )
        
        # Log the response status and headers for debugging
        print(f"OCR API response status: {response.status_code}")
        print(f"OCR API response headers: {response.headers}")
        
        # Parse response
        result = response.json()
        
        # Log the raw response for debugging
        print(f"OCR API response: {json.dumps(result, indent=2)}")
        
        # Handle API errors
        if result.get('IsErroredOnProcessing', False):
            error_msg = result.get('ErrorMessage', 'Unknown OCR error')
            if isinstance(error_msg, list):
                error_msg = ' '.join(error_msg)
            return jsonify({
                'success': False,
                'error': f'OCR processing failed: {error_msg}'
            }), 500
        
        # Return extracted text
        if result.get('ParsedResults'):
            extracted_text = result['ParsedResults'][0].get('ParsedText', '')
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': extracted_text.strip()
            })
        
        return jsonify({
            'success': False,
            'error': 'No text found in document'
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'OCR API request timed out after 20 seconds'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/summarize-report', methods=['POST'])
def summarize_report():
    """Summarize the provided text using Hugging Face model and save to summary.json"""
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Rate limiting
        time.sleep(3)
        
        # Medical analysis using chat completion
        completion = client.chat.completions.create(
            model="aaditya/Llama3-OpenBioLLM-70B",
            messages=[
                {
                    "role": "system",
                    "content": "YYou are a medical expert. Analyze the provided clinical text and generate a small summary with: 1) Patient summary 2) Key findings 3) Recommended actions 4) Date. The output must be small and in 4 paragraphs."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=512,
            temperature=0.3  # Lower for more deterministic medical responses
        )
        
        # Extract the summary
        summary = completion.choices[0].message.content
        
        # Extract date from summary using regex (e.g., DD/MM/YYYY format)
        date_match = re.search(r'\d{2}/\d{2}/\d{4}', summary)
        summary_date = date_match.group(0) if date_match else None
        
        # Convert the extracted date to YYYY-MM-DD format for sorting
        timestamp = datetime.now().strftime('%Y-%m-%d')  # Fallback to current date
        if summary_date:
            try:
                # Parse DD/MM/YYYY and convert to YYYY-MM-DD
                date_obj = datetime.strptime(summary_date, '%d/%m/%Y')
                timestamp = date_obj.strftime('%Y-%m-%d')
            except ValueError as e:
                print(f"Error parsing date from summary: {e}")
        
        # Load existing summaries
        try:
            with open(SUMMARY_FILE, 'r') as f:
                summaries = json.load(f)
        except Exception as e:
            summaries = []
            print(f"Error loading summaries: {str(e)}")
        
        # Append new summary with the extracted date as timestamp
        summaries.append({
            'summary': summary,
            'timestamp': timestamp
        })
        
        # Sort summaries by timestamp (descending order)
        summaries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Save updated summaries back to file
        try:
            with open(SUMMARY_FILE, 'w') as f:
                json.dump(summaries, f, indent=4)
        except Exception as e:
            print(f"Error saving summaries: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to save summary: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'solution': "Try again with shorter text or wait 10 seconds"
        }), 500

@app.route('/data/<path:filename>')
def serve_data(filename):
    """Serve static data files like recommendations.json"""
    data_dir = 'static/data'
    file_path = os.path.join(data_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': f'File {filename} not found in {data_dir}'}), 404
    return send_from_directory(data_dir, filename)

# Custom Jinja filters for date formatting
def strptime(date_string, format):
    return datetime.strptime(date_string, format)

def strftime(date_obj, format):
    return date_obj.strftime(format)

# Register the filters with Jinja
app.jinja_env.filters['strptime'] = strptime
app.jinja_env.filters['strftime'] = strftime

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)