from flask import Flask, Blueprint, request, render_template, redirect, url_for, flash
import psycopg2
from psycopg2.extras import execute_values
import bcrypt
import os 

def signup_user(email, password):
    conn = psycopg2.connect(database = "490DBMS",
    user="postgres", password="FalconCamaro28", host ="localhost", port="5432")
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db_password = hashed_password.decode("utf-8")

    cursor.execute("""
    INSERT INTO users (email, password)
    VALUES (%s, %s)
    """, (email, db_password))

    conn.commit()
    cursor.close()
    conn.close()

def verify_login(email, password):
    conn = psycopg2.connect(database = "490DBMS",
    user="postgres", password="FalconCamaro28", host ="localhost", port="5432")
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    user_password = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user_password and bcrypt.checkpw(password.encode('utf-8'), user_password[0].encode('utf-8')):
        return True
    else:
        return False



job_page = Blueprint('job_page', __name__, template_folder='templates')
@job_page.route('/jobs', methods=["GET", "POST"])
def jobs():
    conn = psycopg2.connect(database = "490DBMS",
    user="postgres", password="FalconCamaro28", host ="localhost", port="5432")

    cur = conn.cursor()
    
    if request.method == 'POST':
        title = "%" + request.form['title'] + "%"
        location = "%" + request.form['location'] + "%"
        salary = request.form['salary'] or 0
        experience_level = request.form['experience_level'] or None
        if experience_level == None:
            data = cur.execute("SELECT * FROM jobs WHERE LOWER(title) LIKE LOWER(%s) AND LOWER(location) LIKE LOWER(%s) AND salary >= %s", (title, location, salary,))
        else:
            data = cur.execute("SELECT * FROM jobs WHERE LOWER(title) LIKE LOWER(%s) AND LOWER(location) LIKE LOWER(%s) AND salary >= %s AND experience_level = %s", (title, location, salary, experience_level,))
    else:
        data = cur.execute("SELECT * FROM jobs")
    results = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('jobs.html', results=results)

# @app.route('/')
# def index():
#     conn = psycopg2.connect(database = "490DBMS",
#     user="postgres", password="FalconCamaro28", host ="localhost", port="5432")

#     cur = conn.cursor()

#     cur.close()
#     conn.close()

#     return render_template('index.html')

@job_page.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'signup' in request.form:
            # Handle signup
            email = request.form['email']
            password = request.form['password']
            signup_user(email, password)
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
    {"title": "Software Engineer", "location": "Remote", "salary": 120000, "experience_level": "mid"},
    {"title": "Data Scientist", "location": "Remote", "salary": 110000, "experience_level": "entry"},
    {"title": "Web Developer", "location": "North Carolina", "salary": 90000, "experience_level": "entry"},
    {"title": "Senior Software Engineer", "location": "North Carolina", "salary": 150000, "experience_level": "senior"}
]

@job_page.route('/add_jobs', methods=['GET'])
def add_jobs():
    conn = psycopg2.connect(database = "490DBMS",
    user="postgres", password="FalconCamaro28", host ="localhost", port="5432")
    
    cursor = conn.cursor()

    cursor.execute("DELETE FROM jobs")

    columns = jobs[0].keys()
    query = "INSERT INTO jobs ({}) VALUES %s".format(','.join(columns))

    # convert projects values to list of lists
    values = [[value for value in job.values()] for job in jobs]

    execute_values(cursor, query, values)
    conn.commit()
    conn.close()
    

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




