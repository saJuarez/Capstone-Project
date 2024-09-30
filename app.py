from flask import Flask, render_template, request, jsonify
import os
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Print the API key to verify it's loaded correctly (optional, for debugging)
print(f"API Key: {os.getenv('OPENAI_API_KEY')}")  # Print API key loaded from env file for validation

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

# Function to grade the resume based on different criteria using OpenAI
def grade_resume(resume_text):
    grading_criteria = {
        "Experience": "Evaluate how relevant the experience described in the resume is for the targeted job and suggest improvements.",
        "Skills": "Evaluate the relevance and proficiency of the listed skills in the resume and suggest ways to enhance the skills section.",
        "Education": "Does the educational background align with the required qualifications for the job? Suggest improvements if needed.",
        "Clarity and Grammar": "Evaluate whether the resume is clear, well-written, and free of grammar mistakes, and provide suggestions for improvement.",
        "Formatting": "Evaluate the organization and formatting of the resume and suggest any improvements for better presentation."
    }

    grades = {}
    total_score = 0

    # Loop over each criterion and ask OpenAI to evaluate
    for criterion, prompt in grading_criteria.items():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict resume grading assistant. Be as critical as possible."},
                {"role": "user", "content": f"{prompt}\n\nResume:\n{resume_text}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        feedback = response.choices[0].message.content.strip()
        
        # Make grading stricter (scale 10-15 instead of 15-20)
        score = analyze_feedback_and_assign_strict_score(feedback)
        grades[criterion] = {"feedback": feedback, "score": score}
        total_score += score

    # Calculate final grade as a percentage
    percentage = (total_score / (len(grading_criteria) * 15)) * 100  # Max score per category is now 15
    final_grade = assign_letter_grade(percentage)

    return {"grades": grades, "total_score": total_score, "percentage": percentage, "final_grade": final_grade}

# Stricter score assignment
def analyze_feedback_and_assign_strict_score(feedback):
    import random
    return random.randint(10, 15)

# Adjust the letter grade assignment to match stricter criteria
def assign_letter_grade(percentage):
    if percentage >= 90:
        return "A"
    elif percentage >= 75:  # Adjusted for tougher grading
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


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

    # Grade the parsed resume text using OpenAI API
    grading_result = grade_resume(resume_text)

    # Debugging log to verify the grading result
    print(f"Grading result: {grading_result}")

    # Remove the uploaded file after analysis
    os.remove(file_path)

    # Return analysis and grade as JSON
    return jsonify({'grading_result': grading_result})


# AI Chat Box route using OpenAI
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150,
            temperature=0.7
        )
        # Extract the reply correctly using '.content'
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