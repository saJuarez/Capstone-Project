document.addEventListener('DOMContentLoaded', function () {
    // Sidebar functionality
    const sidebarIcon = document.getElementById('sidebar-icon');
    const sideMenu = document.getElementById('side-menu');
    const closeMenu = document.getElementById('close-menu');

    if (sidebarIcon) {
        sidebarIcon.addEventListener('click', function () {
            sideMenu.classList.toggle('open');
        });
    }

    if (closeMenu) {
        closeMenu.addEventListener('click', function () {
            sideMenu.classList.remove('open');
        });
    }

    window.addEventListener('click', function (event) {
        if (!sideMenu.contains(event.target) && !sidebarIcon.contains(event.target)) {
            sideMenu.classList.remove('open');
        }
    });

    const jobResultsContainer = document.getElementById('job-results-container');

    // Show "Finding Jobs..." message with animation
    let loadingMessage = document.createElement('p');
    loadingMessage.className = "loading-message"; 
    loadingMessage.textContent = "Finding Jobs";
    jobResultsContainer.appendChild(loadingMessage);

    let dotCount = 0;
    const loadingInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4; // Cycle between 0 to 3 dots
        loadingMessage.textContent = "Finding Jobs" + ".".repeat(dotCount);
    }, 500);

    // Fetch job matches from the server
    const userId = sessionStorage.getItem('user_id');
    if (!userId) {
        alert('You must be logged in to view job matches.');
        window.location.href = '/';
        return;
    }

    fetch(`/job-search?user_id=${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch job matches');
            }
            return response.json();
        })
        .then(data => {
            clearInterval(loadingInterval);
            jobResultsContainer.innerHTML = '';

            if (data.jobs && data.jobs.results.length > 0) {
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
            clearInterval(loadingInterval);
            jobResultsContainer.innerHTML = `<p>An error occurred while fetching job matches.</p>`;
        });
});