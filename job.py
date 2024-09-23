from flask import Flask, request, render_template, redirect, url_for
import psycopg2
import bcrypt

app=Flask(__name__)

def get_db_connection();
    conn = psycopg2.connect(
        host="localhost",
        database="Dev",
        user="postgres",
        password="FalconCamaro28"
    )
    return conn

def signup_user(email_or_phone, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("""
    INSERT INTO users (email_or_phone, password)
    VALUES (%s, %s)
    """,(email_or_phone, hashed_password))

    conn.commit()
    cursor.close()
    conn.close()

def verify_login(email_or_phone, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE email_or_phone = %s", (email_or_phone,))
    user_password = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user_password and bcrypt.checkpw(password.encode('utf-8'), user_password[0].encode('utf-8')):
        return True
    else:
        return False

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'signup' in request.form:
            # Handle signup
            email_or_phone = request.form['email_or_phone']
            password = request.form['password']
            signup_user(email_or_phone, password)
            flash("Sign up successful! Please log in.")
            return redirect(url_for('auth'))

        elif 'login' in request.form:
            # Handle login
            email_or_phone = request.form['email_or_phone']
            password = request.form['password']
            
            if verify_login(email_or_phone, password):
                flash("Login successful!")
                return redirect(url_for('filter_jobs'))  # Redirect to job page
            else:
                flash("Login failed. Check your credentials.")
                return redirect(url_for('auth'))

    return render_template('login.html')  # Renders the combined login/signup form

@app.route('/')
def index():
    return render_template('login.html')


#sample jobs(will be replaced when database is made)
jobs = [
    {"title": "Software Engineer", "location": "Remote", "salary": 120000, "experience": "mid"},
    {"title": "Data Scientist", "location": "Remote", "salary": 110000, "experience": "entry"},
    {"title": "Web Developer", "location": "North Carolina", "salary": 90000, "experience": "entry"},
    {"title": "Senior Software Enigeer", "location": "North Carolina", "salary": 150000, "experience": "senior"}
]

@app.route('/filter_jobs', methods=['GET'])
def filter_jobs():
    location = request.args.get('location')
    job_title = request.args.get('job_title')
    salary_min = request.args.get('salary_min')
    experience_level = request.args.get('experience_level')

#converting salary_min in an int
    if salary_min:
        salary_min = int(salary_min)

#filtering jobs based on options provided
    filter_jobs = []
    for job in jobs:
        if location and location.lower() not in job['location'].lower():
            continue
        if job_title and job_title.lower() not in job['title'].lower():
            continue
        if experience_level and experience_level != job['experience']:
            continue
        filter_jobs.append(job)
#rending the HTML file with filtered jobs

    return render_template('job_results.html', jobs=filter_jobs)

    if__name__ == "_main_":
        app.run(debug=True)


