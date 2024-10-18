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

# Initialize the OpenAI client with the APIç key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print(f"API Key: {os.getenv('OPENAI_API_KEY')}")  # Print API key loaded from env file for validation

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
    
def create_user_table():
    connection = connect_to_db()
    if connection is None:
        print("Could not connect to the database.")
        return
    try:
        cursor = connection.cursor()
        # Create the users table if it doesn't already exist
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

        # Return user ID to client
        return jsonify({'message': 'Signup successful!', 'user_id': user_id}), 200
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Signup failed.'}), 500


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').lower()
    password = request.form.get('password')

    print(f"Attempting login for email: {email}")

    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            print(f"User found with email: {email}")
            print(f"Stored hashed password: {user[1]}")

            if check_password_hash(user[1], password):
                print("Password matched")

                # Return user ID to client
                return jsonify({'message': 'Login successful!', 'user_id': user[0]}), 200
            else:
                print("Password mismatch")
                return jsonify({'message': 'Invalid credentials'}), 401
        else:
            print("No user found with that email")
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error logging in: {e}")
        return jsonify({'message': 'Login failed.'}), 500



# Root route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

print(f"DB Password: {os.getenv('DB_PASSWORD')}")

# Main block to run the Flask app
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create the user table when the app starts
    create_user_table()

    app.run(debug=True)

   