from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import os
import sys
import json
from werkzeug.utils import secure_filename
from config import GEMINI_API_KEY, MAX_IMAGE_SIZE, ALLOWED_EXTENSIONS

# Set UTF-8 as default encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False  # Enable UTF-8 response
app.config['MAX_CONTENT_LENGTH'] = MAX_IMAGE_SIZE

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_assamese_caption(model, image_path):
    image = None
    try:
        print(f"Opening image from path: {image_path}")
        image = Image.open(image_path)
        
        # Validate image format
        if image.format not in ['PNG', 'JPEG', 'GIF']:
            raise ValueError(f"Unsupported image format: {image.format}")
            
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        print("Image loaded successfully")
        
        try:
            prompt = """
            Task: Analyze the image and provide a detailed description in Assamese language.
            Requirements:
            - Be natural and fluent in Assamese
            - Include details about objects, people, actions, and setting
            - Maintain cultural context and sensitivity
            - Use Unicode for Assamese text
            """
            response = model.generate_content([
                prompt,
                image
            ])
            print("Response received from Gemini API")
            
            if not response.text:
                raise ValueError("Empty response received from API")
                
            # Ensure the response is properly encoded
            caption = response.text.encode('utf-8').decode('utf-8')
            return caption
            
        except Exception as api_error:
            error_msg = f"Gemini API Error: {str(api_error)}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        print(error_msg)
        return error_msg
    finally:
        if image:
            image.close()

# Configure Gemini API
model = configure_gemini(GEMINI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types are: png, jpg, jpeg, gif'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            caption = generate_assamese_caption(model, filepath)
            return jsonify({'caption': caption})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
