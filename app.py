from flask import Flask, render_template, request, jsonify
import os
import pdfplumber
import docx
import openai
from dotenv import load_dotenv
from job import job_page

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(job_page)
app.config['UPLOAD_FOLDER'] = './uploads'

openai.api_key = os.getenv('OPENAI_API_KEY')


def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


def parse_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def analyze_resume(resume_text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Please analyze the following resume and provide a summary of the candidate's qualifications:\n{resume_text}",
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].text
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.doc') or file.filename.endswith('.docx')):
        return jsonify({'error': 'Unsupported file format'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 
    if file.filename.endswith('.pdf'):
        resume_text = parse_pdf(file_path)
    elif file.filename.endswith('.doc') or file.filename.endswith('.docx'):
        resume_text = parse_docx(file_path)

    # OpenAI API
    analysis = analyze_resume(resume_text)

    # 
    os.remove(file_path)

    return jsonify({'analysis': analysis})

# AI Chat Box 
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': f"Error generating reply: {str(e)}"}), 500


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
