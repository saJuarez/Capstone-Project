from flask import Flask, request, render_template

app=Flask(__name__)

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


