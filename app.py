from flask import Flask, render_template, request, jsonify, session, redirect
import os
import pdfplumber
import docx
import requests
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras
from werkzeug.security import generate_password_hash, check_password_hash
import spacy

# Load environment variables from .env file
load_dotenv()

# Load the English NLP model from spaCy
nlp = spacy.load("en_core_web_sm")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Set secret key for session management
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

# Create users table 
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

# Create resume_feedback table 
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

# Create jobs table 
def create_jobs_table():
    connection = connect_to_db()
    if connection is None:
        print("Could not connect to the database.")
        return
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                description TEXT,
                company VARCHAR(255),
                location VARCHAR(255),
                posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        connection.commit()
        cursor.close()
        connection.close()
        print("Jobs table created successfully.")
    except Exception as e:
        print(f"Error creating jobs table: {e}")

# Insert a user into the users table
def insert_user(username, email, password):
    connection = connect_to_db()
    if connection is None:
        print("Database connection failed.")
        return None
    try:
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Hash a user's password
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

# Parse PDF files
def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Parse DOCX files
def parse_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Grade the resume based on different criteria using OpenAI
def grade_resume(resume_text):
    grading_criteria = {
        "Experience": "Evaluate how relevant the experience described in the resume is for the targeted job and suggest improvements.",
        "Skills": "Evaluate the relevance and proficiency of the listed skills in the resume and suggest ways to enhance the skills section.",
        "Education": "Does the educational background align with the required qualifications for the job? Suggest improvements if needed.",
        "Clarity and Grammar": "Evaluate whether the resume is clear, well-written, and free of grammar mistakes, and provide suggestions for improvement.",
        "Formatting": "Evaluate the organization and formatting of the resume and suggest any improvements for better presentation.",
        "Portfolio": "Evaluate the relevance of the portfolio provided and suggest improvements."
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

    # Debugging log to verify the grading result
    print(f"Grading result: {grading_result}")

    # Remove the uploaded file after analysis
    os.remove(file_path)

    # Save feedback to the database
    user_id = session.get('user_id')
    if user_id:
        save_feedback_to_db(user_id, resume_text, grading_result)

    # Return analysis and grade as JSON
    return jsonify({'grading_result': grading_result})

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

# Signup route to create a new user
@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Received signup request: username={username}, email={email}")

        # Check input lengths
        if len(username) > 150 or len(email) > 200 or len(password) > 200:
            return jsonify({'message': 'Input values are too long.'}), 400

        user_id = insert_user(username, email, password)

        if user_id:
            return jsonify({'message': 'Signup successful!'}), 200
        else:
            return jsonify({'message': 'Error: User could not be created.'}), 500
    except Exception as e:
        print(f"Error in signup route: {e}")
        return jsonify({'message': f"Error: {str(e)}"}), 500

# Login route to authenticate a user
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user:
        stored_password = user[3]

        if check_password_hash(stored_password, password):  
            session['user_id'] = user[0]  # Store user ID in session
            session['logged_in'] = True

            return jsonify({'success': True, 'message': 'Login successful!', 'user_id': user[0]}), 200
        else:
            print("Password verification failed.")
            return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401
    else:
        print("User not found for email:", email)
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    
    
@app.route('/api/check-login-status')
def check_login_status():
    return jsonify({"logged_in": session.get('logged_in', False)})

# Clear session upon logout
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/feedback-history')
def feedback_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'You must be logged in first to access feedback history.'}), 403
    return render_template('feedback-history.html')

def get_feedback_history(user_id):
    connection = connect_to_db()
    if connection is None:
        print("Database connection failed.")
        return []
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT feedback, upload_date FROM resume_feedback WHERE user_id = %s ORDER BY upload_date DESC', (user_id,))
        feedbacks = cursor.fetchall()
        cursor.close()
        connection.close()

        feedback_list = [{'feedback': row[0], 'upload_date': row[1].strftime('%Y-%m-%d %H:%M:%S')} for row in feedbacks]
        return feedback_list
    except Exception as e:
        print(f"Error retrieving feedback history: {e}")
        return []

@app.route('/api/feedback-history')
def get_feedback_history_data():
    if not session.get('logged_in'):
        return jsonify({'error': 'You must be logged in first to access feedback history.'}), 403

    user_id = session.get('user_id')
    feedbacks = get_feedback_history(user_id)
    return jsonify({'feedbacks': feedbacks})

@app.route('/jobs')
def jobs():
    if not session.get('logged_in'):
        return redirect('/')  # Redirect to homepage if not logged in
    return render_template('jobs.html') 

# Job search route
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
    create_jobs_table()  # Create jobs table if it doesn't exist

    app.run(debug=True)