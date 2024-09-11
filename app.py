from flask import Flask, render_template, request, jsonify
import os
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Print the API key to verify it's loaded correctly
print(f"API Key: {client.api_key}")  # Check if it's None or a valid key

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'


# Function to parse PDF files
def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


# Function to parse DOCX files
def parse_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


# Function to analyze the resume using OpenAI
def analyze_resume(resume_text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Correct model name
        messages=[{"role": "user", "content": f"Analyze this resume:\n{resume_text}"}],
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


# Route to handle file upload and resume analysis
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.doc') or file.filename.endswith('.docx')):
        return jsonify({'error': 'Unsupported file format'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Parse the resume depending on the file type
    if file.filename.endswith('.pdf'):
        resume_text = parse_pdf(file_path)
    elif file.filename.endswith('.doc') or file.filename.endswith('.docx'):
        resume_text = parse_docx(file_path)

    # Analyze the parsed resume text using OpenAI API
    analysis = analyze_resume(resume_text)

    # Remove the uploaded file after analysis
    os.remove(file_path)

    # Return analysis as JSON
    return jsonify({'analysis': analysis})


# AI Chat Box route using OpenAI
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Correct model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        # Extract the reply from the response
        reply = response.choices[0].message.content.strip()
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f"Error generating reply: {str(e)}"}), 500


# Root route to render the index page
@app.route('/')
def index():
    return render_template('index.html')


# Main block to run the Flask app
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
