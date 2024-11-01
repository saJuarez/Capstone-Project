document.addEventListener('DOMContentLoaded', function () {
    const jobResultsContainer = document.getElementById('job-results-container');
    
    // Get user ID from local storage
    const userId = 1;

    if (!userId) {
        alert('You must be logged in to view job matches.');
        window.location.href = '/'; // Redirect to home if not logged in
        return;
    }

    const queryParams = new URLSearchParams(window.location.search);
    let job_title;
    if (queryParams.has("job_title")) {
        job_title = "&job_title=" + queryParams.get("job_title");
    } else {
        job_title = "";
    }
    let location;
    if (queryParams.has("location")) {
        location = "&location=" + queryParams.get("location");
    } else {
        location = "";
    }
    let salary_min;
    if (queryParams.has("salary_min") && queryParams.get("salary_min") != "") {
        salary_min = "&salary_min=" + queryParams.get("salary_min");
    } else {
        salary_min = "";
    }

    // Fetch job matches from the server
    fetch(`/job-search?user_id=${userId}${job_title}${location}${salary_min}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch job matches');
            }
            return response.json();
        })
        .then(data => {
            if (data.jobs && data.jobs.results.length > 0) {
                jobResultsContainer.innerHTML = '';

                data.jobs.results.forEach(job => {
                    const jobItem = document.createElement('div');
                    jobItem.innerHTML = `
                        <div class="job-entry">
                            <p><strong>Title:</strong> ${job.title}</p>
                            <p><strong>Location:</strong> ${job.location.display_name}</p>
                            <p><strong>Description:</strong> ${job.description}</p>
                            <p><a href="${job.redirect_url}" target="_blank">Apply Here</a></p>
                        </div>
                        <hr>
                    `;
                    jobResultsContainer.appendChild(jobItem);
                });
            } else {
                jobResultsContainer.innerHTML = `<p>No matching jobs found.</p>`;
            }
        })
        .catch(error => {
            console.error('Error fetching job matches:', error);
            alert('An error occurred while fetching job matches.');
        });

    // Back button functionality
    document.getElementById('back-button').addEventListener('click', function () {
        window.location.href = '/'; // Redirect back to the main dashboard
    });
});