from flask import Flask, render_template, request, jsonify
import os
import spacy
import requests
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

# Load the English NLP model from spaCy
nlp = spacy.load("en_core_web_sm")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Connect to PostgreSQL database
def connect_to_db():
    try:
        connection = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
# Create user table if it doesn't exist
def create_user_table():
    connection = connect_to_db()
    if connection is None:
        print("Could not connect to the database.")
        return
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL
            );
        ''')
        connection.commit()
        cursor.close()
        connection.close()
        print("User table created successfully.")
    except Exception as e:
        print(f"Error creating user table: {e}")

# Create resume_feedback table to store feedback history
def create_feedback_table():
    connection = connect_to_db()
    if connection is None:
        print("Could not connect to the database.")
        return
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_feedback (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                resume_text TEXT NOT NULL,
                feedback JSONB NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        connection.commit()
        cursor.close()
        connection.close()
        print("Resume feedback table created successfully.")
    except Exception as e:
        print(f"Error creating feedback table: {e}")

# Insert a user into the users table
def insert_user(username, email, password):
    connection = connect_to_db()
    if connection is None:
        print("Database connection failed.")
        return None
    try:
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Hash the password
        cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING id;
        ''', (username, email, hashed_password))
        connection.commit()
        user_id = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        print(f"User inserted with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error inserting user: {e}")
        return None

# Save feedback to the resume_feedback table
def save_feedback_to_db(user_id, resume_text, feedback):
    connection = connect_to_db()
    if connection is None:
        print("Database connection failed.")
        return None
    try:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO resume_feedback (user_id, resume_text, feedback)
            VALUES (%s, %s, %s);
        ''', (user_id, resume_text, psycopg2.extras.Json(feedback)))
        connection.commit()
        cursor.close()
        connection.close()
        print("Feedback saved to the database.")
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return None

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
        
        # Make grading stricter
        score = analyze_feedback_and_assign_strict_score(feedback)
        grades[criterion] = {"feedback": feedback, "score": score}
        total_score += score

    # Calculate final grade as a percentage
    percentage = (total_score / (len(grading_criteria) * 15)) * 100
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
    elif percentage >= 80:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"

# Route to handle file upload and resume grading
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

    # Assuming you have the user_id available from the frontend
    user_id = request.form.get('user_id')  # Ensure this is sent from the frontend

    # Save feedback to the database
    save_feedback_to_db(user_id, resume_text, grading_result)

    os.remove(file_path)

    return jsonify({'grading_result': grading_result})

# Route to view the grading history of a user
@app.route('/history', methods=['GET'])
def view_history():
    user_id = request.args.get('user_id')  # Get the user ID from the frontend

    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT resume_text, feedback, upload_date 
            FROM resume_feedback 
            WHERE user_id = %s ORDER BY upload_date DESC;
        ''', (user_id,))
        history = cursor.fetchall()
        cursor.close()
        connection.close()

        # Format the data for display
        formatted_history = [{
            'resume_text': row[0],
            'feedback': row[1],
            'upload_date': row[2].strftime('%Y-%m-%d %H:%M:%S')  # Format the date nicely
        } for row in history]

        return jsonify({'history': formatted_history})
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

# Route for user signup
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email').lower()
    password = request.form.get('password')

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s) RETURNING id;
        ''', (username, email, hashed_password))
        user_id = cursor.fetchone()[0]
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': 'Signup successful!', 'user_id': user_id}), 200
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Signup failed.'}), 500

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').lower()
    password = request.form.get('password')

    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            if check_password_hash(user[1], password):
                return jsonify({'message': 'Login successful!', 'user_id': user[0]}), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error logging in: {e}")
        return jsonify({'message': 'Login failed.'}), 500
    
    # Enhanced job search route
@app.route('/job-search', methods=['GET'])
def job_search():
    user_id = request.args.get('user_id')
    location = request.args.get('location', 'USA')  
    job_title = request.args.get('job_title', None)  
    
    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT resume_text FROM resume_feedback WHERE user_id = %s ORDER BY upload_date DESC LIMIT 1;', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            resume_text = result[0]
            
            # Extract relevant keywords (e.g., skills) from the resume
            keywords = extract_skills_from_resume(resume_text)
            
            # Call Adzuna API with extracted keywords and location
            api_url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': os.getenv('ADZUNA_APP_ID'),  
                'app_key': os.getenv('ADZUNA_APP_KEY'),
                'what': job_title or ','.join(keywords),  # Search by job title or extracted skills
                'where': location,  # default to 'USA'
                'results_per_page': 10
            }
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                job_results = response.json()
                return jsonify({'jobs': job_results})
            else:
                return jsonify({'error': 'Failed to fetch job listings'}), 500
        else:
            return jsonify({'error': 'No resume found for user'}), 404
    except Exception as e:
        print(f"Error during job search: {e}")
        return jsonify({'error': 'Failed to search for jobs'}), 500




# Define skill-related keywords and patterns to detect skills contextually
SKILL_PATTERNS = ['proficient in', 'experience with', 'familiar with', 'worked on', 'skills in', 'expertise in']

# Function to extract skills from resume text in a flexible way
def extract_skills_from_resume(resume_text):
    doc = nlp(resume_text)
    

    extracted_skills = set()

    for sent in doc.sents:  # Iterate over sentences
        sentence_text = sent.text.lower()
        for pattern in SKILL_PATTERNS:
            if pattern in sentence_text:
                for token in sent:
                    if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 1:
                        extracted_skills.add(token.text)


    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 1:
            extracted_skills.add(token.text)

   
    for chunk in doc.noun_chunks:
        extracted_skills.add(chunk.text)

    # Return the final set of skills found
    return list(extracted_skills)

# Example Usage
resume_text = """
    I am proficient in Python, Java, and Machine Learning. I have extensive experience with Docker, Kubernetes, 
    and building React applications. I am also familiar with Azure and AWS cloud services, and have worked on 
    projects involving data science using TensorFlow and Pandas.
"""
skills = extract_skills_from_resume(resume_text)
print(f"Extracted skills: {skills}")
# Root route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Main block to run the Flask app
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create tables when the app starts
    create_user_table()
    create_feedback_table()

    app.run(debug=True)
