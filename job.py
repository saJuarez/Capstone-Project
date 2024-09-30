from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import bcrypt
import os 


app = Flask(__name__)
app.secret_key = 'your_secret_key'


def signup_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("""
    INSERT INTO users (email, password)
    VALUES (%s, %s)
    """, (email, hashed_password))

    conn.commit()
    cursor.close()
    conn.close()

def verify_login(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    user_password = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user_password and bcrypt.checkpw(password.encode('utf-8'), user_password[0]):
        return True
    else:
        return False
@app.route('/')
def index():
    conn = psycopg2.connect(database = "490DBMS",
    user="postgres", password="FalconCamaro28", host ="localhost", port="5432")

    cur = conn.cursor()

    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html', data=data)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'signup' in request.form:
            # Handle signup
            email = request.form['email']
            password = request.form['password']
            signup_user(email_or_phone, password)
            flash("Sign up successful! Please log in.")
            return redirect(url_for('auth'))

        elif 'login' in request.form:
            # Handle login
            email = request.form['email']
            password = request.form['password']
            
            if verify_login(email, password):
                flash("Login successful!")
                return redirect(url_for('index'))  # Redirect to index page
            else:
                flash("Login failed. Check your credentials.")
                return redirect(url_for('auth'))

    return render_template('login.html')  # Renders the combined login/signup form





# Sample jobs (will be replaced when database is made)
jobs = [
    {"title": "Software Engineer", "location": "Remote", "salary": 120000, "experience": "mid"},
    {"title": "Data Scientist", "location": "Remote", "salary": 110000, "experience": "entry"},
    {"title": "Web Developer", "location": "North Carolina", "salary": 90000, "experience": "entry"},
    {"title": "Senior Software Engineer", "location": "North Carolina", "salary": 150000, "experience": "senior"}
]

@app.route('/filter_jobs', methods=['GET'])
def filter_jobs():
    location = request.args.get('location')
    job_title = request.args.get('job_title')
    salary_min = request.args.get('salary_min')
    experience_level = request.args.get('experience_level')

    # Convert salary_min to int if provided
    if salary_min:
        salary_min = int(salary_min)

    # Filtering jobs based on options provided
    filtered_jobs = []
    for job in jobs:
        if location and location.lower() not in job['location'].lower():
            continue
        if job_title and job_title.lower() not in job['title'].lower():
            continue
        if experience_level and experience_level != job['experience']:
            continue
        if salary_min and job['salary'] < salary_min:
            continue
        filtered_jobs.append(job)
    
    # Rendering the HTML file with filtered jobs
    return render_template('job_results.html', jobs=filtered_jobs)

if __name__ == "__main__":
    app.run(debug=True)




