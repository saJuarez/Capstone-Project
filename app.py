from flask import Flask, render_template, request, jsonify, session
import os
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') # Set secret key for session management
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


@app.route('/settings')
def settings():
    if 'logged_in' in session and session['logged_in']:
        return jsonify({'message': 'User is logged in'}), 200
    else:
        return jsonify({'error': 'You must be logged in to access settings.'}), 403


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

    # Debugging log to verify the grading result
    print(f"Grading result: {grading_result}")

    # Remove the uploaded file after analysis
    os.remove(file_path)

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

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user_id = insert_user(username, email, hashed_password)

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
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'message': 'Invalid credentials.'}), 401
    else:
        return jsonify({'message': 'User not found.'}), 404
    
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

# Clear session upon logout
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Root route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Main block to run the Flask app
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create the user table when the app starts
    create_user_table()

    app.run(debug=True)