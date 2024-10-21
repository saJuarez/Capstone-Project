let feedbackData = null;

document.addEventListener('DOMContentLoaded', function () {
    /**
     * Sidebar toggle handling.
     */
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
        if (
            sideMenu &&
            sideMenu.classList.contains('open') &&
            event.target !== sideMenu &&
            !sideMenu.contains(event.target) &&
            event.target !== sidebarIcon &&
            !sidebarIcon.contains(event.target)
        ) {
            sideMenu.classList.remove('open');
        }
    });

    /**
     * Show login modal when logout button is clicked.
     */
    const logoutButton = document.getElementById('logout-button');
    const loginModal = document.getElementById('login-modal');

    if (logoutButton) {
        logoutButton.addEventListener('click', function (event) {
            event.preventDefault();
            sideMenu.classList.remove('open');
            loginModal.style.display = 'block';
        });
    }

    function closeModal(modal) {
        modal.style.display = 'none';
    }

    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);

        fetch('/login', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Login successful!') {
                    // Store the user_id in localStorage for future use
                    localStorage.setItem('user_id', data.user_id);
                    loginModal.style.display = 'none';  // Close the login modal
                    alert('Login successful!'); 
                } else {
                    alert(data.message);  // Display the error message if login failed
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during login.');
            });
    });
}


    /**
     * Show Sign Up Modal when sign Up button is clicked.
     */
    const signUpButton = document.getElementById('sign-up-button');
    const signUpModal = document.getElementById('sign-up-modal');
    if (signUpButton && signUpModal) {
        signUpButton.addEventListener('click', function (event) {
            event.preventDefault();
            loginModal.style.display = 'none';
            signUpModal.style.display = 'block';
        });
    }

    window.addEventListener('click', function (event) {
        if (loginModal && event.target === loginModal) {
            closeModal(loginModal);
        }
    });

    const signUpForm = document.getElementById('sign-up-form');
    if (signUpForm) {
        signUpForm.addEventListener('submit', function (event) {
            event.preventDefault();  // Prevent default form submission

            const formData = new FormData(this);

            fetch('/signup', {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.message === 'Signup successful!') {
                        // Close the modal or redirect the user
                        signUpModal.style.display = 'none';
                        alert('Signup successful!');  // Replace with better UI feedback
                    } else {
                        // Show error message inside the modal
                        alert(data.message);  // Replace with a modal message if desired
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred during signup.');
                });
        });
    }

    /**
     * Resume form submit handling.
     */
    const resumeForm = document.getElementById('resume-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const resultDiv = document.getElementById('analysis-result');

            resultDiv.innerHTML = `<div class="loading"></div>Analyzing resume...`;

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
                .then((response) => {
                    console.log('Upload response status:', response.status);
                    return response.json();
                })
                .then((data) => {
                    console.log('Received grading result:', data);

                    if (!data || !data.grading_result) {
                        console.error('Invalid grading result:', data);
                        resultDiv.innerHTML = `<p style="color:red;">Error in processing resume grading.</p>`;
                        return;
                    }

                    feedbackData = data;

                    resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>Grading Completed</p>`;

                    const gradeResult = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
                    document.getElementById('grade-result').innerText = gradeResult;

                    const feedbackList = document.getElementById('feedback-list');
                    feedbackList.innerHTML = '';

                    Object.keys(data.grading_result.grades).forEach((criterion) => {
                        const feedbackItem = document.createElement('li');
                        feedbackItem.innerHTML = `<strong>${criterion}:</strong> ${data.grading_result.grades[criterion].feedback}`;
                        feedbackList.appendChild(feedbackItem);
                    });

                    const gradeModal = document.getElementById('grade-modal');
                    if (gradeModal) {
                        gradeModal.style.display = 'block';
                    }

                    const downloadButton = document.getElementById('download-feedback');
                    if (downloadButton) {
                        downloadButton.addEventListener('click', function () {
                            let feedbackContent = `Grade: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)\n\nFeedback:\n`;

                            Object.keys(data.grading_result.grades).forEach((criterion) => {
                                feedbackContent += `\n${criterion}:\n${data.grading_result.grades[criterion].feedback}\n`;
                            });

                            const { jsPDF } = window.jspdf;
                            const doc = new jsPDF();
                            doc.text(feedbackContent, 10, 10);
                            doc.save('resume_feedback.pdf');
                        });
                    }
                })
                .catch((error) => {
                    console.error('Error analyzing resume:', error);
                    resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
                });
        });
    }

    /**
     * Chat Box handling.
     */
    const sendChatButton = document.getElementById('send-chat');
    if (sendChatButton) {
        sendChatButton.addEventListener('click', function () {
            const input = document.getElementById('chat-input').value;
            const chatLog = document.getElementById('chat-log');

            if (!input.trim()) return;

            chatLog.innerHTML += `<div><strong>You:</strong> ${input}</div>`;

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: input })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Chat response not okay');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    chatLog.innerHTML += `<div><strong>AI:</strong> ${data.reply}</div>`;
                    document.getElementById('chat-input').value = '';
                })
                .catch(error => {
                    console.error('Error:', error);
                    chatLog.innerHTML += `<div style="color:red;">Error sending message: ${error.message}</div>`;
                });
        });
    }
    document.addEventListener('DOMContentLoaded', function () {
        // Ensure that feedback data is available when the resume analysis completes
        let feedbackData = null;
    
        // Handle resume upload and analysis
        document.getElementById('resume-form').addEventListener('submit', function (event) {
            event.preventDefault();
    
            const formData = new FormData(this);
            const resultDiv = document.getElementById('analysis-result');
            resultDiv.innerHTML = `<div class="loading"></div>Analyzing resume...`;
    
            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (!data || !data.grading_result) {
                    resultDiv.innerHTML = `<p style="color:red;">Error in processing resume grading.</p>`;
                    return;
                }
    
                feedbackData = data;  // Store the feedback data for later use
                resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>Grading Completed</p>`;
                document.getElementById('grade-result').innerText = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
    
                // Clear previous feedback and add new feedback
                const feedbackList = document.getElementById('feedback-list');
                feedbackList.innerHTML = '';
                Object.keys(data.grading_result.grades).forEach(criterion => {
                    const feedbackItem = document.createElement('li');
                    feedbackItem.innerHTML = `<strong>${criterion}:</strong> ${data.grading_result.grades[criterion].feedback}`;
                    feedbackList.appendChild(feedbackItem);
                });
    
                // Show the modal
                const gradeModal = document.getElementById('grade-modal');
                gradeModal.style.display = 'block';
    
                // Close the modal when the user clicks on the close button
                document.querySelector('.close-modal').onclick = function () {
                    gradeModal.style.display = 'none';
                };
            })
            .catch(error => {
                console.error('Error analyzing resume:', error);
                resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
            });
        });
    
        // Handle downloading feedback as PDF
        document.getElementById('download-feedback').addEventListener('click', function () {
            if (!feedbackData) {
                console.error('No feedback data available to download.');
                return;
            }
    
            let feedbackContent = `Grade: ${feedbackData.grading_result.final_grade} (${feedbackData.grading_result.percentage}%)\n\nFeedback:\n`;
            Object.keys(feedbackData.grading_result.grades).forEach(criterion => {
                feedbackContent += `\n${criterion}:\n${feedbackData.grading_result.grades[criterion].feedback}\n`;
            });
    
            // Create a new PDF using jsPDF
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.text(feedbackContent, 10, 10);
            doc.save('resume_feedback.pdf');
        });
    });

    
    document.addEventListener('DOMContentLoaded', function () {
        const historyLink = document.getElementById('view-history-link');
        const historySection = document.getElementById('history-section');
        const historyContainer = document.getElementById('history-container');
    
        if (historyLink) {
            historyLink.addEventListener('click', function (event) {
                event.preventDefault();  // Prevent default link behavior
    
                const userId = localStorage.getItem('user_id');  // Get the logged-in user ID from localStorage
    
                if (!userId) {
                    alert('You must be logged in to view your feedback history.');
                    return;
                }
    
                // Fetch the feedback history from the server
                fetch(`/history?user_id=${userId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.history && data.history.length > 0) {
                            // Clear any existing history
                            historyContainer.innerHTML = '';
    
                            // Loop through feedback history and display it
                            data.history.forEach(item => {
                                const historyItem = document.createElement('div');
                                historyItem.innerHTML = `
                                    <div class="feedback-entry">
                                        <p><strong>Date:</strong> ${new Date(item.upload_date).toLocaleString()}</p>
                                        <p><strong>Resume Text:</strong> ${item.resume_text}</p>
                                        <p><strong>Feedback:</strong> ${item.feedback}</p>
                                    </div>
                                    <hr>
                                `;
                                historyContainer.appendChild(historyItem);
                            });
    
                            // Show the history section
                            historySection.style.display = 'block';
                        } else {
                            historyContainer.innerHTML = `<p>No feedback history found.</p>`;
                            historySection.style.display = 'block';  // Show the section even if empty
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching feedback history:', error);
                        alert('An error occurred while fetching your feedback history.');
                    });
            });
        }
    });
    
    document.addEventListener('DOMContentLoaded', function () {
        const jobSearchLink = document.getElementById('view-job-search');
        const jobSearchSection = document.getElementById('job-search-section');
        const jobResultsContainer = document.getElementById('job-results-container');
    
        if (jobSearchLink) {
            jobSearchLink.addEventListener('click', function (event) {
                event.preventDefault();
                const userId = localStorage.getItem('user_id');
    
                if (!userId) {
                    alert('You must be logged in to view job matches.');
                    return;
                }
    
                // Fetch job matches from the server
                fetch(`/job-search?user_id=${userId}`)
                    .then(response => response.json())
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
    
                            jobSearchSection.classList.remove('hidden-section');
                            jobSearchSection.classList.add('visible-section');
                        } else {
                            jobResultsContainer.innerHTML = `<p>No matching jobs found.</p>`;
                            jobSearchSection.classList.remove('hidden-section');
                            jobSearchSection.classList.add('visible-section');
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching job matches:', error);
                        alert('An error occurred while fetching job matches.');
                    });
            });
        }
    });
    
});    